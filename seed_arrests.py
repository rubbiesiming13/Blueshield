
import os
import django
from datetime import datetime

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "blueshield_project.settings"
)

django.setup()

from records.models import ArrestRecord, CriminalOffence
from cases.models import Case
from accounts.models import User
from stations.models import PoliceStation
from suspects.models import Suspect


ARRESTS = [
    {
        "case_number": "CASE-2026-001",
        "ob_number": "OB-2026-001",
        "arrest_datetime": datetime(2026, 8, 5, 11, 15),
        "arrest_location": "Madang Town",
        "reason_for_arrest": "Suspected theft of personal property.",
        "property_seized": "One mobile phone and one backpack recorded as exhibits.",
        "physical_condition_at_intake": "No visible injuries recorded at intake.",
        "custody_status": "DETAINED",
        "cell_number": "CELL-01",
        "bail_amount_pgk": None,
        "bail_receipt_no": "",
        "offence_code": "OFF-001",
        "station_id": 15,
        "officer_username": "jwarinak505",
    },

    {
        "case_number": "CASE-2026-002",
        "ob_number": "OB-2026-002",
        "arrest_datetime": datetime(2026, 8, 7, 19, 0),
        "arrest_location": "Bogia",
        "reason_for_arrest": "Suspected involvement in an assault incident.",
        "property_seized": "None recorded.",
        "physical_condition_at_intake": "Minor facial swelling noted and referred for medical assessment.",
        "custody_status": "BAILED_POLICE",
        "cell_number": None,
        "bail_amount_pgk": 500.00,
        "bail_receipt_no": "BR-2026-002",
        "offence_code": "OFF-002",
        "station_id": 5,
        "officer_username": "jwarinak505",
    },

    {
        "case_number": "CASE-2026-003",
        "ob_number": "OB-2026-003",
        "arrest_datetime": datetime(2026, 8, 9, 8, 30),
        "arrest_location": "Usino",
        "reason_for_arrest": "Suspected unlawful entry into a property.",
        "property_seized": "One metal tool recorded as an exhibit.",
        "physical_condition_at_intake": "No visible injuries recorded.",
        "custody_status": "DETAINED",
        "cell_number": "CELL-02",
        "bail_amount_pgk": None,
        "bail_receipt_no": "",
        "offence_code": "OFF-003",
        "station_id": 1,
        "officer_username": "jwarinak505",
    },

    {
        "case_number": "CASE-2026-004",
        "ob_number": "OB-2026-004",
        "arrest_datetime": datetime(2026, 8, 11, 22, 0),
        "arrest_location": "Karkar",
        "reason_for_arrest": "Suspected involvement in a robbery incident.",
        "property_seized": "One bag and personal items recorded as exhibits.",
        "physical_condition_at_intake": "No visible injuries recorded.",
        "custody_status": "COURT_BAIL",
        "cell_number": None,
        "bail_amount_pgk": 1000.00,
        "bail_receipt_no": "BR-2026-004",
        "offence_code": "OFF-004",
        "station_id": 7,
        "officer_username": "jwarinak505",
    },

    {
        "case_number": "CASE-2026-005",
        "ob_number": "OB-2026-005",
        "arrest_datetime": datetime(2026, 8, 14, 1, 10),
        "arrest_location": "Saidor",
        "reason_for_arrest": "Suspected involvement in a serious homicide investigation.",
        "property_seized": "Personal clothing and other items recorded for investigation.",
        "physical_condition_at_intake": "Medical assessment completed; no major injuries recorded.",
        "custody_status": "TRANSFERRED",
        "cell_number": None,
        "bail_amount_pgk": None,
        "bail_receipt_no": "",
        "offence_code": "OFF-005",
        "station_id": 10,
        "officer_username": "jwarinak505",
    },

    {
        "case_number": "CASE-2026-006",
        "ob_number": "OB-2026-006",
        "arrest_datetime": datetime(2026, 8, 15, 20, 15),
        "arrest_location": "Aiome",
        "reason_for_arrest": "Suspected involvement in a domestic violence incident.",
        "property_seized": "None recorded.",
        "physical_condition_at_intake": "No visible injuries recorded.",
        "custody_status": "DETAINED",
        "cell_number": "CELL-03",
        "bail_amount_pgk": None,
        "bail_receipt_no": "",
        "offence_code": "OFF-008",
        "station_id": 17,
        "officer_username": "jwarinak505",
    },

    {
        "case_number": "CASE-2026-007",
        "ob_number": "OB-2026-007",
        "arrest_datetime": datetime(2026, 8, 17, 15, 30),
        "arrest_location": "Madang Town",
        "reason_for_arrest": "Suspected property damage following a reported incident.",
        "property_seized": "One damaged tool recorded for evidence.",
        "physical_condition_at_intake": "No visible injuries recorded.",
        "custody_status": "RELEASED",
        "cell_number": None,
        "bail_amount_pgk": None,
        "bail_receipt_no": "",
        "offence_code": "OFF-009",
        "station_id": 15,
        "officer_username": "jwarinak505",
    },

    {
        "case_number": "CASE-2026-008",
        "ob_number": "OB-2026-008",
        "arrest_datetime": datetime(2026, 8, 19, 17, 5),
        "arrest_location": "Talidig",
        "reason_for_arrest": "Suspected possession of prohibited substances.",
        "property_seized": "Small package recorded and submitted as an exhibit.",
        "physical_condition_at_intake": "No visible injuries recorded.",
        "custody_status": "DETAINED",
        "cell_number": "CELL-04",
        "bail_amount_pgk": None,
        "bail_receipt_no": "",
        "offence_code": "OFF-010",
        "station_id": 6,
        "officer_username": "jwarinak505",
    },

    {
        "case_number": "CASE-2026-009",
        "ob_number": "OB-2026-009",
        "arrest_datetime": datetime(2026, 8, 21, 12, 0),
        "arrest_location": "Bogia",
        "reason_for_arrest": "Suspected involvement in a financial fraud investigation.",
        "property_seized": "Documents and electronic device recorded as exhibits.",
        "physical_condition_at_intake": "No visible injuries recorded.",
        "custody_status": "BAILED_POLICE",
        "cell_number": None,
        "bail_amount_pgk": 1500.00,
        "bail_receipt_no": "BR-2026-009",
        "offence_code": "OFF-011",
        "station_id": 5,
        "officer_username": "jwarinak505",
    },

    {
        "case_number": "CASE-2026-010",
        "ob_number": "OB-2026-010",
        "arrest_datetime": datetime(2026, 8, 23, 10, 0),
        "arrest_location": "Walium",
        "reason_for_arrest": "Suspected possession of property reported as stolen.",
        "property_seized": "Electronic equipment and personal items recorded as exhibits.",
        "physical_condition_at_intake": "No visible injuries recorded.",
        "custody_status": "DETAINED",
        "cell_number": "CELL-05",
        "bail_amount_pgk": None,
        "bail_receipt_no": "",
        "offence_code": "OFF-012",
        "station_id": 2,
        "officer_username": "jwarinak505",
    },
]


