import pandas as pd
from django.core.management import BaseCommand
from api.v1.v1_profile.models import Levels, Administration


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


def seed_administration_test():
    geo_config = [
        {"id": 1, "level": 0, "name": "NAME_0", "alias": "National"},
        {"id": 2, "level": 1, "name": "NAME_1", "alias": "Province"},
        {"id": 3, "level": 2, "name": "NAME_1", "alias": "District"},
        {"id": 4, "level": 3, "name": "NAME_2", "alias": "Subdistrict"},
        {"id": 5, "level": 4, "name": "NAME_3", "alias": "Village"},
    ]
    seed_levels(geo_config=geo_config)
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
            "1_code": "ID-YGK",
            "1_Province": "Yogyakarta",
            "2_code": "ID-YGK-SLE",
            "2_District": "Sleman",
            "3_code": "ID-YGK-SLE-SET",
            "3_Subdistrict": "Seturan",
            "4_code": "ID-YGK-SLE-SET-CEP",
            "4_Village": "Cepit Baru",
        },
    ]
    for row in rows:
        seed_administration(row=row, geo_config=geo_config)


def seed_administration_prod(
    source_file: str = "./source/administrations_fiji.csv"
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
            default="./source/administrations_fiji.csv",
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
