from django.test import TestCase
from django.core.management import call_command
from api.v1.v1_users.models import SystemUser
from api.v1.v1_data.models import (
    FormData,
    PendingDataBatch
)
from api.v1.v1_forms.models import Forms
from api.v1.v1_profile.models import Administration, Access
from api.v1.v1_profile.constants import UserRoleTypes
from api.v1.v1_data.tasks import seed_approved_data
from api.v1.v1_data.functions import add_fake_answers


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
            parent__isnull=True
        ).first()
        role = UserRoleTypes.admin
        self.user_access = Access.objects.create(
            user=self.user, role=role, administration=self.administration
        )
        self.uuid = '1234567890'
        self.form = Forms.objects.get(pk=1)
        self.data = FormData.objects.create(
            parent=None,
            uuid=self.uuid,
            form=self.form,
            administration=self.administration,
            created_by=self.user,
        )
        add_fake_answers(self.data)

    def test_parent_data(self):
        self.assertTrue(self.data.name)
        self.assertEqual(self.data.parent, None)
        self.assertEqual(self.data.uuid, self.uuid)
        self.assertEqual(self.data.form, self.form)
        self.assertEqual(self.data.administration, self.administration)
        self.assertEqual(self.data.created_by, self.user)
        self.assertTrue(self.data.data_answer.count() > 0)

    def test_seed_monitoring_batch(self):
        for i in range(2):
            child_form = self.form.children.first()
            pending_data = FormData.objects.create(
                parent=self.data,
                uuid=self.uuid,
                form=child_form,
                name=f'Child Data {i + 1}',
                administration=self.administration,
                created_by=self.user,
                is_pending=True
            )
            add_fake_answers(pending_data)
        self.assertTrue(FormData.objects.filter(is_pending=True).count() == 2)
        batch = PendingDataBatch.objects.create(
            name='test batch',
            administration=self.administration,
            form=self.form,
            user=self.user,
            approved=True
        )
        batch.batch_form_data.add(*FormData.objects.filter(is_pending=True))
        self.assertTrue(batch.batch_form_data.count() == 2)
        for pending_data in batch.batch_form_data.all():
            seed_approved_data(pending_data)
        self.assertTrue(FormData.objects.count() == 3)
        child_data = self.data.children.all()
        first_child = child_data.first()
        self.assertEqual(first_child.parent.uuid, self.uuid)
        self.assertEqual(self.data.children.first().id, first_child.id)
        self.assertEqual(self.data.children.count(), 2)
