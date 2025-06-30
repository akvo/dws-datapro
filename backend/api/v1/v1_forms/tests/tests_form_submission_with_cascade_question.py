from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from api.v1.v1_forms.models import Forms
from api.v1.v1_users.models import Organisation
from api.v1.v1_profile.models import EntityData
from api.v1.v1_profile.tests.mixins import ProfileTestHelperMixin


@override_settings(USE_TZ=False)
class FormSubmissionWithCascadeTestCase(TestCase, ProfileTestHelperMixin):
    def setUp(self):
        call_command("administration_seeder", "--test")
        call_command("fake_organisation_seeder", "--repeat", 3)
        call_command("entities_seeder", "--repeat", 6, "--test", True)
        call_command("form_seeder", "--test")

        user = self.create_user(
            email="super@akvo.org",
            role_level=self.IS_SUPER_ADMIN,
        )
        user.set_password("password")
        user.save()

        token = self.get_auth_token(user.email, "password")
        self.header = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        self.org = Organisation.objects.order_by('?').first()
        self.form = Forms.objects.get(pk=5)

        self.school = EntityData.objects.filter(
            entity__name="School"
        ).order_by("?").first()
        self.administration = self.school.administration

    def test_success_create_new_submission(self):
        payload = {
            "data": {
                "name": "Testing Data",
                "administration": self.administration.id,
                "geo": [6.2088, 106.8456]
            },
            "answer": [{
                "question": 501,
                "value": self.administration.id
            }, {
                "question": 502,
                "value": self.school.id
            }, {
                "question": 503,
                "value": [6.2088, 106.8456]
            }, {
                "question": 504,
                "value": self.org.id
            }]
        }

        response = self.client.post(
            f"/api/v1/form-data/{self.form.id}",
            data=payload,
            content_type='application/json',
            **self.header
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(
            response_data,
            {
                "message": "ok"
            }
        )
