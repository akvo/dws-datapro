from django.test import TestCase
from api.v1.v1_forms.models import Forms
from api.v1.v1_users.models import SystemUser
from api.v1.v1_profile.tests.mixins import ProfileTestHelperMixin
from api.v1.v1_profile.constants import DataAccessTypes
from api.v1.v1_data.models import FormData
from django.core.management import call_command
from rest_framework import status
from utils.custom_helper import CustomPasscode


class CreateBatchMonitoringDataTest(TestCase, ProfileTestHelperMixin):

    def setUp(self):
        call_command("administration_seeder", "--test")
        call_command("form_seeder", "--test")
        call_command("default_roles_seeder", "--test", 1)
        call_command("fake_user_seeder", "--repeat", 5, "--test", 1)

        self.form = Forms.objects.get(pk=1)
        ds = DataAccessTypes.submit
        user = SystemUser.objects.filter(
            user_user_role__administration__level__level=3,
            user_user_role__role__role_role_access__data_access=ds,
        ).first()

        self.administration = user.user_user_role.filter(
            role__role_role_access__data_access=ds,
        ).first().administration

        # Create approver based on the user's administration
        self.create_user(
            email="approver.123@test.com",
            role_level=self.IS_APPROVER,
            administration=self.administration,
            form=self.form,
        )

        # Create a mobile assignment for the user
        mobile_user = user.mobile_assignments.create(
            name="Test mobile",
            passcode=CustomPasscode().encode("123456"),
        )
        # Assign administration to the mobile assignment
        mobile_user.administrations.add(self.administration)
        # Assign form to the mobile assignment
        mobile_user.forms.add(self.form)

        self.mobile_user = mobile_user
        self.code = CustomPasscode().decode(
            encoded_passcode=self.mobile_user.passcode
        )
        res = self.client.post(
            "/api/v1/device/auth",
            {"code": self.code},
            content_type="application/json",
        )
        data = res.json()
        mobile_token = data["syncToken"]

        self.registration_uuid = "a191e3c6-395d-4728-821a-09b13d1e0869"

        user.set_password("test")
        user.save()

        self.token = self.get_auth_token(user.email, "test")

        reg_adm = self.administration.parent_administration.first()
        reg_geo = [-121.8863, 37.3382]

        payload = {
            "formId": self.form.id,
            "name": "Registration #1",
            "duration": 2000,
            "submittedAt": "2021-01-01T00:00:00.000Z",
            "geo": reg_geo,
            "uuid": self.registration_uuid,
            "answers": {
                101: "John Doe",
                102: ["male"],
                103: 6129912345,
                104: reg_adm.id,
                105: reg_geo,
                106: ["parent", "children"],
                107: "http://example.com/image.jpg",
                108: "2025-07-01T00:00:00.000Z",
                114: ["no"],
            },
        }

        response = self.client.post(
            "/api/v1/device/sync",
            payload,
            content_type="application/json",
            **{"HTTP_AUTHORIZATION": f"Bearer {mobile_token}"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Submit the monitoring data
        monitoring_form = self.form.children.first()
        payload = {
            "formId": monitoring_form.id,
            "name": "Monitoring #1",
            "duration": 1500,
            "submittedAt": "2021-01-01T00:00:00.000Z",
            "geo": [0, 0],
            "uuid": self.registration_uuid,
            "answers": {
                10103: "6129912111",
                10106: ["parent", "wife__husband__partner"],
                10109: 99.1,
            }
        }

        response = self.client.post(
            "/api/v1/device/sync",
            payload,
            content_type="application/json",
            **{"HTTP_AUTHORIZATION": f"Bearer {mobile_token}"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.dp1 = FormData.objects.filter(
            form=self.form,
            created_by=user,
            uuid=self.registration_uuid,
        ).first()

        self.dp2 = FormData.objects.filter(
            form=monitoring_form,
            created_by=user,
            uuid=self.registration_uuid,
        ).first()

    def test_create_batch_with_registration_and_monitoring_data(self):
        data = {
            "name": "Batch Monitoring Data",
            "description": "This is a test batch for monitoring data",
            "data": [
                self.dp1.id,
                self.dp2.id,
            ],
            "files": [],
        }

        response = self.client.post(
            "/api/v1/batch",
            data=data,
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json(),
            {"message": "Batch created successfully"}
        )

    def test_create_batch_only_monitoring_data(self):
        # Attempt to create a batch without including the registration data
        data = {
            "name": "Batch Monitoring Data Without Registration",
            "description": (
                "This is a test batch for monitoring data without registration"
            ),
            "data": [self.dp2.id],  # Only include monitoring data
            "files": [],
        }

        response = self.client.post(
            "/api/v1/batch",
            data=data,
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        batch = response.json()
        self.assertIn("detail", batch)
        self.assertEqual(
            batch["detail"]["data"],
            [(
                "Registration data must be included "
                "in the batch if it is pending."
            )]
        )

    def test_create_batch_registration_first_then_monitoring_data(self):
        # Create a batch with registration only
        data = {
            "name": "Batch Registration Data",
            "description": "This is a test batch for registration data",
            "data": [self.dp1.id],  # Only include registration data
            "files": [],
        }
        response = self.client.post(
            "/api/v1/batch",
            data=data,
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Now create a batch with monitoring data
        data = {
            "name": "Batch Monitoring Data",
            "description": "This is a test batch for monitoring data",
            "data": [self.dp2.id],  # Only include monitoring data
            "files": [],
        }
        response = self.client.post(
            "/api/v1/batch",
            data=data,
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        batch = response.json()
        self.assertIn("detail", batch)
        self.assertEqual(
            batch["detail"]["data"],
            [(
                "Registration data must be included "
                "in the batch if it is pending."
            )]
        )
