from rest_framework.permissions import BasePermission

from django.db.models import Q
from api.v1.v1_profile.constants import DataAccessTypes


class IsEditor(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_superuser:
            # Check if the user has edit or delete access
            return request.user.user_user_role.filter(
                role__role_role_access__data_access__in=[
                    DataAccessTypes.edit,
                    DataAccessTypes.delete,
                ]
            ).exists()
        return request.user.is_superuser


class IsApprover(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_superuser:
            # Check if the user has approve access
            return request.user.user_user_role.filter(
                role__role_role_access__data_access=DataAccessTypes.approve
            ).exists()
        return request.user.is_superuser


class IsSubmitter(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_superuser:
            # Check if the user has submit access
            return request.user.user_user_role.filter(
                role__role_role_access__data_access=DataAccessTypes.submit
            ).exists()
        return request.user.is_superuser


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class IsSuperAdminOrFormUser(BasePermission):
    # Check if the user is a super admin or has form access
    def has_permission(self, request, view):
        if not request.user.is_superuser:
            has_form_access = request.user.user_form.filter(
                Q(
                    form_id=view.kwargs.get("form_id")
                ) | Q(
                    form__children__id=view.kwargs.get("form_id")
                )
            ).exists()
            return has_form_access
        # Check if user is super admin
        return request.user.is_superuser


class PublicGet(BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        if request.user.is_anonymous:
            return False
        if request.method == "DELETE":
            is_editor = IsEditor().has_permission(request, view)
            is_super_admin = IsSuperAdmin().has_permission(request, view)
            return is_editor or is_super_admin
        return False
