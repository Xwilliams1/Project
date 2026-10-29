from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum

# =====================================================================
# 1. GLOBAL PLATFORM SUPERADMINS (Platform Managers)
# =====================================================================

class SuperAdmin(models.Model):
    """
    Represents overarching system administrators.
    These users possess multi-tenant operational visibility and system configuration privileges.
    """
    # Unique text identifier acting as the explicit primary key
    superadmin_id = models.CharField(max_length=50, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True) # Optional descriptive location notes
    phone = models.CharField(max_length=20, blank=True, null=True) # Optional contact numeric string
    email = models.EmailField(unique=True) # Unique platform communication handle
    dob = models.DateField(blank=True, null=True) # Optional date of birth for identity tracking

    def __str__(self):
        """Returns standard visual label for logs and admin drop-down forms."""
        return f"SuperAdmin: {self.first_name} {self.last_name}"


# =====================================================================
# 2. RESTAURANT GROUPS (SaaS Corporate Client Companies)
# =====================================================================

class RestaurantGroup(models.Model):
    """
    Represents corporate parent companies, enterprise franchises, or business entities.
    Acts as the multi-tenant isolation layer separating completely different organizations.
    """
    # Explicit business group alpha-numeric key string
    restaurant_group_id = models.CharField(max_length=50, primary_key=True)
    group_name = models.CharField(max_length=255) # Name of corporate umbrella or parent franchise
    is_chain = models.BooleanField(default=False) # Controls shared resource routing across venues

    def __str__(self):
        return self.group_name


# =====================================================================
# 3. FRANCHISE / BUSINESS OWNERS (Franchise Admins)
# =====================================================================

class Owner(models.Model):
    """
    Represents corporate business owners or franchise executives.
    They retain operational management rights bounded within their specific RestaurantGroup.
    """
    owner_id = models.CharField(max_length=50, primary_key=True)
    # Cascade Delete: If a corporate company parent is removed, purge all associated executive rows
    restaurant_group = models.ForeignKey(
        RestaurantGroup, on_delete=models.CASCADE, related_name='owners')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    dob = models.DateField(blank=True, null=True)
    is_locked_out = models.BooleanField(default=False) # Security flag to instantly freeze user profile access

    def __str__(self):
        return f"Owner: {self.first_name} {self.last_name}"


# =====================================================================
# 4. PHYSICAL RESTAURANT LOCATIONS (The Venues)
# =====================================================================

class Restaurant(models.Model):
    """
    Represents physical brick-and-mortar storefronts or kitchen venues.
    Houses seating limits and references the overarching corporate entity.
    """
    restaurant_name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    max_capacity_guests = models.IntegerField(default=50) # Fire code safety or seating grid limits
    # Nullable Foreign Key: If corporate hierarchy changes or dissolves, preserve historical location records
    restaurant_group = models.ForeignKey(
        RestaurantGroup, on_delete=models.SET_NULL, blank=True, null=True, related_name='restaurants')

    def __str__(self):
        return self.restaurant_name


# =====================================================================
# 5. EMPLOYEES / WORKERS (Roster Registry)
# =====================================================================

class Employee(models.Model):
    """
    Represents internal human resources (chefs, waitstaff, hosts, managers).
    Tracks payroll metrics and corporate system locks.
    """
    employee_id = models.CharField(max_length=50, primary_key=True)
    restaurant_group = models.ForeignKey(
        RestaurantGroup, on_delete=models.CASCADE, related_name='employees')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    dob = models.DateField(blank=True, null=True)
    # Decimal field prevents rounding errors common with standard float numbers in currency systems
    base_annual_salary = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00)
    is_locked_out = models.BooleanField(default=False) # Freezes staff portal authentication rights

    def __str__(self):
        return f"Employee: {self.first_name} {self.last_name}"

    
# =====================================================================
# 6. EMPLOYEE LOCATION ROSTER ASSIGNMENTS (Shift Map)
# =====================================================================

