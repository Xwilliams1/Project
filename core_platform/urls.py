from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from restaurant_app.views import (
    CustomerViewSet, 
    OwnerStaffManagementViewSet, 
    SuperAdminOverrideViewSet,
    RestaurantViewSet,
    BookingViewSet
)

# 1. Initialize Django REST Framework's Automated URL Router
router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'owner-staff', OwnerStaffManagementViewSet, basename='owner-staff')
router.register(r'superadmin-actions', SuperAdminOverrideViewSet, basename='superadmin-actions')
router.register(r'restaurants', RestaurantViewSet, basename='restaurant')
router.register(r'bookings', BookingViewSet, basename='booking')

# 2. Map Core System Endpoints
urlpatterns = [
    # Built-in Django Administrative Interface Portal
    path('admin/', admin.site.urls),
    
    # Pipes automated database data endpoints straight to the browser/API clients
    path('api/', include(router.urls)),
    
    # Mounts local application app path configuration index
    path('', include('restaurant_app.urls')),
]
