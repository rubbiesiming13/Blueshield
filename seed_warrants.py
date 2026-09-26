
import os
import django
from datetime import date, timedelta

# ---------------------------------------------------------
# Django setup
# ---------------------------------------------------------

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "blueshield_project.settings"
)

django.setup()

# ---------------------------------------------------------
# Models
# ---------------------------------------------------------

from warrant.models import Warrant
from cases.models import Case


# ---------------------------------------------------------
# Get ALL cases
# ---------------------------------------------------------

cases = Case.objects.select_related(
    "suspect",
    "station",
    "investigating_officer"
).order_by("id")

print(f"Found {cases.count()} cases.")

if cases.count() == 0:
    print("No cases found. Please create cases first.")
    exit()


created_count = 0
existing_count = 0


# ---------------------------------------------------------
# Create one warrant for each case
# ---------------------------------------------------------

for index, case in enumerate(cases, start=1):

    # Use case number to make warrant number unique
    warrant_number = f"WR-2026-{index:04d}"

    # -----------------------------------------------------
    # Check whether this case already has a warrant
    # -----------------------------------------------------

    existing_warrant = Warrant.objects.filter(
        case=case
    ).first()

    if existing_warrant:
        existing_count += 1

        print(
            f"Warrant already exists: "
            f"{existing_warrant.warrant_number} "
            f"-> {case.case_number}"
        )

        continue

    # -----------------------------------------------------
    # Alternate between Arrest and Search Warrants
    # -----------------------------------------------------

    if index % 2 == 1:

        warrant_type = Warrant.WarrantType.ARREST

        reason = (
            f"Arrest warrant requested in relation to "
            f"case {case.case_number}. The suspect "
            f"{case.suspect.full_name} is required for "
            f"lawful arrest and further police investigation."
        )

    else:

        warrant_type = Warrant.WarrantType.SEARCH

        reason = (
            f"Search warrant requested in relation to "
            f"case {case.case_number}. There are reasonable "
            f"grounds to search property or premises associated "
            f"with the suspect for evidence relevant to the case."
        )

    # -----------------------------------------------------
    # Dates
    # -----------------------------------------------------

    issue_date = date.today()

    expiry_date = issue_date + timedelta(days=30)

    # -----------------------------------------------------
    # Create warrant
    # -----------------------------------------------------

    warrant = Warrant.objects.create(
        warrant_number=warrant_number,
        warrant_type=warrant_type,

        # Link warrant to the case
        case=case,

        # Get suspect and station from the case
        suspect=case.suspect,
        station=case.station,

        reason=reason,

        issue_date=issue_date,
        expiry_date=expiry_date,

        # New warrants require approval
        status=Warrant.Status.PENDING,

        # Investigating officer requests the warrant
        requested_by=case.investigating_officer
    )

    created_count += 1

    print(
        f"Created warrant: "
        f"{warrant.warrant_number} "
        f"| {warrant.get_warrant_type_display()} "
        f"| Case: {case.case_number} "
        f"| Suspect: {case.suspect.full_name} "
        f"| Station: {case.station.name} "
        f"| Requested by: "
        f"{case.investigating_officer.username}"
    )


# ---------------------------------------------------------
# Final summary
# ---------------------------------------------------------

print()

print("==============================================")
print("WARRANT SEEDING COMPLETED")
print("==============================================")

print(f"Cases processed   : {cases.count()}")
print(f"Created warrants  : {created_count}")
print(f"Existing warrants : {existing_count}")
print(f"Total warrants    : {Warrant.objects.count()}")

print("==============================================")

