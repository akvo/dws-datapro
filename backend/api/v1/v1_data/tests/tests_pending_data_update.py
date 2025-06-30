from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from api.v1.v1_data.models import FormData, AnswerHistory
from api.v1.v1_forms.models import Forms
from api.v1.v1_profile.constants import DataAccessTypes
from api.v1.v1_profile.tests.mixins import ProfileTestHelperMixin
from api.v1.v1_data.functions import add_fake_answers


@override_settings(USE_TZ=False)
class PendingDataUpdateTestCase(TestCase, ProfileTestHelperMixin):

    def setUp(self):
        call_command("administration_seeder", "--test")
        call_command("default_roles_seeder", "--test", 1)
        call_command("form_seeder", "--test")
        call_command(
            "fake_data_monitoring_seeder",
            repeat=10,
            test=True,
            approved=False,
        )
        self.parent_form = Forms.objects.get(pk=1)
        self.form = self.parent_form.children.first()
        data = FormData.objects.filter(
            form__pk=self.form.id,
            is_pending=True,
        ).order_by("?").all()

        self.data = data.last()

        self.submitter = self.data.created_by
        self.submitter.set_password("test")
        self.submitter.save()

        self.administration = self.submitter.user_user_role.filter(
            role__role_role_access__data_access=DataAccessTypes.submit
        ).first().administration

        self.token = self.get_auth_token(self.submitter.email, "test")

    def test_update_pending_monitoring_data(self):
        payload = [
            {
                "value": "+62121111",
                "question": 10103,
            },
            {
                "value": [
                    "wife__husband__partner",
                    "children"
                ],
                "question": 10106,
            },
            {
                "value": 99.9,
                "question": 10109,
            }
        ]
        response = self.client.put(
            (
                f"/api/v1/form-pending-data/{self.form.id}/"
                f"?pending_data_id={self.data.id}"
            ),
            data=payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)
        self.assertEqual(
            response.data["message"],
            "update success",
        )

        # Verify that the answers were updated
        updated_data = FormData.objects.get(id=self.data.id)
        self.assertEqual(
            updated_data.data_answer.filter(
                question__id=10103
            ).first().name,
            "+62121111"
        )
        self.assertEqual(
            updated_data.data_answer.filter(
                question__id=10106
            ).first().options,
            ["wife__husband__partner", "children"]
        )
        self.assertEqual(
            updated_data.data_answer.filter(
                question__id=10109
            ).first().value,
            99.9
        )

        # Verify that previous answers stored in AnswerHistory
        self.assertTrue(
            AnswerHistory.objects.filter(
                data_id=updated_data.id,
                question__id=10103,
            ).exists()
        )

    def test_update_pending_registration_data(self):
        registration_data = FormData.objects.create(
            name="Test Registration Data",
            form=self.parent_form,
            created_by=self.submitter,
            administration=self.administration,
            geo=[7.2088, 126.8456],
            is_pending=True,
        )
        add_fake_answers(registration_data)

        payload = [
            {
                "value": ["female"],
                "question": 102,
            },
            {
                "value": [-11.123456, 34.567890],
                "question": 105,
            },
            {
                "value": "/images/question_107.jpg",
                "question": 107,
            }
        ]
        response = self.client.put(
            (
                f"/api/v1/form-pending-data/{self.parent_form.id}/"
                f"?pending_data_id={registration_data.id}"
            ),
            data=payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)
        self.assertEqual(
            response.data["message"],
            "update success",
        )

        # Verify that the answers were updated
        updated_data = FormData.objects.get(id=registration_data.id)
        self.assertEqual(
            updated_data.data_answer.filter(
                question__id=102
            ).first().options,
            ["female"]
        )
        self.assertEqual(
            updated_data.data_answer.filter(
                question__id=105
            ).first().options,
            [-11.123456, 34.567890]
        )
        self.assertEqual(
            updated_data.data_answer.filter(
                question__id=107
            ).first().name,
            "/images/question_107.jpg"
        )

    def test_update_pending_data_invalid_form_id(self):
        payload = [
            {
                "value": "+62121111",
                "question": 10103,
            }
        ]
        response = self.client.put(
            "/api/v1/form-pending-data/9999/?pending_data_id=1",
            data=payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 404)

    def test_update_pending_data_invalid_data_id(self):
        payload = [
            {
                "value": "+62121111",
                "question": 10103,
            }
        ]
        response = self.client.put(
            f"/api/v1/form-pending-data/{self.form.id}/?pending_data_id=9999",
            data=payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 404)
