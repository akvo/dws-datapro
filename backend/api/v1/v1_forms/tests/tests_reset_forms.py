from io import StringIO
from django.test import TestCase
from django.test.utils import override_settings
from django.core.management import call_command
from api.v1.v1_forms.models import Forms


@override_settings(USE_TZ=False)
class FormSeederTestCase(TestCase):
    def setUp(self):
        # Run the form seeder twice to ensure forms
        # are populated with the last version is 2
        call_command("form_seeder", "--test")
        call_command("form_seeder", "--test")

    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "reset_forms",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def test_call_reset_forms_command(self):
        # Show version of the forms before reset
        initial_forms = Forms.objects.all().values_list('id', 'version')
        initial_forms_dict = {form[0]: form[1] for form in initial_forms}
        # Ensure there are forms to reset
        self.assertGreater(len(initial_forms_dict), 0, "No forms to reset.")
        # Check the initial version of the forms
        for form_id, version in initial_forms_dict.items():
            self.assertEqual(
                version,
                2,
                f"Form {form_id} is not at version 2."
            )
        output = self.call_command("--test")
        # Check if the output contains the success message
        self.assertIn("Successfully reset all forms.", output)
        # Check if the forms are reset
        reset_forms = Forms.objects.all().values_list('id', 'version')
        reset_forms_dict = {form[0]: form[1] for form in reset_forms}
        # Ensure forms are still present after reset
        self.assertGreater(len(reset_forms_dict), 0, "No forms after reset.")
        # Check if the forms are reset to version 1
        for form_id, version in reset_forms_dict.items():
            self.assertEqual(
                version,
                1,
                f"Form {form_id} is not reset to version 1."
            )
        # Ensure the reset command does not create new forms
        self.assertEqual(
            len(initial_forms_dict),
            len(reset_forms_dict),
            "Reset command created new forms."
        )
        # Ensure the reset command did not delete any forms
        self.assertEqual(
            set(initial_forms_dict.keys()),
            set(reset_forms_dict.keys()),
            "Reset command deleted some forms."
        )
        # Ensure the reset command did not change the IDs of the forms
        for form_id in initial_forms_dict.keys():
            self.assertIn(
                form_id,
                reset_forms_dict,
                f"Form {form_id} was deleted during reset."
            )
