
import os
import django
from datetime import datetime, timezone

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "blueshield_project.settings"
)

django.setup()

from cases.models import Case
from suspects.models import Suspect
from records.models import CriminalOffence
from accounts.models import User
from stations.models import PoliceStation


CASES = [
    {
        "case_number": "CASE-2026-001",
        "title": "Reported Theft of Property",
        "description": (
            "A report was received concerning the alleged theft "
            "of personal property from a residential location."
        ),
        "suspect": "Daniel",
        "offence": "OFF-001",
        "officer": "jwarinak505",
        "station": 15,
        "status": "OPEN",
        "incident_date": datetime(2026, 8, 5, 10, 30),
        "location": "Madang Town",
    },
    {
        "case_number": "CASE-2026-002",
        "title": "Assault Investigation",
        "description": (
            "An alleged physical assault was reported and referred "
            "to police for investigation."
        ),
        "suspect": "Maria",
        "offence": "OFF-002",
        "officer": "jwarinak505",
        "station": 5,
        "status": "INVESTIGATION",
        "incident_date": datetime(2026, 8, 7, 18, 15),
        "location": "Bogia",
    },
    {
        "case_number": "CASE-2026-003",
        "title": "Burglary Report",
        "description": (
            "Police received a report concerning unlawful entry "
            "into a property and suspected theft."
        ),
        "suspect": "Peter",
        "offence": "OFF-003",
        "officer": "jwarinak505",
        "station": 1,
        "status": "PENDING",
        "incident_date": datetime(2026, 8, 9, 2, 20),
        "location": "Usino",
    },
    {
        "case_number": "CASE-2026-004",
        "title": "Robbery Investigation",
        "description": (
            "An alleged robbery involving personal belongings "
            "was reported to police."
        ),
        "suspect": "John",
        "offence": "OFF-004",
        "officer": "jwarinak505",
        "station": 7,
        "status": "APPROVED",
        "incident_date": datetime(2026, 8, 11, 21, 10),
        "location": "Karkar",
    },
    {
        "case_number": "CASE-2026-005",
        "title": "Homicide Investigation",
        "description": (
            "A serious incident resulting in a reported death "
            "was referred to police for investigation."
        ),
        "suspect": "Sarah",
        "offence": "OFF-005",
        "officer": "jwarinak505",
        "station": 10,
        "status": "INVESTIGATION",
        "incident_date": datetime(2026, 8, 13, 23, 40),
        "location": "Saidor",
    },
    {
        "case_number": "CASE-2026-006",
        "title": "Domestic Violence Report",
        "description": (
            "A domestic violence complaint was received and "
            "recorded for investigation."
        ),
        "suspect": "Thomas",
        "offence": "OFF-008",
        "officer": "jwarinak505",
        "station": 17,
        "status": "OPEN",
        "incident_date": datetime(2026, 8, 15, 19, 30),
        "location": "Aiome",
    },
    {
        "case_number": "CASE-2026-007",
        "title": "Property Damage Complaint",
        "description": (
            "A complaint was received regarding alleged damage "
            "to private property."
        ),
        "suspect": "David",
        "offence": "OFF-009",
        "officer": "jwarinak505",
        "station": 15,
        "status": "CLOSED",
        "incident_date": datetime(2026, 8, 17, 14, 45),
        "location": "Madang Town",
    },
    {
        "case_number": "CASE-2026-008",
        "title": "Drug Offence Investigation",
        "description": (
            "Police recorded an alleged possession-related "
            "drug offence for investigation."
        ),
        "suspect": "Anna",
        "offence": "OFF-010",
        "officer": "jwarinak505",
        "station": 6,
        "status": "INVESTIGATION",
        "incident_date": datetime(2026, 8, 19, 16, 20),
        "location": "Talidig",
    },
    {
        "case_number": "CASE-2026-009",
        "title": "Fraud Investigation",
        "description": (
            "An alleged financial fraud incident was reported "
            "and referred for investigation."
        ),
        "suspect": "Michael",
        "offence": "OFF-011",
        "officer": "jwarinak505",
        "station": 5,
        "status": "COURT",
        "incident_date": datetime(2026, 8, 21, 11, 10),
        "location": "Bogia",
    },
    {
        "case_number": "CASE-2026-010",
        "title": "Possession of Stolen Property",
        "description": (
            "Police recorded a suspected possession of property "
            "believed to have been unlawfully obtained."
        ),
        "suspect": "Joseph",
        "offence": "OFF-012",
        "officer": "jwarinak505",
        "station": 2,
        "status": "PENDING",
        "incident_date": datetime(2026, 8, 23, 9, 0),
        "location": "Walium",
    },
]


for data in CASES:

    suspect = Suspect.objects.filter(
        first_name=data["suspect"]
    ).first()

    if not suspect:
        print(
            f"ERROR: Suspect '{data['suspect']}' was not found."
        )
        continue

    offence = CriminalOffence.objects.filter(
        code=data["offence"]
    ).first()

    if not offence:
        print(
            f"ERROR: Offence '{data['offence']}' was not found."
        )
        continue

    officer = User.objects.filter(
        username=data["officer"]
    ).first()

    if not officer:
        print(
            f"ERROR: Officer '{data['officer']}' was not found."
        )
        continue

    station = PoliceStation.objects.filter(
        id=data["station"]
    ).first()

    if not station:
        print(
            f"ERROR: Station ID '{data['station']}' was not found."
        )
        continue

    case, created = Case.objects.get_or_create(
        case_number=data["case_number"],
        defaults={
            "title": data["title"],
            "description": data["description"],
            "suspect": suspect,
            "offence": offence,
            "investigating_officer": officer,
            "station": station,
            "status": data["status"],
            "incident_date": data["incident_date"],
            "location": data["location"],
        }
    )

    if created:
        print(
            f"Created case: {case.case_number} - {case.title}"
        )
    else:
        print(
            f"Case already exists: "
            f"{case.case_number}"
        )


print("\nCase seeding completed successfully.")

