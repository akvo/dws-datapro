from django.utils import timezone
from api.v1.v1_data.models import FormData


def seed_approved_data(data: FormData):
    """
    Update FormData object from pending status to approved status
    """
    # No need to create new data, just update existing FormData
    data.updated = timezone.now()
    data.is_pending = False
    data.save()

    # Save to file after approval
    if not data.form.parent:
        # If the form is a parent form, save to file
        data.save_to_file

    return data
