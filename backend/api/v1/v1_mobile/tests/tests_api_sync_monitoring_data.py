from django.test import TestCase
from api.v1.v1_forms.models import Forms
from api.v1.v1_users.models import SystemUser
from api.v1.v1_profile.tests.mixins import ProfileTestHelperMixin
from api.v1.v1_profile.constants import DataAccessTypes
from django.core.management import call_command
from rest_framework import status
from utils.custom_helper import CustomPasscode


class MobileApiSyncMonitoringDataTest(TestCase, ProfileTestHelperMixin):

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
        self.mobile_token = data["syncToken"]

        self.registration_uuid = "a191e3c6-395d-4728-821a-09b13d1e0869"

        user.set_password("test")
        user.save()

        self.user_token = self.get_auth_token(user.email, "test")

    def test_sync_both_registration_and_monitoring_data(self):
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
            **{"HTTP_AUTHORIZATION": f"Bearer {self.mobile_token}"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that in the pending form data list via API
        response = self.client.get(
            f"/api/v1/form-pending-data/{self.form.id}",
            content_type="application/json",
            **{"HTTP_AUTHORIZATION": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["total"], 1)

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
            **{"HTTP_AUTHORIZATION": f"Bearer {self.mobile_token}"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the monitoring data is in the pending form data list
        response = self.client.get(
            f"/api/v1/form-pending-data/{self.form.id}",
            content_type="application/json",
            **{"HTTP_AUTHORIZATION": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["total"], 2)

        monitoring_data = list(filter(
            lambda x: x["name"] == "Monitoring #1",
            response.json()["data"],
        ))

        # Administration should be set to the parent administration
        self.assertEqual(
            monitoring_data[0]["administration"],
            reg_adm.name,
        )
        # Geo should be set to the parent administration's geo
        self.assertEqual(
            monitoring_data[0]["geo"],
            reg_geo,
        )
