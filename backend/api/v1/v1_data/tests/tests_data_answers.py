from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from api.v1.v1_data.models import FormData


@override_settings(USE_TZ=False)
class DataAnswersTestCase(TestCase):
    def setUp(self):
        call_command("administration_seeder", "--test")
        call_command("form_seeder", "--test")

        user_payload = {"email": "admin@akvo.org", "password": "Test105*"}
        user_response = self.client.post(
            "/api/v1/login", user_payload, content_type="application/json"
        )
        self.token = user_response.json().get("token")
        call_command("fake_data_seeder", "-r", 1, "-t", True)
        self.data = FormData.objects.filter(
            form__pk=3,
            is_pending=False,
        ).order_by("?").first()

    def test_success_data_answers(self):
        data_id = self.data.id

        response = self.client.get(
            f"/api/v1/data/{data_id}",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data), 0)
        self.assertEqual(
            list(data[0]),
            ["history", "question", "value", "index"]
        )

    def test_error_data_answers(self):
        invalid_data_id = 9999
        response = self.client.get(
            f"/api/v1/data/{invalid_data_id}",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Not found.")

    def test_pending_data_answers(self):
        pending_data = FormData.objects.filter(
            form__pk=3,
            is_pending=True,
        ).order_by("?").first()

        if pending_data:
            pending_data_id = pending_data.id
            response = self.client.get(
                f"/api/v1/data/{pending_data_id}",
                HTTP_AUTHORIZATION=f"Bearer {self.token}",
            )
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json()["detail"], "Not found.")
        else:
            self.skipTest("No pending data available for testing.")

    def test_data_answers_anonymous_user(self):
        data_id = self.data.id
        response = self.client.get(f"/api/v1/data/{data_id}")
        self.assertEqual(response.status_code, 200)

    def test_data_answers_invalid_post_method(self):
        data_id = self.data.id
        response = self.client.post(
            f"/api/v1/data/{data_id}",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["detail"],
            "You do not have permission to perform this action."
        )

    def test_data_answers_invalid_put_method(self):
        data_id = self.data.id
        response = self.client.put(
            f"/api/v1/data/{data_id}",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["detail"],
            "You do not have permission to perform this action."
        )

    def test_data_answers_invalid_delete_method(self):
        data_id = self.data.id
        response = self.client.delete(
            f"/api/v1/data/{data_id}",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 204)

    def test_data_answers_delete_no_authentication(self):
        data_id = self.data.id
        response = self.client.delete(f"/api/v1/data/{data_id}")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json()["detail"],
            "Authentication credentials were not provided."
        )
