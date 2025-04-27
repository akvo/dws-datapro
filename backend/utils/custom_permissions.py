from rest_framework.permissions import BasePermission

from api.v1.v1_profile.constants import UserRoleTypes
from api.v1.v1_forms.models import UserFormAccess
from api.v1.v1_forms.constants import UserFormAccessTypes


class IsSubmitter(BasePermission):
    def has_permission(self, request, view):
        # Check for approver access via UserFormAccess
        has_edit_access = UserFormAccess.objects.filter(
            user_form__user=request.user,
            access_type=UserFormAccessTypes.edit
        ).exists()
        if has_edit_access:
            return True
        return False


class IsApprover(BasePermission):
    def has_permission(self, request, view):
        # Check if user has any form with approver access
        has_approver_access = UserFormAccess.objects.filter(
            user_form__user=request.user,
            access_type=UserFormAccessTypes.approver
        ).exists()
        return has_approver_access


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.user_access.role == UserRoleTypes.admin:
            return True
        return False


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.user_access.role == UserRoleTypes.super_admin:
            return True
        return False


class PublicGet(BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        if request.user.is_anonymous:
            return False
        if request.method == "DELETE":
            if request.user.user_access.role in [
                UserRoleTypes.super_admin,
                UserRoleTypes.admin,
            ]:
                return True
            return False
        if request.user.user_access.role in [
            UserRoleTypes.super_admin,
            UserRoleTypes.admin,
        ]:
            return True
        # Check for approver access via UserFormAccess
        has_approver_access = UserFormAccess.objects.filter(
            user_form__user=request.user,
            access_type=UserFormAccessTypes.approver
        ).exists()
        if has_approver_access:
            return True
        return False
