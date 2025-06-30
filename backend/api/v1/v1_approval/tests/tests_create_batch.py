from django.test import TestCase
from django.test.utils import override_settings
from django.core.management import call_command

from api.v1.v1_data.models import FormData
from api.v1.v1_profile.models import Administration
from api.v1.v1_profile.tests.mixins import ProfileTestHelperMixin


@override_settings(USE_TZ=False, TEST_ENV=True)
class CreateDataBatchTestCase(TestCase, ProfileTestHelperMixin):
    def setUp(self):
        call_command("administration_seeder", "--test", 1)
        call_command("default_roles_seeder", "--test", 1)
        call_command("form_seeder", "--test", 1)

        call_command("fake_data_seeder", "-r", 10, "-t", True)

        self.data = FormData.objects.filter(
            is_pending=True,
            administration__level__level=3,
        ).first()
        self.submitter = self.data.created_by
        self.submitter.set_password("test")
        self.submitter.save()

        self.token = self.get_auth_token(self.submitter.email, "test")

    def test_success_create_batch(self):
        payload = {
            "name": "Test Batch",
            "comment": "This is a test batch",
            "data": [self.data.id],
        }
        response = self.client.post(
            "/api/v1/batch",
            payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertIn("message", response_json)
        self.assertEqual(
            response_json["message"], "Batch created successfully"
        )

    def test_create_batch_without_data(self):
        payload = {
            "name": "Test Batch",
            "comment": "This is a test batch",
            "data": [],
        }
        response = self.client.post(
            "/api/v1/batch",
            payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_batch_with_invalid_data(self):
        payload = {
            "name": "Test Batch",
            "comment": "This is a test batch",
            "data": [9999],  # Assuming 9999 is an invalid ID
        }
        response = self.client.post(
            "/api/v1/batch",
            payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_batch_without_name(self):
        payload = {
            "comment": "This is a test batch",
            "data": [self.data.id],
        }
        response = self.client.post(
            "/api/v1/batch",
            payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_batch_without_comment(self):
        payload = {
            "name": "Test Batch",
            "data": [self.data.id],
        }
        response = self.client.post(
            "/api/v1/batch",
            payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 201)

    def test_create_batch_with_unauthorized_user(self):
        unauthorized_user = self.create_user(
            email="john.123@mail.com",
            administration=self.data.administration,
            role_level=self.IS_ADMIN,
            form=self.data.form,
        )
        unauthorized_user.set_password("test")
        unauthorized_user.save()
        token = self.get_auth_token(unauthorized_user.email, "test")

        payload = {
            "name": "Test Batch",
            "comment": "This is a test batch",
            "data": [self.data.id],
        }
        response = self.client.post(
            "/api/v1/batch",
            payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())
        self.assertEqual(
            response.json()["detail"],
            {
                "data": [
                    "One or more data items were not submitted by the user."
                ]
            },
        )

    def test_create_batch_with_multiple_data_entries(self):
        # Create additional data entries
        additional_data = []
        for i in range(2):
            new_data = FormData.objects.create(
                name=f"Test Data #{i+1}",
                geo=[0, 0],
                form=self.data.form,
                administration=self.data.administration,
                created_by=self.submitter,
                is_pending=True,
            )
            additional_data.append(new_data.id)

        payload = {
            "name": "Test Batch with Multiple Data",
            "comment": "This batch contains multiple data entries",
            "data": [self.data.id] + additional_data,
        }
        response = self.client.post(
            "/api/v1/batch",
            payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertIn("message", response_json)
        self.assertEqual(
            response_json["message"], "Batch created successfully"
        )

    def test_create_batch_with_different_administration(self):
        # Create additional data entries with a different administration
        other_administration = (
            Administration.objects.exclude(
                id=self.data.administration.id,
            )
            .filter(level=self.data.administration.level)
            .first()
        )
        additional_data = []
        for i in range(2):
            new_data = FormData.objects.create(
                name=f"Test Data Other Admin #{i+1}",
                geo=[0, 0],
                form=self.data.form,
                administration=other_administration,
                created_by=self.submitter,
                is_pending=True,
            )
            additional_data.append(new_data.id)

        payload = {
            "name": "Test Batch with Other Admin Data",
            "comment": "This batch contains data from another administration",
            "data": [self.data.id] + additional_data,
        }
        response = self.client.post(
            "/api/v1/batch",
            payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())
        self.assertEqual(
            response.json()["detail"],
            {"data": ["All data must belong to the same administration."]},
        )

    def test_create_batch_with_different_forms(self):
        # Create additional data entries with a different form
        other_form = self.submitter.user_form.exclude(
            form=self.data.form
        ).first().form
        additional_data = []
        for _ in range(5):
            new_data = FormData.objects.create(
                name="Test Data Other Form",
                geo=[0, 0],
                form=other_form,
                administration=self.data.administration,
                created_by=self.submitter,
            )
            additional_data.append(new_data.id)

        payload = {
            "name": "Test Batch with Other Form Data",
            "comment": "This batch contains data from another form",
            "data": [self.data.id] + additional_data,
        }
        response = self.client.post(
            "/api/v1/batch",
            payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_batch_with_empty_payload(self):
        payload = {}
        response = self.client.post(
            "/api/v1/batch",
            payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 400)
