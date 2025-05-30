from django.test import TestCase
from django.test.utils import override_settings

from django.core.management import call_command
from api.v1.v1_profile.models import EntityData, Entity


@override_settings(USE_TZ=False)
class EntitiesSeederTestCase(TestCase):

    def test_entities_seeder_test(self):
        call_command("administration_seeder", "--test")
        call_command("entities_seeder", "-r", 1, "--test", True)
        entities = EntityData.objects.all()
        total_entity = Entity.objects.count()
        self.assertEqual(entities.count(), total_entity)
