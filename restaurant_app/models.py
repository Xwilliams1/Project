from datetime import datetime, time, timedelta

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone

# =====================================================================
# 1. GLOBAL PLATFORM SUPERADMINS (Platform Managers)
# =====================================================================

class SuperAdmin(models.Model):
    """
    Platform-level administrators who manage restaurant accounts,
    locations, users, and system settings. (UNCHANGED)
    """
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
# 2. RESTAURANT GROUPS (Business Entities)
# =====================================================================

class RestaurantGroup(models.Model):
    """
    A business that owns one or more restaurant locations. (UNCHANGED)
    is_chain controls whether staff may work at multiple locations.
    """
    restaurant_group_id = models.CharField(max_length=50, primary_key=True)
    group_name = models.CharField(max_length=255)
    is_chain = models.BooleanField(default=False)

    def __str__(self):
        return self.group_name


# =====================================================================
# 3. OWNERS (Restaurant Owners)
# =====================================================================

class Owner(models.Model):
    """
    Business owners. Their access is limited to their own RestaurantGroup. (UNCHANGED)
    """
    owner_id = models.CharField(max_length=50, primary_key=True)
    restaurant_group = models.ForeignKey(
        RestaurantGroup, on_delete=models.CASCADE, related_name='owners')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    dob = models.DateField(blank=True, null=True)
    is_locked_out = models.BooleanField(default=False)  # Instantly freezes access

    def __str__(self):
        return f"Owner: {self.first_name} {self.last_name}"


# =====================================================================
# 4. RESTAURANTS (Physical Locations)
# =====================================================================

class Restaurant(models.Model):
    """
    A physical restaurant location.
    CHANGED: added opening_time and closing_time (proposal deliverable 5:
    separate hours per location). Booking.clean() uses these to reject
    bookings outside opening hours.
    """
    restaurant_name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    max_capacity_guests = models.IntegerField(default=50)

    # NEW: daily opening hours. Defaults let existing rows migrate cleanly;
    # edit each location's real hours in the admin site afterwards.
    opening_time = models.TimeField(default=time(11, 0))
    closing_time = models.TimeField(default=time(22, 0))

    restaurant_group = models.ForeignKey(
        RestaurantGroup, on_delete=models.SET_NULL,
        blank=True, null=True, related_name='restaurants')

    def __str__(self):
        return self.restaurant_name


# =====================================================================
# 5. EMPLOYEES (Staff Registry)
# =====================================================================

class Employee(models.Model):
    """
    Restaurant staff members. (UNCHANGED)
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
    base_annual_salary = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00)
    is_locked_out = models.BooleanField(default=False)

    def __str__(self):
        return f"Employee: {self.first_name} {self.last_name}"


# =====================================================================
# 6. EMPLOYEE LOCATION ASSIGNMENTS
# =====================================================================

class EmployeeRestaurant(models.Model):
    """
    Links an employee to a restaurant location and role.
    CHANGED: restaurant_name / restaurant_address text fields were replaced
    by a real ForeignKey to Restaurant, so staff access per location can
    be enforced reliably (e.g. "show only bookings for my restaurant").
    """
    assignment_id = models.CharField(max_length=50, primary_key=True)
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='assignments')

    # NEW: real link to the location. null=True only so the migration works
    # on rows that already exist. After reseeding, you can remove null=True.
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='assignments',
        null=True, blank=True)

    role = models.CharField(max_length=100)  # e.g. 'Host', 'Manager'

    def clean(self):
        """
        Business rules checked before saving:
        1. The restaurant must belong to the same group as the employee.
        2. Staff of independent (non-chain) brands can't work at multiple locations.
        """
        group = self.employee.restaurant_group

        # NEW rule 1: block cross-business assignments
        if self.restaurant and self.restaurant.restaurant_group_id != group.pk:
            raise ValidationError(
                "This restaurant does not belong to the employee's business.")

        # Existing rule 2 (unchanged)
        if not group.is_chain:
            other_assignments = EmployeeRestaurant.objects.filter(
                employee=self.employee).exclude(assignment_id=self.assignment_id).exists()
            if other_assignments:
                raise ValidationError(
                    "Employees of independent brands cannot be assigned to multiple locations.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Forces clean() to run on every save
        super().save(*args, **kwargs)


# =====================================================================
# 7. CUSTOMERS (CRM Profiles)
# =====================================================================

class Customer(models.Model):
    """
    Guest profile used for bookings and CRM.
    CHANGED: added marketing_consent (proposal deliverable 3).
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    anniversary_date = models.DateField(blank=True, null=True)
    important_occasion_notes = models.TextField(blank=True, null=True)

    # NEW: whether the guest agreed to receive marketing. Defaults to False
    # (opt-in only), which is the safe default.
    marketing_consent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# =====================================================================
