from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from api.v1.v1_forms.models import Forms
from api.v1.v1_profile.models import Administration
from api.v1.v1_profile.tests.mixins import ProfileTestHelperMixin


@override_settings(USE_TZ=False)
class FormCheckApproverTestCase(TestCase, ProfileTestHelperMixin):
    def setUp(self):
        call_command("administration_seeder", "--test", 1)
        call_command("default_roles_seeder", "--test", 1)
        call_command("form_seeder", "--test", 1)

        self.form = Forms.objects.filter(
            parent__isnull=True
        ).order_by("?").first()

        self.adm = Administration.objects.filter(
            level__level__gt=2,
        ).first()

        user = self.create_user(
            email="user.123@test.com",
            role_level=self.IS_ADMIN,
            administration=self.adm,
            form=self.form,
        )
        user.set_password("password")
        user.save()

        self.token = self.get_auth_token(
            email=user.email,
            password="password",
        )

    def test_get_check_form_approvers_with_zero_approver(self):
        response = self.client.get(
            f"/api/v1/form/check-approver/{self.form.id}/",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data, {"count": 0})

    def test_get_check_form_approvers_with_one_approver(self):
        self.create_user(
            email="approver.123@test.com",
            role_level=self.IS_APPROVER,
            administration=self.adm,
            form=self.form,
        )

        response = self.client.get(
            f"/api/v1/form/check-approver/{self.form.id}/",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data, {"count": 1})

    def test_get_unauthorized_check_form_approvers(self):
        response = self.client.get(
            f"/api/v1/form/check-approver/{self.form.id}/",
            HTTP_AUTHORIZATION="Bearer invalid_token",
        )
        self.assertEqual(response.status_code, 401)

    def test_get_check_form_approvers_with_invalid_form_id(self):
        response = self.client.get(
            "/api/v1/form/check-approver/9999/",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 404)
