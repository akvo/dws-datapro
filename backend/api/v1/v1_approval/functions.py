import uuid
from datetime import datetime
from django.utils.timezone import make_aware

from api.v1.v1_approval.constants import DataApprovalStatus
from api.v1.v1_approval.models import (
    DataBatch,
    DataBatchList,
    DataApproval,
    DataBatchComments
)
from api.v1.v1_data.tasks import seed_approved_data


def create_batch_with_approvals(
    data_items,
    administration,
    user,
    approved_flag,
    batch_size=5
):
    """
    Create batches and handle approval process for form data

    Args:
        data_items: List of FormData objects to batch
        administration: Administration object
        user: User object who created the batch
        batch_name: Base name for the batch
        approved_flag: Boolean indicating if batch should be approved
        batch_size: Number of items per batch (default: 5)

    Returns:
        List of created DataBatch objects
    """
    created_batches = []

    # Group data items into batches
    for i in range(0, len(data_items), batch_size):
        batch_data = data_items[i:i + batch_size]

        # Create a unique and incremental batch name
        # Use total number of batches stored in the database
        # to ensure uniqueness and avoid conflicts
        # This assumes that the batch name is not unique across all batches
        # and that the batch name is not used for any other purpose
        # If you need a unique name, consider using a UUID or timestamp
        # Here we use a simple incremental naming scheme
        # based on the index of the batch in the list
        if not batch_data:
            continue
        batch_count = DataBatch.objects.count()
        batch_name = f"Batch #{batch_count + 1} - {batch_data[0].form.name}"
        # Create DataBatch
        batch = DataBatch.objects.create(
            form=batch_data[0].form,  # All data in batch share same form
            administration=administration,
            user=user,
            name=f"{batch_name}  ({i//batch_size + 1})",
            uuid=uuid.uuid4(),
            approved=approved_flag
        )

        # Create DataBatchList entries for each FormData
        for data in batch_data:
            DataBatchList.objects.create(
                batch=batch,
                data=data
            )

        # Create approval entries (always with comments)
        _create_batch_approvals(batch, approved_flag)

        # Handle approved data
        if approved_flag:
            for data in batch_data:
                seed_approved_data(data)

        created_batches.append(batch)

    return created_batches


def _create_batch_approvals(batch, approved_flag):
    """
    Create DataApproval entries for a batch
    Always includes approval comments for each approver

    Args:
        batch: DataBatch object
        approved_flag: Boolean indicating if approvals should be approved
    """
    # Get approvers for this batch
    approvers = batch.approvers()

    # Create DataApproval entries
    for approver_info in approvers:
        approval_status = (
            DataApprovalStatus.approved if approved_flag
            else DataApprovalStatus.pending
        )

        DataApproval.objects.create(
            batch=batch,
            administration=approver_info['administration'],
            role=approver_info['role'],
            user=approver_info['user'],
            status=approval_status,
            updated=(
                make_aware(datetime.now()) if approved_flag else None
            )
        )

        # Always add approval comment for each approver
        if approved_flag:
            DataBatchComments.objects.create(
                batch=batch,
                user=approver_info['user'],
                comment=(
                    f"Data approved by {approver_info['user'].email}"
                ),
            )
