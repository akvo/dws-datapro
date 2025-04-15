import pandas as pd
from django.core.management import BaseCommand
from api.v1.v1_profile.models import Levels, Administration
from api.v1.v1_profile.constants import (
    DEFAULT_ADMINISTRATION_DATA,
    DEFAULT_ADMINISTRATION_LEVELS,
    DEFAULT_SOURCE_FILE,
)


def seed_levels(geo_config: list = []):
    for geo in geo_config:
        level = Levels(id=geo["id"], name=geo["alias"], level=geo["level"])
        level.save()


def seed_administration(row: dict, geo_config: list = []):
    for geo in geo_config:
        col_level = f"{geo['level']}_{geo['alias']}"
        parent = None
        if geo["level"] > 0:
            code_parent = row.get(f"{geo['level'] - 1}_code")
            parent = Administration.objects.filter(
                code=code_parent, level__level=geo["level"] - 1
            ).first()
        # Get the level from the geo_config
        level = Levels.objects.filter(level=geo["level"]).first()
        # Get the code from the row
        code = row.get(f"{geo['level']}_code")
        # Get the name from the row
        name = row[col_level]

        Administration.objects.update_or_create(
            name=name,
            defaults={
                "level": level,
                "code": code,
                "parent": parent,
            },
        )


def seed_administration_test(
    rows: list = DEFAULT_ADMINISTRATION_DATA,
    geo_config: list = DEFAULT_ADMINISTRATION_LEVELS,
):
    seed_levels(geo_config=geo_config)
    for row in rows:
        seed_administration(row=row, geo_config=geo_config)


def seed_administration_prod(
    source_file: str = DEFAULT_SOURCE_FILE,
):
    Levels.objects.all().delete()

    df = pd.read_csv(source_file)
    header_columns = df.columns.tolist()
    geo_config = []
    for column in header_columns:
        level = int(column.split("_")[0])
        alias = column.split("_")[1]
        if alias.lower() == "code":
            # Skip the code column
            continue
        geo_config.append(
            {
                "id": level + 1,
                "level": level,
                "name": f"NAME_{level}",
                "alias": alias,
            }
        )
    geo_config = sorted(geo_config, key=lambda x: x["level"])

    seed_levels(geo_config=geo_config)
    df = pd.read_csv(source_file)
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)
    for _, row in df.iterrows():
        seed_administration(row=row, geo_config=geo_config)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-t", "--test", nargs="?", const=1, default=False, type=int
        )
        parser.add_argument(
            "-c", "--clean", nargs="?", const=1, default=False, type=int
        )
        parser.add_argument(
            "-s",
            "--source",
            nargs="?",
            const=1,
            default=DEFAULT_SOURCE_FILE,
            type=str,
        )

    def handle(self, *args, **options):
        test = options.get("test")
        clean = options.get("clean")
        source_file = options.get("source")
        if clean:
            Administration.objects.all().delete()
            self.stdout.write("-- Administration Cleared")
        if test:
            seed_administration_test()
        if not test:
            seed_administration_prod(
                source_file=source_file,
            )
            self.stdout.write("-- FINISH")