# 8. ALLERGIES (Guest Safety Records)
# =====================================================================

class Allergy(models.Model):
    """
    A customer's allergy record.
    CHANGED: customer name/phone text fields were replaced with a
    ForeignKey to Customer, matching your ER diagram. Allergies now
    follow the customer and can be shown on their CRM profile.
    """
    allergy_id = models.CharField(max_length=50, primary_key=True)

    # NEW: real link to the customer. null=True only so the migration works
    # on existing rows. Remove it after reseeding.
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='allergies',
        null=True, blank=True)

    allergy_name = models.CharField(max_length=100)    # e.g. 'Peanuts'
    severity_level = models.CharField(max_length=50)   # e.g. 'Anaphylactic'
    staff_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.allergy_name} ({self.severity_level})"


# =====================================================================
# 9. BOOKINGS (Reservation Engine)
# =====================================================================

class Booking(models.Model):
    """
    A reservation.
    CHANGED:
      - staff_notes added (internal notes, separate from the guest's request)
      - guest_count must be at least 1
      - clean() rewritten: cancelled/no-show bookings no longer cause
        conflicts, opening hours are enforced, capacity is checked per
        seating window instead of per day, and past bookings are blocked.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No-Show'),
    ]

    # Statuses that no longer hold a table. Used by the checks below.
    INACTIVE_STATUSES = ['CANCELLED', 'NO_SHOW']

    # How long a party is assumed to occupy seats. Bookings within this
    # many hours of each other share capacity. Change as needed.
    SEATING_WINDOW_HOURS = 2

    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='bookings')
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    booking_time = models.TimeField()

    # CHANGED: MinValueValidator(1) actually blocks 0 guests
    # (PositiveIntegerField alone allows 0).
    guest_count = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    occasion = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    customer_notes = models.TextField(blank=True, null=True)  # Guest's special requests

    # NEW: internal notes written by staff (deliverable 2)
    staff_notes = models.TextField(blank=True, null=True)

    def clean(self):
        """Validation run before every save (reservation conflict control)."""

        # Cancelled / no-show bookings hold no table, so skip all checks.
        # This lets staff cancel a booking even if the restaurant is now full.
        if self.status in self.INACTIVE_STATUSES:
            return

        # Related objects may not be set yet when a form is partly filled in.
        # Required-field errors are reported separately, so just stop here.
        if not (self.restaurant_id and self.customer_id and self.booking_date
                and self.booking_time and self.guest_count):
            return

        # --- Check A: no bookings in the past (new bookings only) --------
        # Only applies on creation, so staff can still edit or complete
        # older bookings.
        if self._state.adding:
            now = timezone.localtime()
            if self.booking_date < now.date() or (
                    self.booking_date == now.date() and self.booking_time < now.time()):
                raise ValidationError("Bookings cannot be made in the past.")

        # --- Check B: restaurant must be open ----------------------------
        if not (self.restaurant.opening_time <= self.booking_time <= self.restaurant.closing_time):
            raise ValidationError(
                f"{self.restaurant} is open from "
                f"{self.restaurant.opening_time:%H:%M} to {self.restaurant.closing_time:%H:%M}.")

        # --- Check C: same customer can't double-book the same slot ------
        # CHANGED: ignores cancelled/no-show bookings, so a guest who
        # cancelled can rebook the same time.
        duplicate_exists = Booking.objects.filter(
            customer=self.customer,
            booking_date=self.booking_date,
            booking_time=self.booking_time,
        ).exclude(id=self.id).exclude(status__in=self.INACTIVE_STATUSES).exists()

        if duplicate_exists:
            raise ValidationError(
                "This customer already has a booking at this date and time.")

        # --- Check D: capacity within the seating window -----------------
        # CHANGED: previously summed the whole day. Now only counts
        # bookings whose time is within SEATING_WINDOW_HOURS of this one,
        # so a busy lunch doesn't block dinner.
        window = timedelta(hours=self.SEATING_WINDOW_HOURS)
        this_start = datetime.combine(self.booking_date, self.booking_time)

        same_day = Booking.objects.filter(
            restaurant=self.restaurant,
            booking_date=self.booking_date,
        ).exclude(id=self.id).exclude(status__in=self.INACTIVE_STATUSES)

        guests_in_window = sum(
            b.guest_count for b in same_day
            if abs(datetime.combine(b.booking_date, b.booking_time) - this_start) < window
        )

        capacity = self.restaurant.max_capacity_guests
        if guests_in_window + self.guest_count > capacity:
            remaining = max(capacity - guests_in_window, 0)
            raise ValidationError(
                f"Not enough capacity at this time. Only {remaining} seats remaining "
                f"for a party of {self.guest_count}.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Runs clean() on every save, including from code/seed scripts
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer} at {self.restaurant} on {self.booking_date} {self.booking_time}"