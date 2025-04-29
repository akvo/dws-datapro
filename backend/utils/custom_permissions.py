from rest_framework.permissions import BasePermission

from api.v1.v1_profile.constants import UserRoleTypes
from api.v1.v1_forms.models import FormAccess
from api.v1.v1_forms.constants import FormAccessTypes


class IsEditor(BasePermission):
    def has_permission(self, request, view):
        # Check for approver access via FormAccess
        has_edit_access = FormAccess.objects.filter(
            user_form__user=request.user,
            access_type=FormAccessTypes.edit
        ).exists()
        if has_edit_access:
            return True
        return False


class IsApprover(BasePermission):
    def has_permission(self, request, view):
        # Check if user has any form with approver access
        has_approver_access = FormAccess.objects.filter(
            user_form__user=request.user,
            access_type=FormAccessTypes.approve
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


class IsEditorOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        is_editor = IsEditor().has_permission(request, view)
        is_super_admin = IsSuperAdmin().has_permission(request, view)
        return is_editor or is_super_admin


class IsSuperAdminOrFormUser(BasePermission):
    # Check if the user is a super admin or has form access
    def has_permission(self, request, view):
        # Check if user is super admin
        if request.user.user_access.role == UserRoleTypes.super_admin:
            return True
        # Check if user has any form
        has_form_access = FormAccess.objects.filter(
            user_form__user=request.user,
            user_form__form_id=view.kwargs.get("form_id")
        ).exists()
        return has_form_access


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
        # Check for approver access via FormAccess
        has_approver_access = FormAccess.objects.filter(
            user_form__user=request.user,
            access_type=FormAccessTypes.approve
        ).exists()
        if has_approver_access:
            return True
        return False
