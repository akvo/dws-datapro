from django.test import TestCase
from django.core.management import call_command
from api.v1.v1_users.models import SystemUser
from api.v1.v1_data.models import FormData
from api.v1.v1_forms.models import Forms, UserForms
from api.v1.v1_forms.constants import FormAccessTypes
from api.v1.v1_profile.models import Administration, Access
from api.v1.v1_profile.constants import UserRoleTypes
from api.v1.v1_data.management.commands.fake_data_seeder import (
    add_fake_answers
)


class MonitoringDataTestCase(TestCase):
    def setUp(self):
        call_command('administration_seeder', '--test')
        call_command('form_seeder', '--test')
        self.user = SystemUser.objects.create_user(
            email='test@test.org',
            password='test1234',
            first_name='test',
            last_name='testing',
        )
        self.administration = Administration.objects.filter(
            level__level=1
        ).first()
        role = UserRoleTypes.admin
        self.user_access = Access.objects.create(
            user=self.user, role=role, administration=self.administration
        )
        self.uuid = '1234567890'
        form = Forms.objects.get(pk=1)
        user_form = UserForms.objects.create(
            user=self.user,
            form=form,
        )
        user_form.user_form_access.create(
            access_type=FormAccessTypes.approve
        )
        self.user_form = user_form.user_form_access.create(
            access_type=FormAccessTypes.edit
        )

        self.form = form
        self.child_form = self.form.children.first()
        self.adm_data = Administration.objects.filter(
            level__level=2,
            path__startswith=self.administration.path
        ).first()
        self.data = FormData.objects.create(
            parent=None,
            uuid=self.uuid,
            form=self.form,
            administration=self.adm_data,
            created_by=self.user,
        )
        add_fake_answers(self.data)
        # Seed monitoring data
        call_command(
            "fake_data_monitoring_seeder", "-r", 2, "-t", True, "-a", True
        )

        # Login as an admin
        admin = {"email": self.user.email, "password": 'test1234'}
        admin = self.client.post(
            '/api/v1/login',
            admin,
            content_type='application/json'
        )
        admin = admin.json()
        self.token = admin.get("token")

    def test_parent_data(self):
        data = self.client.get(
            f"/api/v1/form-data/{self.form.id}",
            content_type='application/json',
            **{'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        )
        self.assertEqual(data.status_code, 200)
        data = data.json()
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['data'][0]['uuid'], self.uuid)

    def test_update_parent_data(self):
        payload = [
            {
                "question": 101,
                "value": "Edit"
            }
        ]
        edit = self.client.put(
            f'/api/v1/form-data/{self.form.id}?data_id={self.data.id}',
            payload,
            content_type='application/json',
            **{'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        )
        self.assertEqual(edit.status_code, 200)

        data = self.client.get(
            f"/api/v1/form-data/{self.form.id}",
            content_type='application/json',
            **{'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        )
        self.assertEqual(data.status_code, 200)
        data = data.json()
        self.assertEqual(data['total'], 1)

        answers = self.client.get(
            f'/api/v1/data/{self.data.id}',
            content_type='application/json',
            **{'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        )
        self.assertEqual(answers.status_code, 200)
        answers = answers.json()
        find_answer = list(filter(lambda a: a['question'] == 101, answers))
        self.assertEqual(len(find_answer), 1)
        self.assertNotEqual(find_answer[0]['history'], None)
        self.assertEqual(find_answer[0]['value'], 'Edit')

    def test_add_new_monitoring(self):
        monitoring = FormData.objects.create(
            uuid=self.uuid,
            form=self.child_form,
            administration=self.administration,
            created_by=self.user,
        )
        add_fake_answers(monitoring)

        data = self.client.get(
            f"/api/v1/form-data/{self.form.id}",
            content_type='application/json',
            **{'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        )
        self.assertEqual(data.status_code, 200)
        data = data.json()
        self.assertEqual(data['total'], 1)
        api_url = f"/api/v1/form-data/{self.child_form.id}"
        api_url += f"?parent={monitoring.uuid}"
        data_parent = self.client.get(
            api_url,
            content_type='application/json',
            **{'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        )
        self.assertEqual(data_parent.status_code, 200)
        data_parent = data_parent.json()
        self.assertEqual(data_parent['total'], 3)

        self.assertEqual(data_parent['data'][0]['name'], monitoring.name)

    def test_monitoring_details_by_parent_uuid(self):
        header = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

        parent = FormData.objects.filter(
            children__gt=0,
        ).first()
        # Get the monitoring data by parent UUID and form children ID
        form_id = parent.form.children.first().id
        url = f"/api/v1/form-data/{form_id}"
        url += f"?page=1&parent={parent.uuid}"
        data = self.client.get(url, follow=True, **header)
        result = data.json()
        self.assertEqual(data.status_code, 200)
        self.assertEqual(
            list(result), ["current", "total", "total_page", "data"]
        )
        self.assertEqual(result["total"], parent.children.count())
