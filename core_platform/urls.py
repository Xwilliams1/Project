from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from restaurant_app.views import (
    CustomerViewSet, 
    OwnerStaffManagementViewSet, 
    SuperAdminOverrideViewSet
)

# 1. Initialize Django REST Framework's Automated URL Router
router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'owner-staff', OwnerStaffManagementViewSet, basename='owner-staff')
router.register(r'superadmin-actions', SuperAdminOverrideViewSet, basename='superadmin-actions')

# 2. Map Core System Endpoints
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Pipes routing prefixes (api/customers/) directly into your custom views
    path('api/', include(router.urls)),
]
