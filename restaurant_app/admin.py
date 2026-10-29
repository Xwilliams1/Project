from django.contrib import admin

from .models import (
    SuperAdmin, RestaurantGroup, Owner, Restaurant, Employee,
    EmployeeRestaurant, Customer, Allergy, Booking,
)

# Each class below controls how one model appears in the admin site.
# Rules used throughout:
#  - models with a custom primary key (owner_id, employee_id, ...) have NO 'id' field
#  - search_fields must point at text fields; for a ForeignKey, use
#    'fk_name__field' (e.g. 'restaurant_group__group_name')


@admin.register(SuperAdmin)
class SuperAdminAdmin(admin.ModelAdmin):
    list_display = ('superadmin_id', 'first_name', 'last_name', 'email')
    search_fields = ('superadmin_id', 'first_name', 'last_name', 'email')


@admin.register(RestaurantGroup)
class RestaurantGroupAdmin(admin.ModelAdmin):
    list_display = ('restaurant_group_id', 'group_name', 'is_chain')
    list_filter = ('is_chain',)
    search_fields = ('restaurant_group_id', 'group_name')


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('owner_id', 'first_name', 'last_name', 'restaurant_group', 'is_locked_out')
    list_filter = ('restaurant_group', 'is_locked_out')
    search_fields = ('owner_id', 'first_name', 'last_name', 'restaurant_group__group_name')


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    # Opening hours and capacity are the per-location settings (deliverable 5)
    list_display = ('id', 'restaurant_name', 'restaurant_group',
                    'max_capacity_guests', 'opening_time', 'closing_time')
    list_filter = ('restaurant_group',)
    search_fields = ('restaurant_name', 'restaurant_group__group_name')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'restaurant_group', 'is_locked_out')
    list_filter = ('restaurant_group', 'is_locked_out')
    search_fields = ('employee_id', 'first_name', 'last_name', 'restaurant_group__group_name')


@admin.register(EmployeeRestaurant)
class EmployeeRestaurantAdmin(admin.ModelAdmin):
    # 'restaurant' replaces the old restaurant_name / restaurant_address text fields
    list_display = ('assignment_id', 'employee', 'restaurant', 'role')
    list_filter = ('restaurant', 'role')
    search_fields = ('assignment_id', 'employee__first_name', 'employee__last_name')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    # marketing_consent added for the CRM requirement (deliverable 3)
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone', 'marketing_consent')
    list_filter = ('marketing_consent',)
    search_fields = ('first_name', 'last_name', 'email', 'phone')


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    # FIX: was ('id', ...). Allergy's primary key is allergy_id, so 'id' doesn't exist.
    list_display = ('allergy_id', 'customer', 'allergy_name', 'severity_level')
    list_filter = ('severity_level',)
    search_fields = ('allergy_name', 'customer__first_name', 'customer__last_name')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # Booking keeps the default 'id' primary key, so 'id' is valid here
    list_display = ('id', 'customer', 'restaurant', 'booking_date',
                    'booking_time', 'guest_count', 'status')
    list_filter = ('status', 'restaurant', 'booking_date')
    search_fields = ('customer__last_name', 'customer__email', 'restaurant__restaurant_name')