from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from api.v1.v1_forms.models import Forms
from api.v1.v1_jobs.models import Jobs
from api.v1.v1_jobs.job import (
    job_generate_data_download,
)
from api.v1.v1_users.models import SystemUser
from api.v1.v1_profile.models import Administration
from api.v1.v1_profile.functions import get_max_administration_level


@override_settings(USE_TZ=False)
class JobDownloadUnitTestCase(TestCase):
    def setUp(self):
        call_command("form_seeder", "--test")
        call_command("administration_seeder", "--test")
        call_command("default_roles_seeder", "--test", 1)
        user = {"email": "admin@akvo.org", "password": "Test105*"}
        user = self.client.post('/api/v1/login',
                                user,
                                content_type='application/json')

    def test_download_all_data(self):
        form = Forms.objects.get(pk=1)
        admin = SystemUser.objects.first()
        result = call_command(
            "job_download",
            form.id,
            admin.id,
            "-a",
            0,
            "-t",
            "all",
        )
        self.assertTrue(result)

        job = Jobs.objects.get(pk=result)
        self.assertEqual(job.info.get("download_type"), "all")

        url = job_generate_data_download(job_id=job.id, **job.info)
        self.assertTrue("download-test_form" in url)

    def test_download_recent_data_with_administration(self):
        form = Forms.objects.get(pk=1)
        admin = SystemUser.objects.first()

        max_level = get_max_administration_level()
        ward = Administration.objects.filter(
            level__level=max_level - 1,
        ).order_by("?").first()

        result = call_command(
            "job_download",
            form.id,
            admin.id,
            "-a",
            ward.id,
            "-t",
            "recent",
        )
        self.assertTrue(result)

        job = Jobs.objects.get(pk=result)
        self.assertEqual(job.info.get("download_type"), "recent")
        self.assertEqual(job.info.get("administration"), ward.id)

        url = job_generate_data_download(job_id=job.id, **job.info)
        self.assertTrue("download-test_form" in url)
