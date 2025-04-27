from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from django.test.utils import override_settings
from api.v1.v1_profile.constants import UserRoleTypes
from api.v1.v1_profile.models import Administration
from api.v1.v1_users.models import SystemUser, Organisation
from api.v1.v1_forms.constants import UserFormAccessTypes


@override_settings(USE_TZ=False)
class UpdateUserTestCase(TestCase):
    def setUp(self):
        call_command("administration_seeder", "--test")
        call_command("fake_organisation_seeder")
        call_command("form_seeder", "--test")
        user_payload = {"email": "admin@rush.com", "password": "Test105*"}
        user_response = self.client.post(
            "/api/v1/login",
            user_payload,
            content_type="application/json"
        )
        user = user_response.json()
        self.token = user.get("token")
        self.header = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        self.org = Organisation.objects.order_by("?").first()

    def test_remove_form_approver_access_assignment(self):
        # Create a user with approver access
        adm = Administration.objects.filter(
            level__level=1
        ).order_by("?").first()
        payload = {
            "first_name": "Admin",
            "last_name": "Approver",
            "email": "admin.approver@test.com",
            "administration": adm.id,
            "organisation": self.org.id,
            "role": UserRoleTypes.admin,
            "access_forms": [
                {
                    "form_id": 1,
                    "access_type": UserFormAccessTypes.read
                },
                {
                    "form_id": 1,
                    "access_type": UserFormAccessTypes.approver
                },
            ],
            "trained": True,
        }
        add_response = self.client.post(
            "/api/v1/user",
            payload,
            content_type="application/json",
            **self.header
        )
        self.assertEqual(add_response.status_code, 200)
        self.assertEqual(
            add_response.json(),
            {"message": "User added successfully"}
        )
        # Update the new user password
        new_user = SystemUser.objects.filter(
            email="admin.approver@test.com"
        ).first()
        new_user.set_password("Test#123")
        new_user.updated = timezone.now()
        new_user.date_joined = timezone.now()
        new_user.save()
        # Login with the new user
        user_payload = {
            "email": new_user.email,
            "password": "Test#123"
        }
        user_response = self.client.post(
            "/api/v1/login",
            user_payload,
            content_type="application/json"
        )
        user = user_response.json()
        # Check if the login was successful
        self.assertEqual(user_response.status_code, 200)

        # Update the user to remove approver access
        payload = {
            "first_name": "Admin",
            "last_name": "Editor",
            "email": "admin.approver@test.com",
            "administration": adm.id,
            "organisation": self.org.id,
            "role": UserRoleTypes.admin,
            "access_forms": [
                {
                    "form_id": 1,
                    "access_type": UserFormAccessTypes.read
                },
                {
                    "form_id": 1,
                    "access_type": UserFormAccessTypes.edit
                },
            ],
        }
        update_response = self.client.put(
            f"/api/v1/user/{new_user.id}",
            payload,
            content_type="application/json",
            **self.header
        )
        # Check if the update was successful
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(
            update_response.json(),
            {"message": "User updated successfully"}
        )
        # Check if the user has been updated
        user = SystemUser.objects.filter(
            email="admin.approver@test.com"
        ).first()
        self.assertEqual(user.first_name, "Admin")
        self.assertEqual(user.last_name, "Editor")

        # Check if the user no longer has approval assignment
        self.assertEqual(user.user_data_approval.count(), 0)

        # Check UserFomrAccess
        user_forms = user.user_form.all()
        self.assertEqual(len(user_forms), 1)
        user_form = user_forms.first()
        self.assertNotIn(
            UserFormAccessTypes.approver,
            [
                form_access.access_type
                for form_access in user_form.user_form_access.all()
            ]
        )
