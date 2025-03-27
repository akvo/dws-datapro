class UserRoleTypes:
    super_admin = 1
    admin = 2
    approver = 3
    user = 4

    FieldStr = {
        super_admin: "Super Admin",
        admin: "County Admin",
        approver: "Data Approver",
        user: "Data Entry Supervisor",
    }


class UserDesignationTypes:
    nse = 1
    cse = 2
    ppho = 3
    pho = 4
    cpho = 5
    cwash = 6
    cha = 7
    chew = 8
    me = 9
    it = 10
    sa = 11
    tr = 12
    chv = 13

    FieldStr = {
        nse: "NSE (National Sanitation Extender)",
        cse: "CSE (County Sanitation Extender)",
        ppho: "PPHO (Principal Public Health Officer)",
        pho: "PHO (Public Health Officer)",
        cpho: "CPHO (County Public Health Officer)",
        cwash: "CWASH (County WASH Officer)",
        cha: "CHA (Community Health Assistant)",
        chew: "CHEW (Community Health Extension Worker)",
        me: "M&E",
        it: "IT",
        sa: "System Admin",
        tr: "Teacher",
        chv: "CHV (Community Health Volunteer)",
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
