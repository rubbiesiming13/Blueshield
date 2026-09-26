
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blueshield_project.settings")
django.setup()

from suspects.models import Suspect


SUSPECTS = [
    {
        "national_id_or_voter_no": "TEST-NID-001",
        "first_name": "Daniel",
        "last_name": "Wama",
        "alias": "Danny",
        "date_of_birth": "1992-04-15",
        "gender": "MALE",
        "village_province": "Madang Province",
        "residential_address": "Test Address, Madang",
        "identifying_marks": "Small scar above left eyebrow",
        "fingerprint_record_code": "FP-TEST-001",
    },
    {
        "national_id_or_voter_no": "TEST-NID-002",
        "first_name": "Maria",
        "last_name": "Kila",
        "alias": "Mia",
        "date_of_birth": "1995-08-22",
        "gender": "FEMALE",
        "village_province": "Bogia, Madang Province",
        "residential_address": "Test Address, Bogia",
        "identifying_marks": "Small tattoo on right wrist",
        "fingerprint_record_code": "FP-TEST-002",
    },
    {
        "national_id_or_voter_no": "TEST-NID-003",
        "first_name": "Peter",
        "last_name": "Yaro",
        "alias": "Pete",
        "date_of_birth": "1988-11-03",
        "gender": "MALE",
        "village_province": "Usino Bundi, Madang Province",
        "residential_address": "Test Address, Usino",
        "identifying_marks": "Scar on right forearm",
        "fingerprint_record_code": "FP-TEST-003",
    },
    {
        "national_id_or_voter_no": "TEST-NID-004",
        "first_name": "John",
        "last_name": "Maro",
        "alias": "",
        "date_of_birth": "1990-02-17",
        "gender": "MALE",
        "village_province": "Sumkar, Madang Province",
        "residential_address": "Test Address, Karkar",
        "identifying_marks": "None recorded",
        "fingerprint_record_code": "FP-TEST-004",
    },
    {
        "national_id_or_voter_no": "TEST-NID-005",
        "first_name": "Sarah",
        "last_name": "Bena",
        "alias": "Sally",
        "date_of_birth": "1997-06-10",
        "gender": "FEMALE",
        "village_province": "Raicoast, Madang Province",
        "residential_address": "Test Address, Saidor",
        "identifying_marks": "Birthmark on left cheek",
        "fingerprint_record_code": "FP-TEST-005",
    },
    {
        "national_id_or_voter_no": "TEST-NID-006",
        "first_name": "Thomas",
        "last_name": "Kora",
        "alias": "Tom",
        "date_of_birth": "1985-09-28",
        "gender": "MALE",
        "village_province": "Middle Ramu, Madang Province",
        "residential_address": "Test Address, Aiome",
        "identifying_marks": "Scar on chin",
        "fingerprint_record_code": "FP-TEST-006",
    },
    {
        "national_id_or_voter_no": "TEST-NID-007",
        "first_name": "David",
        "last_name": "Singa",
        "alias": "",
        "date_of_birth": "1993-12-05",
        "gender": "MALE",
        "village_province": "Madang District, Madang Province",
        "residential_address": "Test Address, Town",
        "identifying_marks": "Small scar on left hand",
        "fingerprint_record_code": "FP-TEST-007",
    },
    {
        "national_id_or_voter_no": "TEST-NID-008",
        "first_name": "Anna",
        "last_name": "Wari",
        "alias": "Annie",
        "date_of_birth": "1999-03-19",
        "gender": "FEMALE",
        "village_province": "Sumkar, Madang Province",
        "residential_address": "Test Address, Talidig",
        "identifying_marks": "None recorded",
        "fingerprint_record_code": "FP-TEST-008",
    },
    {
        "national_id_or_voter_no": "TEST-NID-009",
        "first_name": "Michael",
        "last_name": "Daku",
        "alias": "Mike",
        "date_of_birth": "1987-07-31",
        "gender": "MALE",
        "village_province": "Bogia, Madang Province",
        "residential_address": "Test Address, Bogia",
        "identifying_marks": "Tattoo on left shoulder",
        "fingerprint_record_code": "FP-TEST-009",
    },
    {
        "national_id_or_voter_no": "TEST-NID-010",
        "first_name": "Joseph",
        "last_name": "Ramu",
        "alias": "Joe",
        "date_of_birth": "1991-10-12",
        "gender": "MALE",
        "village_province": "Usino Bundi, Madang Province",
        "residential_address": "Test Address, Walium",
        "identifying_marks": "Scar on right eyebrow",
        "fingerprint_record_code": "FP-TEST-010",
    },
]


for data in SUSPECTS:

    suspect, created = Suspect.objects.get_or_create(
        national_id_or_voter_no=data["national_id_or_voter_no"],
        defaults=data
    )

    if created:
        print(
            f"Created suspect: "
            f"{suspect.first_name} {suspect.last_name}"
        )
    else:
        print(
            f"Suspect already exists: "
            f"{suspect.first_name} {suspect.last_name}"
        )


print("\nSuspect seeding completed successfully.")

