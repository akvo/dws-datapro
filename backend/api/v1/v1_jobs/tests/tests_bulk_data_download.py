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
                "0_code": "ID",
                "0_National": "Indonesia",
                "1_code": "ID-JK",
                "1_Province": "Jakarta",
                "2_code": "ID-JK-JKE",
                "2_District": "East Jakarta",
                "3_code": "ID-JK-JKE-KJ",
                "3_Subdistrict": "Kramat Jati",
                "4_code": "ID-JK-JKE-KJ-CW",
                "4_Village": "Cawang",
            },
            {
                "0_code": "ID",
                "0_National": "Indonesia",
                "1_code": "ID-JK",
                "1_Province": "Jakarta",
                "2_code": "ID-JK-JKW",
                "2_District": "West Jakarta",
                "3_code": "ID-JK-JKW-KJ",
                "3_Subdistrict": "Kebon Jeruk",
                "4_code": "ID-JK-JKW-KJ-KJ",
                "4_Village": "Kebon Jeruk",
            },
            {
                "0_code": "ID",
                "0_National": "Indonesia",
                "1_code": "ID-YO",
                "1_Province": "Yogyakarta",
                "2_code": "ID-YO-SL",
                "2_District": "Sleman",
                "3_code": "ID-YO-SL-ST",
                "3_Subdistrict": "Seturan",
                "4_code": "ID-YO-SL-ST-CB",
                "4_Village": "Cepit Baru",
            },
            {
                "0_code": "ID",
                "0_National": "Indonesia",
                "1_code": "ID-YO",
                "1_Province": "Yogyakarta",
                "2_code": "ID-YO-BT",
                "2_District": "Bantul",
                "3_code": "ID-YO-BT-BT",
                "3_Subdistrict": "Bantul",
                "4_code": "ID-YO-BT-BT-BT",
                "4_Village": "Bantul",
            },
        ]
        administration_seeder.seed_administration_test(rows=rows)
        call_command("demo_approval_flow", "--test", True)
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
