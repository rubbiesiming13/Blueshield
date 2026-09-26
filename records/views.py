from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect

from .forms import ArrestRecordForm
from .models import ArrestRecord


@login_required
def record_list(request):

    records = (
        ArrestRecord.objects
        .select_related(
            "suspect",
            "case",
            "arresting_officer",
            "station",
        )
        .prefetch_related("offences")
        .order_by("-created_at")
    )

    return render(
        request,
        "records/list.html",
        {
            "records": records,
        }
    )


@login_required
def record_create(request):

    user = request.user

    # -------------------------------------------------
    # BACKEND-CONTROLLED STATION
    # -------------------------------------------------
    station = user.station

    if not station:
        messages.error(
            request,
            "Your BlueShield account does not have a police station "
            "assigned. Please contact the system administrator."
        )

        return redirect("accounts:dashboard")

    # -------------------------------------------------
    # BACKEND-CONTROLLED DISTRICT
    # -------------------------------------------------
    district = getattr(station, "district", None)

    if not district:
        messages.error(
            request,
            "Your assigned police station does not have a district "
            "configured. Please contact the system administrator."
        )

        return redirect("accounts:dashboard")

    # -------------------------------------------------
    # CREATE RECORD
    # -------------------------------------------------
    if request.method == "POST":

        form = ArrestRecordForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                arrest_record = form.save(commit=False)

                # NEVER accept these from POST data.
                # They are controlled by the authenticated user.
                arrest_record.arresting_officer = user
                arrest_record.station = station

                arrest_record.save()

                form.save_m2m()

            messages.success(
                request,
                f"Arrest record "
                f"{arrest_record.arrest_tracking_id} "
                f"was successfully created."
            )

            return redirect("records:list")

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