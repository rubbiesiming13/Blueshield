from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ArrestRecordForm
from .models import ArrestRecord


# ============================================================
# GET ACCESSIBLE ARREST RECORDS
# ============================================================

def get_accessible_arrest_records(user):
    """
    Return only the arrest records the logged-in user
    is allowed to access.
    """

    records = ArrestRecord.objects.none()

    # --------------------------------------------------------
    # POLICE OFFICER
    # --------------------------------------------------------
    # Can view arrest records created by themselves
    # at their assigned police station.
    # --------------------------------------------------------

    if user.role == "OFFICER":

        if user.station and user.district:

            records = ArrestRecord.objects.filter(
                arresting_officer=user,
                station=user.station,
            )

    # --------------------------------------------------------
    # DIVISION ADMIN
    # --------------------------------------------------------
    # Can view arrest records made by officers belonging
    # to the same division, station and district.
    # --------------------------------------------------------

    elif user.role == "DIVISION_ADMIN":

        if user.division and user.station and user.district:

            records = ArrestRecord.objects.filter(
                arresting_officer__division=user.division,
                station=user.station,
                station__district=user.district,
            )

    # --------------------------------------------------------
    # STATION COMMANDER
    # --------------------------------------------------------
    # Can view all arrest records belonging to their
    # assigned police station and district.
    # --------------------------------------------------------

    elif user.role == "STATION_COMMANDER":

        if user.station and user.district:

            records = ArrestRecord.objects.filter(
                station=user.station,
                station__district=user.district,
            )

    # --------------------------------------------------------
    # PPC / SYSTEM ADMIN
    # --------------------------------------------------------
    # Can view all arrest records.
    # --------------------------------------------------------

    elif user.role == "ADMIN":

        records = ArrestRecord.objects.all()

    return records


# ============================================================
# ARREST RECORD LIST
# ============================================================

@login_required(login_url="accounts:login")
def record_list(request):

    records = get_accessible_arrest_records(request.user)

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
    # GET USER'S ASSIGNED STATION
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
    # GET DISTRICT
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
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        form = ArrestRecordForm(
            request.POST
        )

        if form.is_valid():

            try:

                with transaction.atomic():

                    arrest_record = form.save(
                        commit=False
                    )

                    # ------------------------------------------------
                    # SECURITY:
                    # Never accept officer or station from POST data.
                    # These values come directly from the logged-in
                    # BlueShield account.
                    # ------------------------------------------------

                    arrest_record.arresting_officer = user
                    arrest_record.station = station

                    arrest_record.save()

                    # Save ManyToMany offences.
                    form.save_m2m()

                messages.success(
                    request,
                    f"Arrest record "
                    f"{arrest_record.arrest_tracking_id} "
                    "was successfully created."
                )

                return redirect(
                    "records:detail",
                    pk=arrest_record.pk
                )

            except Exception:

                messages.error(
                    request,
                    "An error occurred while saving the arrest record. "
                    "Please try again."
                )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

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


# ============================================================
# ARREST RECORD DETAIL
# ============================================================

@login_required(login_url="accounts:login")
def record_detail(request, pk):

    # --------------------------------------------------------
    # GET ONLY RECORDS THIS USER IS ALLOWED TO ACCESS
    # --------------------------------------------------------

    records = get_accessible_arrest_records(
        request.user
    )

    record = get_object_or_404(
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
        ),
        pk=pk,
    )

    return render(
        request,
        "records/detail.html",
        {
            "record": record,
        }
    )


# ============================================================
# EDIT ARREST RECORD
# ============================================================

@login_required(login_url="accounts:login")
def record_edit(request, pk):

    user = request.user

    # --------------------------------------------------------
    # Only Police Officers can edit arrest records.
    # --------------------------------------------------------

    if user.role != "OFFICER":

        messages.error(
            request,
            "You do not have permission to edit arrest records."
        )

        return redirect(
            "records:list"
        )

    # --------------------------------------------------------
    # Officer can only edit their own accessible record.
    # --------------------------------------------------------

    records = get_accessible_arrest_records(
        user
    )

    record = get_object_or_404(
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
        ),
        pk=pk,
    )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        form = ArrestRecordForm(
            request.POST,
            instance=record
        )

        if form.is_valid():

            try:

                with transaction.atomic():

                    updated_record = form.save(
                        commit=False
                    )

                    # ------------------------------------------------
                    # SECURITY:
                    # Keep the original officer and station.
                    # A user must not be able to change these
                    # through manipulated POST data.
                    # ------------------------------------------------

                    updated_record.arresting_officer = (
                        record.arresting_officer
                    )

                    updated_record.station = (
                        record.station
                    )

                    updated_record.save()

                    form.save_m2m()

                messages.success(
                    request,
                    f"Arrest record "
                    f"{record.arrest_tracking_id} "
                    "was successfully updated."
                )

                return redirect(
                    "records:detail",
                    pk=record.pk
                )

            except Exception:

                messages.error(
                    request,
                    "An error occurred while updating the arrest "
                    "record. Please try again."
                )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    else:

        form = ArrestRecordForm(
            instance=record
        )

    return render(
        request,
        "records/edit.html",
        {
            "form": form,
            "record": record,
            "officer": record.arresting_officer,
            "station": record.station,
            "district": (
                record.station.district
                if record.station
                else None
            ),
        }
    )


# ============================================================
# DELETE ARREST RECORD
# ============================================================

@login_required(login_url="accounts:login")
def record_delete(request, pk):

    user = request.user

    # --------------------------------------------------------
    # Only Police Officers can delete arrest records.
    # --------------------------------------------------------

    if user.role != "OFFICER":

        messages.error(
            request,
            "You do not have permission to delete arrest records."
        )

        return redirect(
            "records:list"
        )

    # --------------------------------------------------------
    # Officer can only delete their own accessible record.
    # --------------------------------------------------------

    records = get_accessible_arrest_records(
        user
    )

    record = get_object_or_404(
        records,
        pk=pk,
    )

    # --------------------------------------------------------
    # DELETE ONLY THROUGH POST
    # --------------------------------------------------------

    if request.method == "POST":

        tracking_id = record.arrest_tracking_id

        try:

            with transaction.atomic():

                record.delete()

            messages.success(
                request,
                f"Arrest record {tracking_id} "
                "was successfully deleted."
            )

            return redirect(
                "records:list"
            )

        except Exception:

            messages.error(
                request,
                "The arrest record could not be deleted. "
                "It may be linked to other protected records."
            )

            return redirect(
                "records:detail",
                pk=pk
            )

    # --------------------------------------------------------
    # GET REQUEST
    # Show confirmation page.
    # --------------------------------------------------------

    return render(
        request,
        "records/delete.html",
        {
            "record": record,
        }
    )