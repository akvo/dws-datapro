import typing
from django.test import TestCase
from django.http import HttpResponse
from django.test.utils import override_settings
from api.v1.v1_profile.management.commands import administration_seeder
from api.v1.v1_profile.models import Administration


@override_settings(USE_TZ=False)
class UpdateAdministrationPathTestCase(TestCase):

    def setUp(self):
        super().setUp()
        rows = [
            {
                "0_code": "ID",
                "0_National": "Indonesia",
                "1_code": "ID-JK",
                "1_Provinsi": "Jakarta/DKI Jakarta",
                "2_code": "ID-JKE",
                "2_Kabupaten": "East Jakarta",
                "3_code": "ID-JKE-KJ",
                "3_Kecamatan": "Kramat Djati",
                "4_code": "ID-JKE-KJ-CW",
                "4_Kelurahan": "Cawang",
            },
            {
                "0_code": "ID",
                "0_National": "Indonesia",
                "1_code": "ID-JK",
                "1_Provinsi": "Jakarta",
                "2_code": "ID-JKE",
                "2_Kabupaten": "East-Jakarta",
                "3_code": "ID-JKE-KJ",
                "3_Kecamatan": "Kramat Jati",
                "4_code": "ID-JKE-KJ-BK",
                "4_Kelurahan": "Balekambang",
            },
            {
                "0_code": "ID",
                "0_National": "Indonesia",
                "1_code": "ID-YGK",
                "1_Provinsi": "Yogyakarta",
                "2_code": "ID-YGK-SL",
                "2_Kabupaten": "Sleman",
                "3_code": "ID-YGK-SL-SET",
                "3_Kecamatan": "Seturan",
                "4_code": "ID-YGK-SL-SET-CP",
                "4_Kelurahan": "Cepit Baru",
            },
        ]
        geo_config = [
            {"id": 1, "level": 0, "name": "NAME_0", "alias": "National"},
            {"id": 2, "level": 1, "name": "NAME_1", "alias": "Provinsi"},
            {"id": 3, "level": 2, "name": "NAME_1", "alias": "Kabupaten"},
            {"id": 4, "level": 3, "name": "NAME_2", "alias": "Kecamatan"},
            {"id": 5, "level": 4, "name": "NAME_3", "alias": "Kelurahan"},
        ]
        administration_seeder.seed_administration_test(
            rows=rows,
            geo_config=geo_config
        )

        user_payload = {"email": "admin@akvo.org", "password": "Test105*"}
        user_response = self.client.post(
            "/api/v1/login", user_payload, content_type="application/json"
        )
        self.token = user_response.json().get("token")

    def test_update_parent_of_village(self):
        target = Administration.objects.filter(
            name="Cawang"
        ).first()
        correct_parent = Administration.objects.filter(
            name="Kramat Jati"
        ).first()
        payload = {
            'parent': correct_parent.id,
            'name': target.name,
        }

        response = typing.cast(
                HttpResponse,
                self.client.put(
                    f"/api/v1/administrations/{target.id}",
                    payload,
                    content_type='application/json',
                    HTTP_AUTHORIZATION=f'Bearer {self.token}'))

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["name"], target.name)
        self.assertEqual(
            f"{correct_parent.path}{correct_parent.id}.",
            body["path"]
        )

    def test_update_parent_of_ward(self):
        target = Administration.objects.filter(
            name="Kramat Jati"
        ).first()
        correct_parent = Administration.objects.filter(
            name="East Jakarta"
        ).first()
        payload = {
            'parent': correct_parent.id,
            'name': target.name,
        }

        response = typing.cast(
                HttpResponse,
                self.client.put(
                    f"/api/v1/administrations/{target.id}",
                    payload,
                    content_type='application/json',
                    HTTP_AUTHORIZATION=f'Bearer {self.token}'))

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["name"], target.name)
        self.assertEqual(
            f"{correct_parent.path}{correct_parent.id}.",
            body["path"]
        )
        for child in target.parent_administration.all():
            self.assertTrue(str(correct_parent.id) in child.path)

    def test_update_parent_of_second_level(self):
        target = Administration.objects.filter(
            name="East Jakarta"
        ).first()
        correct_parent = Administration.objects.filter(
            name="Jakarta"
        ).first()
        payload = {
            'parent': correct_parent.id,
            'name': target.name,
        }

        response = typing.cast(
                HttpResponse,
                self.client.put(
                    f"/api/v1/administrations/{target.id}",
                    payload,
                    content_type='application/json',
                    HTTP_AUTHORIZATION=f'Bearer {self.token}'))

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["name"], target.name)

        current_path = f"{correct_parent.path}{correct_parent.id}."
        self.assertEqual(current_path, body["path"])

        villages_count = Administration.objects.filter(
            path__startswith=current_path,
            level__name="Kelurahan",
        ).count()
        self.assertEqual(villages_count, 2)
