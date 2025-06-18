from io import StringIO

from django.test.utils import override_settings
from django.core.management import call_command
from api.v1.v1_profile.models import Administration, Levels
from django.test import TestCase

from api.v1.v1_forms.models import Forms


def seed_administration_test():
    level = Levels(name="country", level=1)
    level.save()
    administration = Administration(
        id=1, name="Indonesia", parent=None, level=level
    )
    administration.save()
    administration = Administration(
        id=2, name="Jakarta", parent=administration, level=level
    )
    administration.save()


@override_settings(USE_TZ=False)
class FormSeederTestCase(TestCase):
    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "form_seeder",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def get_question_group(self, form, question_group_name):
        return [
            g
            for g in form["question_group"]
            if g["name"] == question_group_name
        ][0]

    def get_user_token(self):
        user = {"email": "admin@akvo.org", "password": "Test105*"}
        user = self.client.post(
            "/api/v1/login", user, content_type="application/json"
        )
        user = user.json()
        return user.get("token")

    def test_call_command(self):

        self.maxDiff = None
        seed_administration_test()
        forms = Forms.objects.all().delete()
        json_forms = [
            "WAF Water Treatment Plant",
            "WAF Wastewater Treatment Plan",
            "Wastewater Pump Station",
            "Rural Water Project Inspection",
            "Short HH",
            "EPS Water Quality Testing",
            "EPS Projects Construction",
            "WAF Inspection",
            "RWS Monitoring",
            "Short HH Monitoring",
            "Short HH Testimonials",
            "Wastewater Pump Station - Monitoring",
            "Wastewater Pump Station - Quick Inspection",
            "EPS Projects Construction - Monitoring",
            "WAF Water Treatment Plant - Monitoring",
            "WAF Quick Inspection",
            "EPS Water Quality Testing - Monitoring",
            "WAF Water Treatment Plant - Quick Monitoring",
        ]

        # RUN SEED NEW FORM
        output = self.call_command()
        output = list(filter(lambda x: len(x), output.split("\n")))
        forms = Forms.objects.all()
        self.assertEqual(forms.count(), len(json_forms))
        for form in forms:
            self.assertIn(
                f"Form Created | {form.name} V{form.version}", output
            )
            self.assertIn(form.name, json_forms)

        # RUN UPDATE EXISTING FORM
        output = self.call_command()
        output = list(filter(lambda x: len(x), output.split("\n")))
        forms = Forms.objects.all()
        form_ids = [form.id for form in forms]
        for form in forms:
            if form.version == 2:
                self.assertIn(
                    f"Form Updated | {form.name} V{form.version}", output
                )
            # FOR NON PRODUCTION FORM
            if form.version == 1:
                self.assertIn(
                    f"Form Created | {form.name} V{form.version}", output
                )
            self.assertIn(form.name, json_forms)

        token = self.get_user_token()
        self.assertTrue(token)
        for id in form_ids:
            response = self.client.get(
                f"/api/v1/form/web/{id}",
                follow=True,
                content_type="application/json",
                **{"HTTP_AUTHORIZATION": f"Bearer {token}"},
            )
            self.assertEqual(200, response.status_code)

        # TEST USING ./source/short-test-form.test.json
        response = self.client.get(
            "/api/v1/form/web/16993539153551",
            follow=True,
            content_type="application/json",
            **{"HTTP_AUTHORIZATION": f"Bearer {token}"},
        )
        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertTrue(response)

    def test_additional_attributes(self):
        seed_administration_test()
        self.call_command("--test")
        token = self.get_user_token()
        form_id = 2

        response = self.client.get(
            f"/api/v1/form/web/{form_id}",
            follow=True,
            content_type="application/json",
            **{"HTTP_AUTHORIZATION": f"Bearer {token}"},
        )

        data = response.json()
        self.assertIn("approval_instructions", data)
        gender = [
            q
            for q in data["question_group"][0]["question"]
            if q["name"] == "gender"
        ][0]
        self.assertIn("tooltip", gender)
        self.assertIn("color", gender["option"][0])
        autofield = [
            q
            for q in data["question_group"][0]["question"]
            if q["name"] == "autofield"
        ][0]
        self.assertIn("fn", autofield)

    def test_question_pre_field(self):
        seed_administration_test()
        self.call_command("--test")
        token = self.get_user_token()
        form_id = 2

        response = self.client.get(
            f"/api/v1/form/web/{form_id}",
            follow=True,
            content_type="application/json",
            **{"HTTP_AUTHORIZATION": f"Bearer {token}"},
        )

        data = response.json()
        gender = [
            q
            for q in data["question_group"][0]["question"]
            if q["name"] == "gender"
        ][0]
        self.assertIn("pre", gender)

    def test_display_only_and_monitoring_field(self):
        seed_administration_test()
        self.call_command("--test")
        token = self.get_user_token()
        form_id = 2

        response = self.client.get(
            f"/api/v1/form/web/{form_id}",
            follow=True,
            content_type="application/json",
            **{"HTTP_AUTHORIZATION": f"Bearer {token}"},
        )

        data = response.json()
        name = [
            q
            for q in data["question_group"][0]["question"]
            if q["name"] == "name"
        ][0]
        self.assertIn("displayOnly", name)
        self.assertTrue(name["displayOnly"])
        phone = [
            q
            for q in data["question_group"][0]["question"]
            if q["name"] == "phone"
        ][0]
        self.assertEqual(phone["short_label"], "Phone Number")

    def test_repeatable_question_group(self):
        seed_administration_test()
        self.call_command("--test")
        token = self.get_user_token()
        form_id = 4

        response = self.client.get(
            f"/api/v1/form/web/{form_id}",
            follow=True,
            content_type="application/json",
            **{"HTTP_AUTHORIZATION": f"Bearer {token}"},
        )

        data = response.json()
        question_group = [
            qg
            for qg in data["question_group"]
            if qg["name"] == "testimonials"
        ][0]
        self.assertIn("repeatable", question_group)
        self.assertTrue(question_group["repeatable"])
        self.assertIn("repeat_text", question_group)
        self.assertEqual(
            question_group["repeat_text"], "Add more"
        )

    def test_form_seeder_with_children(self):
        seed_administration_test()
        self.call_command("--test")
        form_1 = Forms.objects.get(pk=1)
        form_2 = Forms.objects.get(pk=2)

        self.assertEqual(form_1.name, "Test Form")
        self.assertEqual(form_2.name, "Test Form 2")
        self.assertEqual(form_1.children.count(), 1)
        self.assertEqual(form_2.children.count(), 0)
