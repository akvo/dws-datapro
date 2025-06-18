from django.core.management import BaseCommand
from django.core.management import call_command
from api.v1.v1_profile.models import (
    Administration,
    Entity,
    EntityData,
    SystemUser,
)
from api.v1.v1_forms.models import Forms
from api.v1.v1_profile.constants import EntityTypes
from api.v1.v1_profile.functions import get_max_administration_level


def seed_randomly(repeat: int = 1):
    MAX_ADM_LEVEL = get_max_administration_level()
    entity_types = EntityTypes.FieldStr.values()
    for t in entity_types:
        entity, created = Entity.objects.get_or_create(name=t)
        for i in range(repeat):
            administration = Administration.objects.filter(
                level__level=MAX_ADM_LEVEL
            ).order_by("?").first()
            name = entity.name if created else t
            EntityData.objects.create(
                name=f"{name} - {administration.name} {i+1}",
                entity=entity,
                administration=administration
            )


def seed_data(self, repeat: int = 1, test: bool = False):
    entity_form = Forms.objects.filter(
        form_question_group__question_group_question__extra__type="entity"
    ).all()
    for form in entity_form:
        users = SystemUser.objects.filter(
            user_form__form=form,
        ).all()
        for u in users:
            path = u.user_user_role.all().first().administration.path
            if not path:
                adm = u.user_user_role.all().first().administration
                path = f"{adm.id}."
            for adm in Administration.objects.filter(
                path__startswith=path
            )[:repeat].all():
                entity_types = EntityTypes.FieldStr.items()
                for t in entity_types:
                    key, value = t
                    entity, created = Entity.objects.get_or_create(
                        id=key,
                        name=value,
                    )
                    name = entity.name if created else value
                    EntityData.objects.get_or_create(
                        name=f"{name} - {adm.name}",
                        administration=adm,
                        entity=entity
                    )


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-t", "--test",
            nargs="?",
            const=False,
            default=False,
            type=bool
        )
        parser.add_argument(
            "-r", "--repeat",
            nargs="?",
            const=1,
            default=1,
            type=int
        )
        parser.add_argument(
            "-c", "--clean",
            nargs="?",
            const=1,
            default=False,
            type=int
        )

    def handle(self, *args, **options):
        test = options.get("test")
        repeat = options.get("repeat")
        clean = options.get("clean")
        if clean:
            EntityData.objects.all().delete()
            Entity.objects.all().delete()
            self.stdout.write("-- Entities Cleared")
        else:
            seed_data(self, repeat=repeat, test=test)
            seed_randomly(repeat=repeat)
        if not test:
            self.stdout.write("-- FINISH")
            call_command("generate_sqlite")
