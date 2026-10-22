from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum

# =====================================================================
# 1. GLOBAL PLATFORM SUPERADMINS (Platform Managers)
# =====================================================================


class SuperAdmin(models.Model):
    superadmin_id = models.CharField(max_length=50, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    dob = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"SuperAdmin: {self.first_name} {self.last_name}"


# =====================================================================
# 2. RESTAURANT GROUPS (SaaS Corporate Client Companies)
# =====================================================================
class RestaurantGroup(models.Model):
    restaurant_group_id = models.CharField(max_length=50, primary_key=True)
    group_name = models.CharField(max_length=255)
    is_chain = models.BooleanField(default=False)

    def __str__(self):
        return self.group_name


# =====================================================================
# 3. FRANCHISE / BUSINESS OWNERS (Franchise Admins)
# =====================================================================
class Owner(models.Model):
    owner_id = models.CharField(max_length=50, primary_key=True)
    restaurant_group = models.ForeignKey(
        RestaurantGroup, on_delete=models.CASCADE, related_name='owners')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    dob = models.DateField(blank=True, null=True)
    is_locked_out = models.BooleanField(default=False)

    def __str__(self):
        return f"Owner: {self.first_name} {self.last_name}"


# =====================================================================
# 4. PHYSICAL RESTAURANT LOCATIONS (The Venues)
# =====================================================================
class Restaurant(models.Model):
    restaurant_name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    max_capacity_guests = models.IntegerField(default=50)
    restaurant_group = models.ForeignKey(
        RestaurantGroup, on_delete=models.SET_NULL, blank=True, null=True, related_name='restaurants')

    def __str__(self):
        return self.restaurant_name


# =====================================================================
# 5. EMPLOYEES / WORKERS (Roster Registry)
# =====================================================================
class Employee(models.Model):
    employee_id = models.CharField(max_length=50, primary_key=True)
    restaurant_group = models.ForeignKey(
        RestaurantGroup, on_delete=models.CASCADE, related_name='employees')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    dob = models.DateField(blank=True, null=True)
    base_annual_salary = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00)
    is_locked_out = models.BooleanField(default=False)

    def __str__(self):
        return f"Employee: {self.first_name} {self.last_name}"


# =====================================================================
# 6. EMPLOYEE LOCATION ROSTER ASSIGNMENTS (Shift Map)
# =====================================================================
class EmployeeRestaurant(models.Model):
    assignment_id = models.CharField(max_length=50, primary_key=True)
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='assignments')
    restaurant_name = models.CharField(max_length=255)
    restaurant_address = models.TextField()
    role = models.CharField(max_length=100)

    def clean(self):
        # Enforces your assignment rule: Local independent brands cannot share crew across branches.
        group = self.employee.restaurant_group
        if not group.is_chain:
            existing_assignments = EmployeeRestaurant.objects.filter(
                employee=self.employee).exclude(assignment_id=self.assignment_id).exists()
            if existing_assignments:
                raise ValidationError(
                    "Single-Venue Brand Boundary Violation: Employees working for independent brands cannot register across multiple branches.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# =====================================================================
# 7. CUSTOMER CRM PROFILES (Internal Usage Tracking)
# =====================================================================
class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    anniversary_date = models.DateField(blank=True, null=True)
    important_occasion_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# =====================================================================
# 8. GUEST HEALTH & ALLERGY REGISTRY (Safety Ledger)
# =====================================================================
class Allergy(models.Model):
    allergy_id = models.CharField(max_length=50, primary_key=True)
    customer_first_name = models.CharField(max_length=100)
    customer_last_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    allergy_name = models.CharField(max_length=100)
    severity_level = models.CharField(max_length=50)
    staff_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.allergy_name} ({self.severity_level})"


# =====================================================================
# 9. SCHEDULING & BOOKINGS MATRIX (Reservation Engine)
# =====================================================================
class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No-Show'),
    ]

    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='bookings')
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    booking_time = models.TimeField()
    guest_count = models.PositiveIntegerField()
    occasion = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    customer_notes = models.TextField(blank=True, null=True)

    def clean(self):
        # A. Safeguard: Block overlapping bookings for the exact same customer profile.
        duplicate_exists = Booking.objects.filter(
            customer=self.customer,
            booking_date=self.booking_date,
            booking_time=self.booking_time
        ).exclude(id=self.id).exists()

        if duplicate_exists:
            raise ValidationError(
                "Double-Booking Violation: This client profile already holds an active reservation layout at this concurrent spot.")

        # B. Safeguard: Block bookings that push the specific branch past its seating capacity threshold.
        existing_guests = Booking.objects.filter(
            restaurant=self.restaurant,
            booking_date=self.booking_date,
            booking_time=self.booking_time
        ).exclude(id=self.id).aggregate(total=Sum('guest_count'))['total'] or 0

        if existing_guests + self.guest_count > self.restaurant.max_capacity_guests:
            raise ValidationError(
                "Capacity Overload: This layout size pushes the active venue far beyond its remaining seating capacity limits.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.id} - {self.customer} at {self.restaurant.restaurant_name}"
