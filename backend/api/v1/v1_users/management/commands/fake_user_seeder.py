import random
import re
import uuid

from django.core.management import BaseCommand
from faker import Faker

from api.v1.v1_profile.constants import UserRoleTypes, UserDesignationTypes
from api.v1.v1_profile.constants import OrganisationTypes
from api.v1.v1_profile.models import Levels, Access, Administration
from api.v1.v1_users.models import SystemUser, Organisation
from api.v1.v1_forms.models import Forms, UserForms, FormAccess
from api.v1.v1_forms.constants import FormAccessTypes
fake = Faker()

DEFAULT_PASSWORD = "Test#1234"


def create_user(
    administration: Administration,
    is_superadmin: bool = False,
    test: bool = False
) -> SystemUser:
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = ("{}@test.com").format(
        re.sub('[^A-Za-z0-9]+', '', first_name.lower()))
    email = "{}_{}".format(str(uuid.uuid4())[:4], email)
    organisation = Organisation.objects.filter(
        organisation_organisation_attribute=OrganisationTypes.member
    ).order_by('?').first()
    user = SystemUser.objects.create(
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone_number=fake.msisdn(),
        designation=UserDesignationTypes.sa
    )
    if organisation:
        user.organisation = organisation
    if test:
        password = random.choice(["test", None])
        if password:
            user.set_password(password)
    if not test:
        user.set_password(DEFAULT_PASSWORD)
    user.save()
    role = UserRoleTypes.super_admin if is_superadmin else UserRoleTypes.admin
    Access.objects.create(
        user=user,
        role=role,
        administration=administration
    )
    if is_superadmin:
        forms = Forms.objects.all()
        for form in forms:
            user_form, _ = UserForms.objects.get_or_create(
                user=user,
                form=form
            )
            FormAccess.objects.get_or_create(
                user_form=user_form,
                access_type=FormAccessTypes.read
            )
            FormAccess.objects.get_or_create(
                user_form=user_form,
                access_type=FormAccessTypes.edit
            )
    if not is_superadmin:
        form = Forms.objects.all().order_by('?').first()
        user_form, _ = UserForms.objects.get_or_create(
            user=user,
            form=form
        )
        FormAccess.objects.get_or_create(
            user_form=user_form,
            access_type=FormAccessTypes.read
        )
        FormAccess.objects.get_or_create(
            user_form=user_form,
            access_type=FormAccessTypes.edit
        )
    return user


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-r",
            "--repeat",
            nargs="?",
            const=1,
            default=1,
            type=int
        )
        parser.add_argument(
            "-t",
            "--test",
            nargs="?",
            const=False,
            default=False,
            type=bool
        )

    def handle(self, *args, **options):
        repeat = options.get("repeat")
        test = options.get("test")
        levels = Levels.objects.all()
        for level in levels:
            administration = Administration.objects.filter(
                level=level
            ).order_by('?').first()
            if not administration:
                continue
            for _ in range(repeat):
                create_user(
                    administration=administration,
                    is_superadmin=level.level == 0,
                    test=test
                )
