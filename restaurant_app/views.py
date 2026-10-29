from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework import serializers
from django.db.models import Count, Q
from .models import SuperAdmin, Owner, Employee, Customer, Restaurant, Booking, Allergy
from .permissions import CustomerProfileAccess, EmployeeManagementAccess, IsSystemOwnerOrAdmin, get_actor_role


# CUSTOM GATEWAY SECURITY PERMISSIONS
# =====================================================================

class IsSystemSuperAdmin(BasePermission):
    """
    Strict system-level gateway.
    
    How it works:
    - Calls the 'get_actor_role' utility to scan request headers for a valid Admin UUID.
    - Returns True ONLY if the authenticated user has a role string matching 'SuperAdmin'.
    - Completely blocks Owners, Employees, Customers, and Public Guests.
    """
    def has_permission(self, request, view):
        role, entity = get_actor_role(request)
        return role == 'SuperAdmin'

# =====================================================================
# DJANGO REST FRAMEWORK SECURE BACKEND DATA API ENDPOINTS
# =====================================================================

class CustomerViewSet(viewsets.ModelViewSet):
    """
    Secure CRUD interface to manage Customer profiles.
    
    Security Architecture:
    - Enforces 'CustomerProfileAccess' rules.
    - SuperAdmins retain full global control.
    - Restaurant Owners and Staff are restricted to read-only views.
    - Customers can only view or modify records matching their exact profile headers.
    """
    queryset = Customer.objects.all()
    permission_classes = [CustomerProfileAccess]

    def get_serializer_class(self):
        # Inline serialization captures all table columns dynamically for translation to JSON
        class CustomerSerializer(serializers.ModelSerializer):
            class Meta:
                model = Customer
                fields = '__all__'
        return CustomerSerializer

class OwnerStaffManagementViewSet(viewsets.ModelViewSet):
    """
    Secure HR endpoint to process and manage Employee files.
    
    Security Architecture:
    - Enforces 'EmployeeManagementAccess' rules.
    - SuperAdmins can manage any employee record globally.
    - Restaurant Owners can manage staff ONLY within their own restaurant group.
    - Regular employees and public users are strictly blocked from this entire endpoint.
    """
    queryset = Employee.objects.all()
    permission_classes = [EmployeeManagementAccess]

    def get_serializer_class(self):
        class EmployeeSerializer(serializers.ModelSerializer):
            class Meta:
                model = Employee
                fields = '__all__'
        return EmployeeSerializer

class SuperAdminOverrideViewSet(viewsets.ModelViewSet):
    """
    Master platform administration panel.
    
    Security Architecture:
    - CRITICAL FIX: Changed from 'AllowAny' to 'IsSystemSuperAdmin'.
    - Only the overarching platform SuperAdmins can access this data.
    - Prevents malicious actors from escalating privileges or altering administrative cores.
    """
    queryset = SuperAdmin.objects.all()
    permission_classes = [IsSystemSuperAdmin]

    def get_serializer_class(self):
        class SuperAdminSerializer(serializers.ModelSerializer):
            class Meta:
                model = SuperAdmin
                fields = '__all__'
        return SuperAdminSerializer

class RestaurantViewSet(viewsets.ModelViewSet):
    """
    Physical restaurant profiles and seating capacities router.
    
    Security Architecture:
    - Dynamically evaluates permissions based on the incoming HTTP verb (Action).
    - Public Guests can execute 'list' (GET) and 'retrieve' (GET) to view open locations.
    - Administrative operations (POST, PUT, PATCH, DELETE) require 'IsSystemOwnerOrAdmin'.
    """
    queryset = Restaurant.objects.all()
    
    def get_permissions(self):
        # Public-facing read actions are open; state changes are locked to leadership
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsSystemOwnerOrAdmin()]

    def get_serializer_class(self):
        class RestaurantSerializer(serializers.ModelSerializer):
            class Meta:
                model = Restaurant
                fields = '__all__'
        return RestaurantSerializer

class BookingViewSet(viewsets.ModelViewSet):
    """
    Reservation ledger interface.
    
    Security Architecture:
    - Anyone ('AllowAny') can initiate a 'create' (POST) action to book a table.
    - Reading the reservation books or modifying a reservation requires 'CustomerProfileAccess'.
    - This ensures staff can monitor tables, while customers can only manipulate their own bookings.
    """
    queryset = Booking.objects.all()
    
    def get_permissions(self):
        # Open reservation creation to the public, protect management operations
        if self.action == 'create':
            return [AllowAny()]
        return [CustomerProfileAccess()]

    def get_serializer_class(self):
        class BookingSerializer(serializers.ModelSerializer):
            class Meta:
                model = Booking
                fields = '__all__'
        return BookingSerializer

# =====================================================================
# DJANGO REST FRAMEWORK OWNER ANALYTICS DASHBOARD ENGINE
# =====================================================================

class OwnerAnalyticsDashboardAPI(APIView):
    """
    Headless analytical aggregation engine.
    
    Security Architecture:
    - Enforces 'IsSystemOwnerOrAdmin' strictly.
    - Blocked for regular employees and customers to prevent exposure of corporate financial metrics.
    
    How it works:
    - Bypasses raw SQL queries by utilizing Django's ORM database aggregation.
    - Computes metrics on-the-fly directly inside the database layer for rapid performance.
    """
    permission_classes = [IsSystemOwnerOrAdmin]

    def get(self, request, *args, **kwargs):
        # 1. Transactional Volumes: Aggregates totals across reservation statuses via conditional counting
        booking_metrics = Booking.objects.aggregate(
            total_reservations=Count('id'),
            completed_count=Count('id', filter=Q(status='COMPLETED')),
            cancelled_count=Count('id', filter=Q(status='CANCELLED')),
            no_show_count=Count('id', filter=Q(status='NO_SHOW')),
            confirmed_count=Count('id', filter=Q(status='CONFIRMED'))
        )

        # 2. Location Analysis: Groups reservation data by restaurant names to surface regional performance
        location_breakdown = Booking.objects.values('restaurant__restaurant_name').annotate(
            total_bookings=Count('id'),
            no_shows=Count('id', filter=Q(status='NO_SHOW')),
            cancellations=Count('id', filter=Q(status='CANCELLED'))
        )

        # 3. CRM Metrics: Uses an annotation layer to track returning customers (those with multiple entries)
        customer_retention = Customer.objects.annotate(
            booking_count=Count('bookings')
        ).aggregate(
            total_tracked_customers=Count('id'),
            returning_customers=Count('id', filter=Q(booking_count__gt=1)),
            one_time_customers=Count('id', filter=Q(booking_count=1))
        )

        # 4. Payload Dispatch: Package all analytics vectors into a uniform JSON response structure
        return Response({
            "status": "success",
            "summary_metrics": booking_metrics,
            "venue_breakdown": location_breakdown,
            "crm_retention_metrics": customer_retention
        })