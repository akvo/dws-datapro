from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from api.v1.v1_profile.tests.mixins import ProfileTestHelperMixin
from api.v1.v1_users.models import SystemUser


@override_settings(USE_TZ=False, TEST_ENV=True)
class UserDetailsTestCase(TestCase, ProfileTestHelperMixin):
    def setUp(self):
        call_command("administration_seeder", "--test")
        call_command("default_roles_seeder", "--test", 1)
        call_command("fake_organisation_seeder", "--repeat", 2)
        call_command("fake_user_seeder", "--repeat", 10, "--test", 1)
        # Create a superuser for testing
        self.superuser = self.create_user(
            email="super@akvo.org",
            role_level=self.IS_SUPER_ADMIN,
        )
        self.token = self.get_auth_token(self.superuser.email)

    def test_get_user_detail(self):
        user = (
            SystemUser.objects.filter(
                user_user_role__isnull=False,
            )
            .order_by("?")
            .first()
        )
        if not user:
            self.fail("No user found for detail test")
        response = self.client.get(
            f"/api/v1/user/{user.id}",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        user_data = response.json()
        # Check if user data contains the required fields
        self.assertEqual(
            list(user_data),
            [
                "first_name",
                "last_name",
                "email",
                "roles",
                "organisation",
                "trained",
                "phone_number",
                "forms",
                "pending_approval",
                "data",
                "pending_batch",
                "is_superuser",
                "administration",
            ],
        )

        # Check user data matches the user
        self.assertEqual(user_data["email"], user.email)

    def test_get_user_detail_unauthenticated(self):
        user = (
            SystemUser.objects.filter(
                user_user_role__isnull=False,
            )
            .order_by("?")
            .first()
        )
        if not user:
            self.fail("No user found for detail test")
        response = self.client.get(
            f"/api/v1/users/{user.id}", content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())
        self.assertEqual(
            response.json()["detail"],
            "Authentication credentials were not provided."
        )
