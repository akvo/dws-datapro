from django.utils import timezone
from typing import List
from api.v1.v1_profile.constants import UserRoleTypes
from api.v1.v1_forms.constants import UserFormAccessTypes
from api.v1.v1_forms.models import (
    FormApprovalAssignment,
    UserFormAccess,
    UserForms,
    Forms,
)
from api.v1.v1_data.models import PendingDataBatch, PendingDataApproval
from api.v1.v1_data.constants import DataApprovalStatus
from api.v1.v1_profile.models import Administration
from api.v1.v1_users.models import SystemUser


def is_has_approver(role: int, access_forms: list = None):
    # Check if user has approver access through access_forms
    has_approver_access = False
    if access_forms:
        for form_access in access_forms:
            if form_access.get('access_type') == UserFormAccessTypes.approve:
                has_approver_access = True
                break
    is_approver = role == UserRoleTypes.admin and has_approver_access
    is_super_admin = role == UserRoleTypes.super_admin
    return is_approver or is_super_admin


def check_form_approval_assigned(
    role: int,
    administration: Administration,
    user: SystemUser = None,
    access_forms: list = None
):
    forms = [
        item["form_id"]
        for item in access_forms
    ]
    # Check if user is super admin
    # Check if user is admin and has approver access
    unique_user = is_has_approver(
        role=role,
        access_forms=access_forms
    )
    # Check if user is not super admin and has no approver access
    # and is editing user
    if not unique_user and not user:
        return False
    # Check if form id x in y administration has approver assignment
    # send a message to FE 403
    form_approval_assignment_obj = FormApprovalAssignment.objects
    form_approval_assignment = form_approval_assignment_obj.filter(
        administration=administration
    )
    if not user:
        form_approval_assignment = form_approval_assignment.filter(
            form__in=forms
        )
    if user:  # for edited user
        # if administration updated
        if user.user_access.administration_id != administration.id:
            # check approver tree with prev administration and prev forms
            # if any, delete previous approver tree
            prev_approval_assignment = form_approval_assignment_obj.filter(
                administration_id=user.user_access.administration_id,
                form_id__in=[uf.form_id for uf in user.user_form.all()],
                user=user,
            )
            if prev_approval_assignment.count():
                # find administration path
                user_adm = user.user_access.administration
                filter_batch = {
                    "form_id__in": [uf.form_id for uf in user.user_form.all()],
                    "approved": False,
                }
                if user_adm.level.level in [0, 3]:
                    filter_batch.update({"administration_id": user_adm.id})
                else:
                    adm_path = f"{user_adm.path}{user_adm.id}"
                    filter_batch.update(
                        {"administration__path__startswith": adm_path}
                    )
                prev_pending_batch = PendingDataBatch.objects.filter(
                    **filter_batch
                ).values_list("id", flat=True)
                # check pending batch approval for prev user
                # find pending data approval by prev_pending_batch
                prev_pending_approval = PendingDataApproval.objects.filter(
                    batch_id__in=prev_pending_batch,
                    status=DataApprovalStatus.pending,
                    user=user,
                )
                if prev_pending_approval.count():
                    # raise an error to prevent administration update
                    # when edited user has pending data approval
                    prev_pending_approval.delete()
                prev_approval_assignment.delete()

        # check if updated user already have form assigned
        form_assigned = (
            form_approval_assignment.filter(user=user)
            .distinct("form")
            .values_list("form_id", flat=True)
        )
        form_assigned_to_delete = []
        form_to_assign = [
            item["form_id"].id
            for item in access_forms
            if item["access_type"] == UserFormAccessTypes.approve
        ]
        for fa in form_assigned:
            if fa not in form_to_assign:
                form_assigned_to_delete.append(fa)
            else:
                # remove assigned form from form filter
                form_to_assign.remove(fa)
        form_approval_assignment = form_approval_assignment.filter(
            form_id__in=form_to_assign
        )
        # delete approval assigned
        if form_assigned_to_delete:
            FormApprovalAssignment.objects.filter(
                administration=administration,
                form_id__in=form_assigned_to_delete,
                user=user,
            ).delete()

    form_approval_assignment = form_approval_assignment.distinct(
        "form", "administration"
    ).all()
    if form_approval_assignment:
        message_detail = [
            {"form": fa.form.name, "administration": fa.administration.name}
            for fa in form_approval_assignment
        ]
        return message_detail
    return False


def assign_form_approval(
    role: int,
    forms: List[Forms],
    administration: Administration,
    user: SystemUser,
    access_forms: List = None
):
    unique_user = is_has_approver(
        role=role,
        access_forms=access_forms
    )
    if not unique_user:
        return False

    form_to_assign = []
    for fr in forms:
        # Check if the user has approver access for this form
        user_form = UserForms.objects.filter(user=user, form=fr).first()
        has_approver_access = False

        # Check if the user has approver access through UserFormAccess
        if user_form:
            user_form_access = UserFormAccess.objects.filter(
                user_form=user_form,
                access_type=UserFormAccessTypes.approve
            ).exists()
            if user_form_access:
                has_approver_access = True

        # Only assign forms where the user has approver access
        if has_approver_access:
            form_to_assign.append(fr)

    # check if forms already assigned to user
    check = FormApprovalAssignment.objects.filter(
        administration=administration, form__in=form_to_assign, user=user
    )

    # Update existing assignments
    if check:
        # Remove already assigned forms from the list to assign
        form_to_assign = [
            fr for fr in form_to_assign
            if fr.id not in check.values_list("form_id", flat=True)
        ]

        # Update timestamps for existing assignments
        for fa in check.all():
            fa.updated = timezone.now()
            fa.save()
    # Add user value to approval assignment table (approval tree)
    form_approval_obj = [
        FormApprovalAssignment(
            form=fr, administration=administration, user=user
        )
        for fr in form_to_assign
    ]
    approval = FormApprovalAssignment.objects.bulk_create(form_approval_obj)

    # Assign to previous batch
    has_pending_data_batch = PendingDataBatch.objects.filter(
        approved=False
    ).count()
    if has_pending_data_batch:
        batch_filter = {"approved": False}
        if administration.path:
            batch_filter.update(
                {"administration__path__startswith": administration.path}
            )
        else:
            batch_filter.update({"administration": 1})
        current_batch = PendingDataBatch.objects.filter(**batch_filter).all()
        if current_batch.count():
            for batch in current_batch:
                # Only process forms that are in the approved list
                if batch.form in forms and batch.form in form_to_assign:
                    approver = PendingDataApproval.objects.filter(
                        level=administration.level, batch=batch
                    ).first()
                    if not approver:
                        approver = PendingDataApproval(
                            level=administration.level, user=user, batch=batch
                        )
                    else:
                        approver.user = user
                    approver.save()
                else:
                    approver = PendingDataApproval.objects.filter(
                        batch=batch, user=user
                    ).all()
                    approver.delete()
    return approval
