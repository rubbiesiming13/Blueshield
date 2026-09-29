from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect

from .forms import ArrestRecordForm
from .models import ArrestRecord


# ============================================================
# ARREST RECORD LIST
# ============================================================

@login_required(login_url="accounts:login")
def record_list(request):

    user = request.user

    # --------------------------------------------------------
    # START WITH NO RECORDS
    # --------------------------------------------------------

    records = ArrestRecord.objects.none()

    # ========================================================
    # POLICE OFFICER
    # ========================================================
    # Officer sees ONLY arrests made by that officer.
    # ========================================================

    if user.role == "OFFICER":

        if user.station and user.district:

            records = ArrestRecord.objects.filter(
                arresting_officer=user,
                station=user.station,
            )

    # ========================================================
    # DIVISION ADMIN / PROSECUTION
    # ========================================================
    # Sees arrests within their assigned division,
    # district and station.
    # ========================================================

    elif user.role == "DIVISION_ADMIN":

        if user.division and user.station and user.district:

            records = ArrestRecord.objects.filter(
                arresting_officer__division=user.division,
                station=user.station,
                station__district=user.district,
            )

    # ========================================================
    # STATION COMMANDER
    # ========================================================
    # Sees all arrests at their station.
    # ========================================================

    elif user.role == "STATION_COMMANDER":

        if user.station and user.district:

            records = ArrestRecord.objects.filter(
                station=user.station,
                station__district=user.district,
            )

    # ========================================================
    # PPC / SYSTEM ADMIN
    # ========================================================
    # Province-wide access.
    # ========================================================

    elif user.role == "ADMIN":

        records = ArrestRecord.objects.all()

    # ========================================================
    # COMMON QUERY OPTIMIZATION
    # ========================================================

    records = (
        records
        .select_related(
            "suspect",
            "case",
            "arresting_officer",
            "station",
            "station__district",
        )
        .prefetch_related(
            "offences"
        )
        .order_by(
            "-created_at"
        )
    )

    return render(
        request,
        "records/list.html",
        {
            "records": records,
        }
    )


# ============================================================
# CREATE ARREST RECORD
# ============================================================

@login_required(login_url="accounts:login")
def record_create(request):

    user = request.user

    # --------------------------------------------------------
    # ONLY POLICE OFFICERS CAN CREATE ARREST RECORDS
    # --------------------------------------------------------

    if user.role != "OFFICER":

        messages.error(
            request,
            "You do not have permission to create arrest records."
        )

        return redirect("accounts:dashboard")

    # --------------------------------------------------------
    # BACKEND-CONTROLLED STATION
    # --------------------------------------------------------

    station = user.station

    if not station:

        messages.error(
            request,
            "Your BlueShield account does not have a police station "
            "assigned. Please contact the system administrator."
        )

        return redirect("accounts:dashboard")

    # --------------------------------------------------------
    # BACKEND-CONTROLLED DISTRICT
    # --------------------------------------------------------

    district = getattr(
        station,
        "district",
        None
    )

    if not district:

        messages.error(
            request,
            "Your assigned police station does not have a district "
            "configured. Please contact the system administrator."
        )

        return redirect("accounts:dashboard")

    # --------------------------------------------------------
    # CREATE RECORD
    # --------------------------------------------------------

    if request.method == "POST":

        form = ArrestRecordForm(
            request.POST
        )

        if form.is_valid():

            with transaction.atomic():

                arrest_record = form.save(
                    commit=False
                )

                # NEVER accept these values from POST data.
                # They are controlled by the authenticated officer.

                arrest_record.arresting_officer = user
                arrest_record.station = station

                arrest_record.save()

                form.save_m2m()

            messages.success(
                request,
                f"Arrest record "
                f"{arrest_record.arrest_tracking_id} "
                "was successfully created."
            )

            return redirect(
                "records:list"
            )

    else:

        form = ArrestRecordForm()

    return render(
        request,
        "records/create_arrest_record.html",
        {
            "form": form,
            "officer": user,
            "station": station,
            "district": district,
        }
    )