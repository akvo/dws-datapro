from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from api.v1.v1_profile.tests.mixins import ProfileTestHelperMixin
from api.v1.v1_users.models import Organisation


@override_settings(USE_TZ=False, TEST_ENV=True)
class UpdateProfileTestCase(TestCase, ProfileTestHelperMixin):
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

    def test_update_user_profile(self):
        org = Organisation.objects.order_by("?").first()
        payload = {
            "first_name": "UpdatedFirstName",
            "last_name": "UpdatedLastName",
            "phone_number": "+1234567890",
            "organisation": org.id,
        }
        response = self.client.put(
            "/api/v1/update-profile",
            payload,
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["name"], "UpdatedFirstName UpdatedLastName"
        )
        self.assertEqual(response.data["phone_number"], "+1234567890")
        self.assertEqual(response.data["organisation"]["id"], org.id)
        self.assertEqual(response.data["organisation"]["name"], org.name)
        self.assertEqual(response.data["email"], self.superuser.email)

    def test_update_user_profile_invalid_data(self):
        payload = {
            "email": "invalid_email",  # Invalid email format
            "first_name": "",
            "last_name": "",
            "phone_number": "invalid_phone",
            "organisation": 9999,  # Non-existent organisation
        }
        response = self.client.put(
            "/api/v1/update-profile",
            payload,
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_update_user_profile_empty_payload(self):
        payload = {}
        response = self.client.put(
            "/api/v1/update-profile",
            payload,
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_update_user_profile_empty_string(self):
        payload = {
            "email": "",
            "first_name": "",
            "last_name": "",
            "phone_number": "",
            "organisation": "",
        }
        response = self.client.put(
            "/api/v1/update-profile",
            payload,
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_update_user_profile_unauthenticated(self):
        payload = {
            "first_name": "Unauthenticated",
            "last_name": "User",
            "phone_number": "+1234567890",
        }
        response = self.client.put(
            "/api/v1/update-profile",
            payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)
        self.assertEqual(
            response.data["detail"],
            "Authentication credentials were not provided."
        )
