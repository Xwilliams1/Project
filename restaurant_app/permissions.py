from rest_framework import permissions
from .models import SuperAdmin, Owner, Employee


def get_actor_role(request):
    """Identifies who is making the request by checking the User ID header."""
    auth_uid = request.META.get('HTTP_X_USER_ID')
    if not auth_uid:
        return 'Public_Guest', None

    if SuperAdmin.objects.filter(superadmin_id=auth_uid).exists():
        return 'SuperAdmin', auth_uid
    try:
        owner_obj = Owner.objects.get(owner_id=auth_uid)
        return 'Owner', owner_obj
    except Owner.DoesNotExist:
        pass
    try:
        emp_obj = Employee.objects.get(employee_id=auth_uid)
        return 'Employee', emp_obj
    except Employee.DoesNotExist:
        pass

    return 'Public_Guest', None


class CustomerProfileAccess(permissions.BasePermission):
    """
    Access Control Rules for Customers:
    - SuperAdmin: Global read/write access.
    - Owner/Employee: Can view profile/allergies during active service windows, but cannot alter them.
    - Customer: Full edit rights restricted entirely to their own natural key match.
    """

    def has_object_permission(self, request, view, obj):
        role, entity = get_actor_role(request)
        if role == 'SuperAdmin':
            return True

        if role in ['Owner', 'Employee']:
            return request.method in permissions.SAFE_METHODS

        cust_first = request.headers.get('X-Customer-First')
        cust_last = request.headers.get('X-Customer-Last')
        cust_phone = request.headers.get('X-Customer-Phone')

        return (obj.first_name == cust_first and
                obj.last_name == cust_last and
                obj.phone == cust_phone)


class EmployeeManagementAccess(permissions.BasePermission):
    """
    Access Control Rules for HR:
    - SuperAdmin: Full platform control.
    - Owner: Can create, modify, or delete employees strictly within their own corporate group.
    - Employee/Customer: Completely blocked.
    """

    def has_object_permission(self, request, view, obj):
        role, entity = get_actor_role(request)
        if role == 'SuperAdmin':
            return True

        if role == 'Owner':
            return obj.restaurant_group == entity.restaurant_group

        return False
