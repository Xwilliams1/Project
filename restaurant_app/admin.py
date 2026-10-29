from django.contrib import admin
from .models import SuperAdmin, Owner, Employee, Customer, Restaurant, Booking, Allergy


# CUSTOM ADMIN CONFIGURATIONS (CONTROL SEARCH & DISPLAY LAYOUTS)
# =====================================================================

@admin.register(SuperAdmin)
class SuperAdminAdmin(admin.ModelAdmin):
    """Exposes SuperAdmin management profiles inside the admin interface."""
    list_display = ('superadmin_id',)
    search_fields = ('superadmin_id',)


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    """Exposes Owner profiles and filters them by corporate groups."""
    list_display = ('owner_id', 'restaurant_group')
    list_filter = ('restaurant_group',)
    search_fields = ('owner_id', 'restaurant_group')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Manages staff members and identifies their corporate alignment."""
    list_display = ('employee_id', 'restaurant_group')
    list_filter = ('restaurant_group',)
    search_fields = ('employee_id', 'restaurant_group')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Provides a searchable ledger of registered restaurant customers."""
    list_display = ('id', 'first_name', 'last_name', 'phone')
    search_fields = ('first_name', 'last_name', 'phone')


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    """Controls physical location profiles and baseline venue data."""
    list_display = ('id', 'restaurant_name', 'restaurant_group')
    list_filter = ('restaurant_group',)
    search_fields = ('restaurant_name', 'restaurant_group')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Manages live reservation books.
    
    Includes sorting filters so admins can instantly sort through books
    by booking status or target restaurant venue.
    """
    list_display = ('id', 'customer', 'restaurant', 'status')
    list_filter = ('status', 'restaurant')
    search_fields = ('customer__last_name', 'restaurant__restaurant_name')


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    """Tracks safety profiles and ingredient alerts for guests."""
    list_display = ('id', 'allergy_name')
    search_fields = ('allergy_name',)
