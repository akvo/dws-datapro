from faker import Faker
import re
import uuid

from django.core.management import BaseCommand
from api.v1.v1_users.models import SystemUser
from api.v1.v1_profile.models import Access, Administration
from api.v1.v1_profile.constants import UserRoleTypes
from api.v1.v1_forms.models import UserForms, UserFormAccess
from api.v1.v1_forms.constants import FormAccessTypes

fake = Faker()


def new_user(administrations):
    for administration in administrations:
        email = ("{}{}@test.com").format(
            re.sub('[^A-Za-z0-9]+', '', administration.name.lower()),
            administration.id)
        email = "{}_{}".format(str(uuid.uuid4())[:4], email)
        user, _ = SystemUser.objects.get_or_create(
            email=email,
            first_name=administration.name,
            last_name="Approver",
        )
        user.set_password("test")
        user.save()

        # Create user access with admin role (no longer using approver role)
        Access.objects.create(
            user=user,
            role=UserRoleTypes.admin,  # All users are admins now
            administration=administration
        )

        # Assign form access for any forms they need to approve
        from api.v1.v1_forms.models import Forms
        forms = Forms.objects.all()
        for form in forms:
            user_form, _ = UserForms.objects.get_or_create(
                user=user,
                form=form
            )
            # For non-level 1 (non-admin) users, grant approver access
            if administration.level.level > 1:
                UserFormAccess.objects.get_or_create(
                    user_form=user_form,
                    access_type=FormAccessTypes.approve
                )


class Command(BaseCommand):
    help = "Create fake approver users with access to forms"

    def add_arguments(self, parser):
        parser.add_argument(
            "-r",
            "--repeat",
            nargs="?",
            const=1,
            default=1,
            type=int
        )

    def handle(self, *args, **options):
        repeat = options.get("repeat")
        # Approvers (with approver form access)
        administrations = Administration.objects.filter(
            level__level__gt=0
        ).order_by('?')[:repeat]
        new_user(administrations)
