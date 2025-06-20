import pandas as pd
import os
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from api.v1.v1_forms.models import Questions, Forms
from api.v1.v1_data.models import FormData
from api.v1.v1_jobs.job import download_data, generate_definition_sheet
from api.v1.v1_profile.management.commands import administration_seeder


@override_settings(USE_TZ=False)
class BulkUnitTestCase(TestCase):
    def setUp(self):
        call_command("form_seeder", "--test")
        rows = [
            {
                "code_0": "ID",
                "National_0": "Indonesia",
                "code_1": "ID-JK",
                "Province_1": "Jakarta",
                "code_2": "ID-JK-JKE",
                "District_2": "East Jakarta",
                "code_3": "ID-JK-JKE-KJ",
                "Subdistrict_3": "Kramat Jati",
                "code_4": "ID-JK-JKE-KJ-CW",
                "Village_4": "Cawang",
            },
            {
                "code_0": "ID",
                "National_0": "Indonesia",
                "code_1": "ID-JK",
                "Province_1": "Jakarta",
                "code_2": "ID-JK-JKW",
                "District_2": "West Jakarta",
                "code_3": "ID-JK-JKW-KJ",
                "Subdistrict_3": "Kebon Jeruk",
                "code_4": "ID-JK-JKW-KJ-KJ",
                "Village_4": "Kebon Jeruk",
            },
            {
                "code_0": "ID",
                "National_0": "Indonesia",
                "code_1": "ID-YO",
                "Province_1": "Yogyakarta",
                "code_2": "ID-YO-SL",
                "District_2": "Sleman",
                "code_3": "ID-YO-SL-ST",
                "Subdistrict_3": "Seturan",
                "code_4": "ID-YO-SL-ST-CB",
                "Village_4": "Cepit Baru",
            },
            {
                "code_0": "ID",
                "National_0": "Indonesia",
                "code_1": "ID-YO",
                "Province_1": "Yogyakarta",
                "code_2": "ID-YO-BT",
                "District_2": "Bantul",
                "code_3": "ID-YO-BT-BT",
                "Subdistrict_3": "Bantul",
                "code_4": "ID-YO-BT-BT-BT",
                "Village_4": "Bantul",
            },
        ]
        administration_seeder.seed_administration_test(rows=rows)
        # Seed default roles after administration seeder
        call_command("default_roles_seeder", "--test", 1)

        user = {"email": "admin@akvo.org", "password": "Test105*"}
        user = self.client.post('/api/v1/login',
                                user,
                                content_type='application/json')
        call_command("fake_data_seeder", "-r", 2, "--test", True)

    def test_data_download_list_of_columns(self):
        form_data = FormData.objects.count()
        self.assertTrue(form_data)
        form_data = FormData.objects.first()
        administration = form_data.administration
        download_response = download_data(form_data.form, [administration.id])
        self.assertTrue(download_response)
        download_columns = list(download_response[0].keys())
        questions = Questions.objects.filter(form=form_data.form).values_list(
            "name", flat=True)
        meta_columns = ["id", "created_at", "created_by", "updated_at",
                        "updated_by", "datapoint_name", "administration",
                        "geolocation"]
        columns = list(
            filter(lambda x: x not in meta_columns, download_columns)
        )
        self.assertEqual(list(columns).sort(), list(questions).sort())

        # test if the download recent data is successful
        download_response = download_data(
            form_data.form,
            [administration.id],
            "recent")
        self.assertTrue(download_response)

    def test_generate_definition_sheet(self):
        form = Forms.objects.first()
        writer = pd.ExcelWriter("test.xlsx", engine='xlsxwriter')
        generate_definition_sheet(form=form, writer=writer)
        writer.save()
        # test if excel has been created
        self.assertTrue(os.path.exists("test.xlsx"))
        os.remove("test.xlsx")
