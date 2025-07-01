from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from api.v1.v1_forms.models import Forms
from api.v1.v1_profile.models import Administration
from api.v1.v1_profile.tests.mixins import ProfileTestHelperMixin


@override_settings(USE_TZ=False)
class FormApproverTestCase(TestCase, ProfileTestHelperMixin):
    def setUp(self):
        call_command("administration_seeder", "--test", 1)
        call_command("default_roles_seeder", "--test", 1)
        call_command("form_seeder", "--test", 1)

        self.form = Forms.objects.filter(
            parent__isnull=True
        ).order_by("?").first()

        user = self.create_user(
            email="super@akvo.org",
            role_level=self.IS_SUPER_ADMIN,
        )
        user.set_password("password")
        user.save()

        self.token = self.get_auth_token(
            email=user.email,
            password="password",
        )

    def test_get_form_approvers_in_national_level(self):
        adm = Administration.objects.filter(
            parent__isnull=True,
        ).first()
        approver = self.create_user(
            email="national.approver@test.com",
            role_level=self.IS_APPROVER,
            administration=adm,
            form=self.form,
        )
        response = self.client.get(
            (
                "/api/v1/form/approver"
                f"?form_id={self.form.id}&administration_id={adm.id}"
            ),
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data), 0)

        national_adm = Administration.objects.filter(
            parent__isnull=True,
        ).first()
        national_approvers = [
            res["users"]
            for res in data if res["administration"]["id"] == national_adm.id
        ]
        national_approvers = [
            u for sublist in national_approvers for u in sublist
        ]
        self.assertIn(
            approver.email,
            [u["email"] for u in national_approvers],
        )

    def test_get_form_approvers_in_second_administration_level(self):
        adm = Administration.objects.filter(
            level__level=1,
        ).order_by("?").first()
        approver = self.create_user(
            email="second.approver@test.com",
            role_level=self.IS_APPROVER,
            administration=adm,
            form=self.form,
        )
        response = self.client.get(
            (
                "/api/v1/form/approver"
                f"?form_id={self.form.id}&administration_id={adm.id}"
            ),
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data), 0)

        second_approvers = [
            res["users"]
            for res in data if res["administration"]["id"] == adm.id
        ]
        second_approvers = [
            u for sublist in second_approvers for u in sublist
        ]
        self.assertIn(
            approver.email,
            [u["email"] for u in second_approvers],
        )

    def test_get_form_approvers_in_third_administration_level(self):
        adm = Administration.objects.filter(
            level__level=2,
        ).order_by("?").first()
        approver = self.create_user(
            email="third.approver@test.com",
            role_level=self.IS_APPROVER,
            administration=adm,
            form=self.form,
        )
        response = self.client.get(
            (
                "/api/v1/form/approver"
                f"?form_id={self.form.id}&administration_id={adm.id}"
            ),
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data), 0)

        third_approvers = [
            res["users"]
            for res in data if res["administration"]["id"] == adm.id
        ]
        third_approvers = [
            u for sublist in third_approvers for u in sublist
        ]
        self.assertIn(
            approver.email,
            [u["email"] for u in third_approvers],
        )

    def test_get_form_approvers_with_invalid_form_id(self):
        adm = Administration.objects.filter(
            level__level__gt=2,
        ).order_by("?").first()
        response = self.client.get(
            (
                "/api/v1/form/approver"
                f"?form_id=9999&administration_id={adm.id}"
            ),
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "message": 'Invalid pk "9999" - object does not exist.'
            }
        )

    def test_get_form_approvers_with_invalid_administration_id(self):
        response = self.client.get(
            (
                "/api/v1/form/approver"
                "?form_id=1&administration_id=9999"
            ),
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "message": 'Invalid pk "9999" - object does not exist.'
            }
        )

    def test_get_unauthorized_form_approvers(self):
        response = self.client.get(
            (
                "/api/v1/form/approver"
                f"?form_id={self.form.id}&administration_id=1"
            ),
            HTTP_AUTHORIZATION="Bearer invalid_token",
        )
        self.assertEqual(response.status_code, 401)

    def test_get_form_approvers_with_no_approvers(self):
        adm = Administration.objects.filter(
            parent__isnull=True,
        ).first()
        response = self.client.get(
            (
                "/api/v1/form/approver"
                f"?form_id={self.form.id}&administration_id={adm.id}"
            ),
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data[0]["users"], [])
