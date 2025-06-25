from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from api.v1.v1_profile.models import Administration
from api.v1.v1_profile.tests.mixins import ProfileTestHelperMixin


@override_settings(USE_TZ=False, TEST_ENV=True)
class UserListTestCase(TestCase, ProfileTestHelperMixin):
    def setUp(self):
        call_command("administration_seeder", "--test")
        call_command("default_roles_seeder", "--test", 1)
        call_command("fake_organisation_seeder", "--repeat", 2)
        call_command(
            "fake_user_seeder",
            "--repeat",
            10,
            "--test",
            1
        )

        # Create a superuser for testing
        self.superuser = self.create_user(
            email="super@akvo.org",
            role_level=self.IS_SUPER_ADMIN,
        )
        self.token = self.get_auth_token(self.superuser.email)

    def test_get_user_list(self):
        response = self.client.get(
            "/api/v1/users",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        user_data = response.json()
        # Check pagination structure
        self.assertIn("current", user_data)
        self.assertIn("total", user_data)
        self.assertIn("total_page", user_data)
        self.assertIn("data", user_data)

        self.assertIsInstance(user_data["data"], list)
        self.assertGreater(len(user_data["data"]), 0)
        # Check if each user has the required fields
        for user in user_data["data"]:
            self.assertIn("email", user)
            self.assertIn("first_name", user)
            self.assertIn("last_name", user)
            self.assertIn("roles", user)
            self.assertIn("trained", user)
            self.assertIn("phone_number", user)
            self.assertIn("forms", user)
            self.assertIn("organisation", user)
            self.assertIn("last_login", user)
            self.assertIn("id", user)

    def test_get_user_list_unauthenticated(self):
        response = self.client.get(
            "/api/v1/users",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())
        self.assertEqual(
            response.json()["detail"],
            "Authentication credentials were not provided."
        )

    def test_get_user_list_with_non_superuser(self):
        # Create a non-superuser for testing
        non_superuser = self.create_user(
            email="nonsuper@test.com",
            role_level=self.IS_ADMIN,
            administration=Administration.objects.filter(
                parent_administration__isnull=True,
                level__level__gt=0
            ).first()
        )
        non_superuser_token = self.get_auth_token(non_superuser.email)
        response = self.client.get(
            "/api/v1/users",
            HTTP_AUTHORIZATION=f"Bearer {non_superuser_token}",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("detail", response.json())
        self.assertEqual(
            response.json()["detail"],
            "You do not have permission to perform this action."
        )