class EmployeeRestaurant(models.Model):
    """
    Maps specific employees to active storefront branches and functional roles.
    Houses business logic enforcing staff boundaries for independent operations.
    """
    assignment_id = models.CharField(max_length=50, primary_key=True)
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='assignments')
    restaurant_name = models.CharField(max_length=255)
    restaurant_address = models.TextField()
    role = models.CharField(max_length=100) # e.g., 'Sous Chef', 'Head Bartender', 'General Manager'

    def clean(self):
        """
        Enforces operational safety constraints prior to database insertion.
        Rule: Independent brands (non-chains) cannot share staff across multiple locations.
        """
        group = self.employee.restaurant_group
        if not group.is_chain:
            # Check if this employee already holds an assignment outside of this entry's primary key
            existing_assignments = EmployeeRestaurant.objects.filter(
                employee=self.employee).exclude(assignment_id=self.assignment_id).exists()
            if existing_assignments:
                raise ValidationError(
                    "Single-Venue Brand Boundary Violation: Employees working for independent brands cannot register across multiple branches.")

    def save(self, *args, **kwargs):
        """Overrides built-in save behavior to force validation checks on programmatic entries."""
        self.full_clean() # Triggers the 'clean()' method automatically before saving
        super().save(*args, **kwargs)


# =====================================================================
# 7. CUSTOMER CRM PROFILES (Internal Usage Tracking)
# =====================================================================

class Customer(models.Model):
    """
    Represents customer profile records used by marketing and guest relations.
    Stores personal dates to facilitate automated loyalty milestones or promos.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    anniversary_date = models.DateField(blank=True, null=True)
    important_occasion_notes = models.TextField(blank=True, null=True) # Tracks specific notes like "Prefers outdoor seating"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# =====================================================================
# 8. GUEST HEALTH & ALLERGY REGISTRY (Safety Ledger)
# =====================================================================

class Allergy(models.Model):
    """
    Critical dining health safety ledger.
    Keeps customer names and ingredient severities unlinked from standard login sessions
    to streamline point-of-sale terminal lookup operations for waitstaff.
    """
    allergy_id = models.CharField(max_length=50, primary_key=True)
    customer_first_name = models.CharField(max_length=100)
    customer_last_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    allergy_name = models.CharField(max_length=100) # e.g., 'Peanuts', 'Shellfish', 'Gluten'
    severity_level = models.CharField(max_length=50) # e.g., 'Mild Irritation', 'Anaphylactic Danger'
    staff_notes = models.TextField(blank=True, null=True) # e.g., 'Requires kitchen sanitizer override'

    def __str__(self):
        return f"{self.allergy_name} ({self.severity_level})"


# =====================================================================
# 9. SCHEDULING & BOOKINGS MATRIX (Reservation Engine)
# =====================================================================

class Booking(models.Model):
    """
    Core transactional booking engine.
    Manages seat availability, prevents double-booking overlaps,
    and runs aggregation calculations to prevent physical overcapacity issues.
    """
    # State mapping tuples formatting data values safely for database rows vs human-readable text
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
    guest_count = models.PositiveIntegerField() # Forces numeric integers greater than 0
    occasion = models.CharField(max_length=100, blank=True, null=True) # e.g., 'Birthday Anniversary'
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    customer_notes = models.TextField(blank=True, null=True)

    def clean(self):
        """Runs complex data validation rules prior to scheduling reservation slots."""
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
        # Sums all guest counts registered for active seating allocations at this venue on this date
        current_guests_total = Booking.objects.filter(
            restaurant=self.restaurant,
            booking_date=self.booking_date
        ).exclude(id=self.id).exclude(status__in=['CANCELLED', 'NO_SHOW']).aggregate(
            total_seated=Sum('guest_count')
        )['total_seated'] or 0

        # Check if the incoming guest addition pushes the venue past fire-code limits
        if current_guests_total + self.guest_count > self.restaurant.max_capacity_guests:
            raise ValidationError(
                f"Overcapacity Warning: Adding this reservation of {self.guest_count} guests exceeds "
                f"the remaining capacity of this venue on this date ({self.restaurant.max_capacity_guests - current_guests_total} seats remaining)."
            )

    def save(self, *args, **kwargs):
        """Ensures programmatic and dashboard additions pass all capacity tests prior to execution."""
        self.full_clean()
        super().save(*args, **kwargs)
