from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Customer, Employee, Owner
from .permissions import CustomerProfileAccess, EmployeeManagementAccess, get_actor_role

# =====================================================================
# 1. CUSTOMER IDENTITY CONTROLLER ENVELOPE
# =====================================================================

class CustomerViewSet(viewsets.ModelViewSet):
    """Handles account creations, tracking, and deep custom occasion modifications."""
    queryset = Customer.objects.all()
    permission_classes = [CustomerProfileAccess]

    @action(detail=False, methods=['get', 'put'])
    def self_service_portal(self, request):
        """Allows public consumers to fetch, track, and modify their personal profile details securely."""
        first = request.headers.get('X-Customer-First')
        last = request.headers.get('X-Customer-Last')
        phone = request.headers.get('X-Customer-Phone')

        try:
            profile = Customer.objects.get(first_name=first, last_name=last, phone=phone)
        except Customer.DoesNotExist:
            return Response({"error": "Account profile lookup matching credentials failed."}, status=status.HTTP_444_NOT_FOUND)

        if request.method == 'GET':
            return Response({
                "first_name": profile.first_name, "last_name": profile.last_name, "phone": profile.phone,
                "email": profile.email, "dob": profile.dob, "anniversary_date": profile.anniversary_date,
                "important_occasion_notes": profile.important_occasion_notes
            })

        elif request.method == 'PUT':
            # Process modification instructions for personal data updates
            profile.email = request.data.get('email', profile.email)
            profile.address = request.data.get('address', profile.address)
            profile.anniversary_date = request.data.get('anniversary_date', profile.anniversary_date)
            profile.important_occasion_notes = request.data.get('important_occasion_notes', profile.important_occasion_notes)
            profile.save()
            return Response({"success": "Customer CRM profile information successfully updated."})


# =====================================================================
# 2. OWNER STRATEGIC STAFF MANAGEMENT PORTAL
# =====================================================================

class OwnerStaffManagementViewSet(viewsets.ModelViewSet):
    """Provides business owners full rights to hire, edit, or purge employee profiles."""
    queryset = Employee.objects.all()
    permission_classes = [EmployeeManagementAccess]

    def create(self, request, *args, **kwargs):
        role, entity = get_actor_role(request)
        if role != 'Owner' and role != 'SuperAdmin':
            return Response({"error": "Unauthorized permission tier level allocation barrier."}, status=status.HTTP_403_FORBIDDEN)

        # Automatically bind new hires to the active owner's parent company
        group = entity.restaurant_group if role == 'Owner' else request.data.get('restaurant_group_id')
        
        new_staff = Employee.objects.create(
            employee_id=request.data.get('employee_id'),
            restaurant_group_id=group if role == 'SuperAdmin' else group.restaurant_group_id,
            first_name=request.data.get('first_name'),
            last_name=request.data.get('last_name'),
            address=request.data.get('address'),
            phone=request.data.get('phone'),
            email=request.data.get('email'),
            dob=request.data.get('dob'),
            base_annual_salary=request.data.get('base_annual_salary')
        )
        return Response({"success": f"New worker account successfully initialized under ID {new_staff.employee_id}."}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Fulfills the requirement to completely purge staff records when they leave the business."""
        staff_member = self.get_object()
        self.check_object_permissions(request, staff_member)
        staff_member.delete()
        return Response({"success": "Employee record completely purged from database system rosters."}, status=status.HTTP_200_OK)


# =====================================================================
# 3. SUPERADMIN SYSTEM SYSTEM MASTER MODULE
# =====================================================================

class SuperAdminSystemModuleViewSet(viewsets.ViewSet):
    """Global system tools exclusively accessible by platform Super Admins."""

    @action(detail=False, methods=['post'])
    def administrative_profile_unlock(self, request):
        """Allows platform Super Admins to manually unlock accounts if someone gets locked out."""
        role, entity = get_actor_role(request)
        if role != 'SuperAdmin':
            return Response({"error": "System Override Access Denied: Action requires absolute platform authority privileges."}, status=status.HTTP_403_FORBIDDEN)

        target_uid = request.data.get('locked_account_id')
        account_type = request.data.get('account_type') # Expected values: 'Owner' or 'Employee'

        if account_type == 'Owner':
            try:
                profile = Owner.objects.get(owner_id=target_uid)
                profile.is_locked_out = False
                profile.save()
                return Response({"success": f"Platform Status Reset: Owner profile card '{target_uid}' unlocked safely."})
            except Owner.DoesNotExist:
                return Response({"error": "Target owner account identifier matches no file logs."}, status=status.HTTP_404_NOT_FOUND)

        elif account_type == 'Employee':
            try:
                profile = Employee.objects.get(employee_id=target_uid)
                profile.is_locked_out = False
                profile.save()
                return Response({"success": f"Platform Status Reset: Staff profile card '{target_uid}' unlocked safely."})
            except Employee.DoesNotExist:
                return Response({"error": "Target staff account identifier matches no file logs."}, status=status.HTTP_444_NOT_FOUND)

        return Response({"error": "Invalid administrative classification argument."}, status=status.HTTP_400_BAD_REQUEST)

SuperAdminOverrideViewSet = SuperAdminSystemModuleViewSet

SuperAdminOverrideViewSet = SuperAdminSystemModuleViewSet
