from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from rest_framework_simplejwt.tokens import RefreshToken

from api.v1.v1_profile.tests.mixins import ProfileTestHelperMixin
from api.v1.v1_data.models import FormData
from api.v1.v1_forms.models import Forms
from api.v1.v1_profile.models import Administration


@override_settings(USE_TZ=False)
class PendingDataTestCase(TestCase, ProfileTestHelperMixin):
    def setUp(self) -> None:
        call_command("administration_seeder", "--test")
        call_command("form_seeder", "--test")
        call_command("demo_approval_flow", "--test", True)

        # get administration that have approval flow
        parent_adm = Administration.objects.filter(
            administration_data_approval__isnull=False,
            parent_administration__gt=0
        ).first()
        self.administration = parent_adm.parent_administration.first()
        user = self.create_user(
            email="john.pending@test.com",
            role_level=self.IS_ADMIN,
            administration=self.administration,
        )
        t = RefreshToken.for_user(user)
        self.token = t.access_token
        self.form = Forms.objects.get(pk=1)

        # Create a pending registration data point
        payload = {
            "data": {
                "name": "Registration Data #1",
                "administration": self.administration.id,
                "geo": [6.2088, 106.8456],
            },
            "answer": [
                {"question": 101, "value": "John Doe"},
                {"question": 102, "value": ["Male"]},
                {"question": 103, "value": 621231},
                {"question": 104, "value": 2.0},
                {"question": 105, "value": [6.2088, 106.8456]},
                {"question": 106, "value": ["parent"]},
                {"question": 109, "value": 11},
            ],
        }
        self.client.post(
            f"/api/v1/form-pending-data/{self.form.id}",
            payload,
            content_type="application/json",
            **{"HTTP_AUTHORIZATION": f"Bearer {self.token}"},
        )
        self.datapoint = FormData.objects.filter(
            form=self.form, name="Registration Data #1", is_pending=True
        ).first()

    def test_pending_registration_data_details(self):
        self.assertIsNotNone(self.datapoint)
        res = self.client.get(
            f"/api/v1/pending-data/{self.datapoint.id}",
            content_type="application/json",
            **{"HTTP_AUTHORIZATION": f"Bearer {self.token}"},
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json(),
            [
                {
                    "history": None,
                    "question": 101,
                    "value": "John Doe",
                    "last_value": None,
                    "index": 0,
                },
                {
                    "history": None,
                    "question": 102,
                    "value": ["Male"],
                    "last_value": None,
                    "index": 0,
                },
                {
                    "history": None,
                    "question": 103,
                    "value": 621231.0,
                    "last_value": None,
                    "index": 0,
                },
                {
                    "history": None,
                    "question": 104,
                    "value": 2,
                    "last_value": None,
                    "index": 0,
                },
                {
                    "history": None,
                    "question": 105,
                    "value": [6.2088, 106.8456],
                    "last_value": None,
                    "index": 0,
                },
                {
                    "history": None,
                    "question": 106,
                    "value": ["parent"],
                    "last_value": None,
                    "index": 0,
                },
                {
                    "history": None,
                    "question": 109,
                    "value": 11.0,
                    "last_value": None,
                    "index": 0,
                },
            ],
        )

    def test_first_pending_monitoring_data_details(self):
        """
        Test the first pending monitoring data details endpoint.
        """
        self.assertIsNotNone(self.datapoint)
        # Update the registration data to be approved
        self.datapoint.is_pending = False
        self.datapoint.save()

        # Create a new monitoring data point
        payload = {
            "data": {
                "name": "Monitoring Data #1",
                "administration": self.administration.id,
                "geo": [6.2088, 106.8456],
                "uuid": self.datapoint.uuid,
            },
            "answer": [
                {"question": 10103, "value": 621234},
                {"question": 10106, "value": ["parent", "children"]},
                {"question": 10109, "value": 8.1},
            ],
        }
        monitoring_form = self.form.children.first()
        data = self.client.post(
            f"/api/v1/form-pending-data/{monitoring_form.id}",
            payload,
            content_type="application/json",
            **{"HTTP_AUTHORIZATION": f"Bearer {self.token}"},
        )
        self.assertEqual(data.status_code, 200)
        datapoint = FormData.objects.filter(
            form=monitoring_form, name="Monitoring Data #1", is_pending=True
        ).first()
        self.assertIsNotNone(datapoint)
        res = self.client.get(
            f"/api/v1/pending-data/{datapoint.id}",
            content_type="application/json",
            **{"HTTP_AUTHORIZATION": f"Bearer {self.token}"},
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json(),
            [
                {
                    "history": None,
                    "question": 10103,
                    "value": 621234.0,
                    "last_value": 621231.0,
                    "index": 0,
                },
                {
                    "history": None,
                    "question": 10106,
                    "value": ["parent", "children"],
                    "last_value": ["parent"],
                    "index": 0,
                },
                {
                    "history": None,
                    "question": 10109,
                    "value": 8.1,
                    "last_value": 11.0,
                    "index": 0,
                },
            ],
        )

    def test_second_pending_monitoring_data_details(self):
        """
        Test the second pending monitoring data details endpoint.
        """
        self.assertIsNotNone(self.datapoint)
        # Update the registration data to be approved
        self.datapoint.is_pending = False
        self.datapoint.save()
        # Create a new monitoring data point
        payload = {
            "data": {
                "name": "Monitoring Data #2",
                "administration": self.administration.id,
                "geo": [6.2088, 106.8456],
                "uuid": self.datapoint.uuid,
            },
            "answer": [
                {"question": 10103, "value": 621235},
                {"question": 10106, "value": ["parent", "children"]},
                {"question": 10109, "value": 9.5},
            ],
        }
        monitoring_form = self.form.children.first()
        data = self.client.post(
            f"/api/v1/form-pending-data/{monitoring_form.id}",
            payload,
            content_type="application/json",
            **{"HTTP_AUTHORIZATION": f"Bearer {self.token}"},
        )
        self.assertEqual(data.status_code, 200)
        dp1 = FormData.objects.filter(
            form=monitoring_form, name="Monitoring Data #2", is_pending=True
        ).first()
        self.assertIsNotNone(dp1)
        # Approve the first monitoring data point
        dp1.is_pending = False
        dp1.save()

        self.datapoint.refresh_from_db()

        # Add more new monitoring data point
        payload = {
            "data": {
                "name": "Monitoring Data #3",
                "administration": self.administration.id,
                "geo": [6.2088, 106.8456],
                "uuid": self.datapoint.uuid,
            },
            "answer": [
                {"question": 10103, "value": 621236},
                {"question": 10106, "value": ["parent", "children"]},
                {"question": 10109, "value": 10.0},
            ],
        }
        data = self.client.post(
            f"/api/v1/form-pending-data/{monitoring_form.id}",
            payload,
            content_type="application/json",
            **{"HTTP_AUTHORIZATION": f"Bearer {self.token}"},
        )
        self.assertEqual(data.status_code, 200)
        datapoint2 = FormData.objects.filter(
            form=monitoring_form, name="Monitoring Data #3", is_pending=True
        ).first()
        self.assertIsNotNone(datapoint2)
        res = self.client.get(
            f"/api/v1/pending-data/{datapoint2.id}",
            content_type="application/json",
            **{"HTTP_AUTHORIZATION": f"Bearer {self.token}"},
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json(),
            [
                {
                    "history": None,
                    "question": 10103,
                    "value": 621236.0,
                    "last_value": 621235.0,
                    "index": 0,
                },
                {
                    "history": None,
                    "question": 10106,
                    "value": ["parent", "children"],
                    "last_value": ["parent", "children"],
                    "index": 0,
                },
                {
                    "history": None,
                    "question": 10109,
                    "value": 10.0,
                    "last_value": 9.5,
                    "index": 0,
                },
            ],
        )

    def test_pending_data_details_with_invalid_id(self):
        """
        Test the pending data details endpoint with an invalid ID.
        """
        res = self.client.get(
            "/api/v1/pending-data/999999",
            content_type="application/json",
            **{"HTTP_AUTHORIZATION": f"Bearer {self.token}"},
        )
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json(), {"detail": "Not found."})
