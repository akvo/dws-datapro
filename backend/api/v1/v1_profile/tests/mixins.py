import typing
from django.core.management.color import no_style
from django.db import connection
from django.test.client import Client
from faker import Faker
from api.v1.v1_profile.models import (
    Administration,
    Role,
    UserRole,
)
from api.v1.v1_users.models import SystemUser
from api.v1.v1_forms.models import UserForms, Forms
fake = Faker()


class HasTestClientProtocol(typing.Protocol):
    @property
    def client(self) -> Client:
        ...


class ProfileTestHelperMixin:

    IS_SUPER_ADMIN = 0
    IS_ADMIN = 1
    IS_APPROVER = 2

    def create_user(
        self,
        email: str,
        role_level: int,
        password: str = 'password',
        administration: Administration = None,
        form: Forms = None,
    ) -> SystemUser:
        user = SystemUser.objects.filter(email=email).first()
        if user:
            return user
        profile = fake.profile()
        name = profile.get("name")
        name = name.split(" ")
        user = SystemUser.objects.create(
            email=email,
            first_name=name[0],
            last_name=name[1])
        user.set_password(password)
        user.save()

        if not administration:
            if role_level == self.IS_SUPER_ADMIN:
                administration = Administration.objects.filter(
                    level__level=0
                ).order_by('?').first()
            else:
                administration = Administration.objects.filter(
                    level__level__gt=0
                ).order_by('?').first()
        if form:
            UserForms.objects.get_or_create(
                user=user,
                form=form
            )
        if role_level != self.IS_SUPER_ADMIN:
            role_name = "{0} {1}".format(
                administration.level.name,
                "Approver" if role_level == self.IS_APPROVER else "Admin"
            )
            role = Role.objects.filter(
                administration_level=administration.level,
                name=role_name,
            ).order_by('?').first()
            if role:
                UserRole.objects.get_or_create(
                    user=user,
                    role=role,
                    administration=administration
                )
        return user

    @staticmethod
    def reset_db_sequence(*models):
        """
        Auto fields are no longer incrementing after running create with
        explicit id parameter

        see: https://code.djangoproject.com/ticket/11423
        """
        sequence_sql = connection.ops.sequence_reset_sql(no_style(), models)
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)

    def get_auth_token(self: HasTestClientProtocol,
                       email: str,
                       password: str = 'password') -> str:
        response = self.client.post(
                '/api/v1/login',
                {'email': email, 'password': password},
                content_type='application/json')
        user = response.json()
        return user.get('token')
