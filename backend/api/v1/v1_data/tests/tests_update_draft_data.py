from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from api.v1.v1_forms.models import Forms
from api.v1.v1_profile.models import Administration
from api.v1.v1_data.models import FormData
from api.v1.v1_profile.tests.mixins import ProfileTestHelperMixin


@override_settings(USE_TZ=False)
class UpdateDraftFormDataTestCase(TestCase, ProfileTestHelperMixin):
    def setUp(self):
        super().setUp()
        call_command("administration_seeder", "--test")
        call_command("form_seeder", "--test")
        call_command("default_roles_seeder", "--test", 1)
        self.form = Forms.objects.get(pk=1)

        self.administration = (
            Administration.objects.filter(level__level=3).order_by("?").first()
        )

        self.user = self.create_user(
            email="admin@akvo.org",
            role_level=self.IS_ADMIN,
            administration=self.administration,
            form=self.form,
        )
        self.user.set_password("password")
        self.user.save()

        self.token = self.get_auth_token(self.user.email, "password")
        self.reg_uuid = "8d1822c2-0b01-43e2-97f3-67ab71e5f946"
        payload = {
            "data": {
                "name": "Testing Data",
                "administration": self.administration.id,
                "geo": [6.2088, 106.8456],
                "uuid": self.reg_uuid,
            },
            "answer": [
                {"question": 101, "value": "Jane"},
                {"question": 102, "value": ["female"]},
                {"question": 103, "value": 6212111},
                {"question": 104, "value": 2.0},
                {"question": 105, "value": [6.2088, 106.8456]},
                {"question": 106, "value": ["parent"]},
                {"question": 109, "value": 0},
            ],
        }

        response = self.client.post(
            f"/api/v1/draft-submissions/{self.form.id}/",
            data=payload,
            content_type="application/json",
            **{'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 201)

        self.draft_data = FormData.objects_draft.first()

    def test_update_draft_data_payload(self):
        url = f"/api/v1/draft-submission/{self.draft_data.id}/"
        payload = {
            "data": {
                "name": "Updated Testing Data",
                "administration": self.administration.id,
                "geo": [6.2088, 106.8456],
                "uuid": self.reg_uuid,
            },
            "answer": [
                {"question": 101, "value": "Jane"},
                {"question": 102, "value": ["female"]},
                {"question": 103, "value": 6212111},
                {"question": 104, "value": 2.0},
                {"question": 105, "value": [6.2088, 106.8456]},
                {"question": 106, "value": ["parent", "children"]},
                {"question": 109, "value": 0},
            ],
        }
        response = self.client.put(
            url,
            data=payload,
            content_type="application/json",
            **{'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            data,
            {"message": "Draft updated successfully"}
        )

        # Verify the draft was updated
        updated_draft_data = FormData.objects_draft.get(id=self.draft_data.id)
        self.assertEqual(updated_draft_data.name, "Updated Testing Data")

    def test_update_incomplete_draft_submission(self):
        # First create a draft submission
        url = f"/api/v1/draft-submissions/{self.form.id}/"
        payload = {
            "data": {
                "name": "Incomplete Draft",
                "administration": self.administration.id,
                "uuid": self.reg_uuid,
            },
            "answer": [
                {"question": 101, "value": "Jane"},
            ]
        }
        response = self.client.post(
            url,
            data=payload,
            content_type="application/json",
            **{'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 201)

        # Get the created draft submission
        draft_data = FormData.objects_draft.filter(
            name="Incomplete Draft"
        ).first()
        self.assertIsNotNone(draft_data)

        # Now update the draft submission with complete data
        update_url = f"/api/v1/draft-submission/{draft_data.id}/"
        update_payload = {
            "data": {
                "name": "Updated Incomplete Draft",
                "administration": self.administration.id,
                "geo": [6.2088, 106.8456],
                "uuid": self.reg_uuid,
            },
            "answer": [
                {"question": 101, "value": "Jane"},
                {"question": 102, "value": ["female"]},
                {"question": 103, "value": 6212111},
                {"question": 104, "value": 2.0},
                {"question": 105, "value": [6.2088, 106.8456]},
                {"question": 106, "value": ["parent", "children"]},
                {"question": 109, "value": 0},
            ],
        }
        update_response = self.client.put(
            update_url,
            data=update_payload,
            content_type="application/json",
            **{'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        )
        self.assertEqual(update_response.status_code, 200)

        draft_data.refresh_from_db()
        self.assertEqual(draft_data.name, "Updated Incomplete Draft")
        self.assertEqual(draft_data.geo, [6.2088, 106.8456])
        # Verify the answers were updated
        self.assertEqual(draft_data.data_answer.count(), 7)

    def test_update_draft_data_with_invalid_payload(self):
        url = f"/api/v1/draft-submission/{self.draft_data.id}/"
        payload = {
            "data": {
                "name": "",
                "administration": 99999,  # Invalid administration ID
                "geo": "[6.2088, 106.8456]",  # Invalid geo format
                "uuid": self.reg_uuid,
            },
            "answer": [
                {"question": 101, "value": "Jane"},
                {"question": 102, "value": ["female"]},
                {"question": 103, "value": 6212111},
                {"question": 104, "value": 2.0},
                {"question": 105, "value": [6.2088, 106.8456]},
                {"question": 106, "value": ["parent", "children"]},
                {"question": 109, "value": 0},
            ],
        }

        response = self.client.put(
            url,
            data=payload,
            content_type="application/json",
            **{'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 400)

    def test_update_draft_data_with_non_existent_id(self):
        url = "/api/v1/draft-submission/99999/"
        payload = {
            "data": {
                "name": "Non-existent Draft",
                "administration": self.administration.id,
                "geo": [6.2088, 106.8456],
                "uuid": self.reg_uuid,
            },
            "answer": [
                {"question": 101, "value": "Jane"},
                {"question": 102, "value": ["female"]},
                {"question": 103, "value": 6212111},
                {"question": 104, "value": 2.0},
                {"question": 105, "value": [6.2088, 106.8456]},
                {"question": 106, "value": ["parent", "children"]},
                {"question": 109, "value": 0},
            ],
        }
        response = self.client.put(
            url,
            data=payload,
            content_type="application/json",
            **{'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 404)

    def test_update_draft_answers_only(self):
        url = f"/api/v1/draft-submission/{self.draft_data.id}/"
        payload = {
            "data": {
                "name": "Testing Data",
                "administration": self.administration.id,
                "geo": [6.2088, 106.8456],
                "uuid": self.reg_uuid,
            },
            "answer": [
                {"question": 101, "value": "John"},
                {"question": 102, "value": ["male"]},
                {"question": 103, "value": 6212111},
                {"question": 104, "value": 2.0},
                {"question": 105, "value": [6.2088, 106.8456]},
                {
                    "question": 106,
                    "value": ["parent", "wife__husband__partner"]
                },
                {"question": 109, "value": 12},
            ],
        }
        response = self.client.put(
            url,
            data=payload,
            content_type="application/json",
            **{'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            data,
            {"message": "Draft updated successfully"}
        )

        # Verify the draft answers were updated
        updated_draft_data = FormData.objects_draft.get(id=self.draft_data.id)
        self.assertEqual(updated_draft_data.data_answer.count(), 7)
        for answer in updated_draft_data.data_answer.all():
            if answer.question.id == 101:
                self.assertEqual(answer.name, "John")
            elif answer.question.id == 102:
                self.assertEqual(answer.options, ["male"])
            elif answer.question.id == 103:
                self.assertEqual(answer.value, 6212111)
            elif answer.question.id == 104:
                self.assertEqual(answer.value, 2.0)
            elif answer.question.id == 105:
                self.assertEqual(answer.options, [6.2088, 106.8456])
            elif answer.question.id == 106:
                self.assertEqual(
                    answer.options,
                    ["parent", "wife__husband__partner"]
                )
            elif answer.question.id == 109:
                self.assertEqual(answer.value, 12)