for data in ARRESTS:

    # Find Case
    case = Case.objects.filter(
        case_number=data["case_number"]
    ).first()

    if not case:
        print(
            f"ERROR: Case {data['case_number']} was not found."
        )
        continue

    # Find Officer
    officer = User.objects.filter(
        username=data["officer_username"]
    ).first()

    if not officer:
        print(
            f"ERROR: Officer {data['officer_username']} was not found."
        )
        continue

    # Find Station
    station = PoliceStation.objects.filter(
        id=data["station_id"]
    ).first()

    if not station:
        print(
            f"ERROR: Station ID {data['station_id']} was not found."
        )
        continue

    # Find Suspect through the Case
    suspect = case.suspect

    # Find offence
    offence = CriminalOffence.objects.filter(
        code=data["offence_code"]
    ).first()

    if not offence:
        print(
            f"ERROR: Offence {data['offence_code']} was not found."
        )
        continue

    # Prevent duplicate arrest records for the same OB number
    arrest, created = ArrestRecord.objects.get_or_create(
        occurrence_book_no=data["ob_number"],
        defaults={
            "suspect": suspect,
            "case": case,
            "arresting_officer": officer,
            "station": station,
            "arrest_datetime": data["arrest_datetime"],
            "arrest_location": data["arrest_location"],
            "reason_for_arrest": data["reason_for_arrest"],
            "property_seized": data["property_seized"],
            "physical_condition_at_intake": data[
                "physical_condition_at_intake"
            ],
            "custody_status": data["custody_status"],
            "cell_number": data["cell_number"],
            "bail_amount_pgk": data["bail_amount_pgk"],
            "bail_receipt_no": data["bail_receipt_no"],
        }
    )

    if created:
        # Connect the criminal offence
        arrest.offences.add(offence)

        print(
            f"Created arrest: "
            f"{arrest.arrest_tracking_id} -> "
            f"{case.case_number} -> "
            f"{suspect.full_name}"
        )
    else:
        print(
            f"Arrest already exists: "
            f"{arrest.occurrence_book_no}"
        )


print("\nArrest record seeding completed successfully.")

