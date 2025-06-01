from mis.settings import COUNTRY_NAME


class UserRoleTypes:
    super_admin = 1
    admin = 2

    FieldStr = {
        super_admin: "Super Admin",
        admin: "Admin",
    }


class OrganisationTypes:
    member = 1
    partnership = 2

    FieldStr = {
        member: "member",
        partnership: "partnership",
    }


class EntityTypes:
    school = 1
    health_care_facility = 2
    water_treatment_plant = 3
    rural_water_supply = 4

    FieldStr = {
        school: "School",
        health_care_facility: "Health Care Facilities",
        water_treatment_plant: "Water Treatment Plant",
        rural_water_supply: "Rural Water Supply",
    }


ADMINISTRATION_CSV_FILE = f"{COUNTRY_NAME}-administration.csv"

DEFAULT_SOURCE_FILE = f"./source/{ADMINISTRATION_CSV_FILE}"

DEFAULT_ADMINISTRATION_DATA = [
    {
        "id": 111,
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
        "id": 222,
        "code_0": "ID",
        "National_0": "Indonesia",
        "code_1": "ID-YGK",
        "Province_1": "Yogyakarta",
        "code_2": "ID-YGK-SLE",
        "District_2": "Sleman",
        "code_3": "ID-YGK-SLE-SET",
        "Subdistrict_3": "Seturan",
        "code_4": "ID-YGK-SLE-SET-CEP",
        "Village_4": "Cepit Baru",
    },
]

DEFAULT_ADMINISTRATION_LEVELS = [
    {"id": 1, "level": 0, "name": "NAME_0", "alias": "National"},
    {"id": 2, "level": 1, "name": "NAME_1", "alias": "Province"},
    {"id": 3, "level": 2, "name": "NAME_2", "alias": "District"},
    {"id": 4, "level": 3, "name": "NAME_3", "alias": "Subdistrict"},
    {"id": 5, "level": 4, "name": "NAME_4", "alias": "Village"},
]
