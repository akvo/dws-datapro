# import pandas as pd
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from api.v1.v1_forms.models import Forms
from api.v1.v1_jobs.management.commands.generate_excel_data import (
    CRONJOB_RESULT_DIR,
)
from utils import storage


@override_settings(USE_TZ=False)
class JobGenerateExcelDataCommand(TestCase):
    def setUp(self):
        call_command("form_seeder", "--test")
        call_command("administration_seeder", "--test")
        user = {"email": "admin@akvo.org", "password": "Test105*"}
        user = self.client.post(
            "/api/v1/login", user, content_type="application/json"
        )
        call_command("fake_data_seeder", "-r", 2, "--test", True)

    def test_download_all_data(self):
        form = Forms.objects.get(pk=1)

        # Test download all data
        call_command(
            "generate_excel_data",
            form.id,
        )
        form_name = form.name.replace(" ", "_").lower()
        result_file = f"{CRONJOB_RESULT_DIR}/{form_name}-routine.xlsx"
        self.assertTrue(storage.check(result_file))
        storage.delete(result_file)

        call_command("generate_excel_data", form.id, "--latest", True)

        result_file = f"{CRONJOB_RESULT_DIR}/{form_name}-routine-latest.xlsx"
        # self.assertTrue(storage.check(result_file))

        # download_file = storage.download(result_file)
        # df = pd.read_excel(download_file)
        # self.assertTrue(df.shape[0])

        storage.delete(result_file)

    def call_generate_excel_data_use_label(self):
        form = Forms.objects.get(pk=1)
        call_command("generate_excel_data", form.id, "--use-label", True)
        form_name = form.name.replace(" ", "_").lower()
        result_file = f"{CRONJOB_RESULT_DIR}/{form_name}-routine.xlsx"
        self.assertTrue(storage.check(result_file))
        storage.delete(result_file)
