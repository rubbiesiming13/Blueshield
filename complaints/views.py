from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    ComplaintForm,
    ComplaintWitnessForm,
    ComplaintWitnessFormSet,
)
from .models import Complaint, ComplaintWitness

from accounts.services import log_activity


def generate_complaint_number():
    """
    Generate a complaint number such as:
    CMP-2026-0001
    """

    year = timezone.now().year

    last_complaint = (
        Complaint.objects
        .filter(
            complaint_number__startswith=f"CMP-{year}-"
        )
        .order_by("-complaint_number")
        .first()
    )

    if last_complaint:
        try:
            last_number = int(
                last_complaint.complaint_number.split("-")[-1]
            )
        except (ValueError, IndexError):
            last_number = 0
    else:
        last_number = 0

    return f"CMP-{year}-{last_number + 1:04d}"


# ============================================================
# CREATE COMPLAINT
# ============================================================

@login_required
def create_complaint(request):

    user = request.user

    # Officer must have a station
    if not user.station:
        return render(
            request,
            "complaints/create_complaint.html",
            {
                "form": ComplaintForm(),
                "witness_forms": [],
                "witness_count": 0,
                "station": None,
                "district": None,
                "officer": user,
                "error_message": (
                    "Your account is not assigned to a police station. "
                    "Please contact the System Administrator."
                ),
            },
        )

    station = user.station
    district = getattr(station, "district", None)

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    if request.method == "GET":

        form = ComplaintForm()

        return render(
            request,
            "complaints/create_complaint.html",
            {
                "form": form,
                "witness_forms": [],
                "witness_count": 0,
                "station": station,
                "district": district,
                "officer": user,
            },
        )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    form = ComplaintForm(request.POST)

    try:
        witness_count = int(
            request.POST.get("witness_count", 0)
        )
    except (TypeError, ValueError):
        witness_count = 0

    # Keep witness count between 0 and 20
    witness_count = max(
        0,
        min(witness_count, 20)
    )

    witness_forms = []

    for i in range(witness_count):

        witness_form = ComplaintWitnessForm(
            request.POST,
            prefix=f"witness-{i}",
        )

        witness_forms.append(witness_form)

    complaint_valid = form.is_valid()

    witnesses_valid = True

    for witness_form in witness_forms:

        if not witness_form.is_valid():
            witnesses_valid = False

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    if complaint_valid and witnesses_valid:

        with transaction.atomic():

            complaint = form.save(
                commit=False
            )

            complaint.reported_by = user
            complaint.station = station
            complaint.complaint_number = (
                generate_complaint_number()
            )

            complaint.save()

            # Save additional witnesses
            for witness_form in witness_forms:

                witness = witness_form.save(
                    commit=False
                )

                witness.complaint = complaint

                witness.save()

        # ----------------------------------------------------
        # AUDIT LOG
        # ----------------------------------------------------

        log_activity(
            request=request,
            action="CREATE",
            target_model="Complaint",
            target_id=complaint.pk,
            details=(
                f"Created complaint "
                f"{complaint.complaint_number}. "
                f"Station: {station.name}. "
                f"District: "
                f"{district.name if district else 'N/A'}."
            ),
        )

        # Go back to My Complaints
        return redirect(
            "complaints:list"
        )

    # --------------------------------------------------------
    # VALIDATION ERROR
    # --------------------------------------------------------

    return render(
        request,
        "complaints/create_complaint.html",
        {
            "form": form,
            "witness_forms": witness_forms,
            "witness_count": witness_count,
            "station": station,
            "district": district,
            "officer": user,
        },
    )


# ============================================================
# COMPLAINT LIST
# ============================================================

@login_required
def complaint_list(request):

    user = request.user

    complaints = (
        Complaint.objects
        .filter(
            reported_by=user
        )
        .select_related(
            "station",
            "station__district",
            "reported_by",
        )
        .prefetch_related(
            "witnesses"
        )
        .order_by(
            "-created_at"
        )
    )

    return render(
        request,
        "complaints/complaint_list.html",
        {
            "complaints": complaints,
        },
    )


# ============================================================
# VIEW COMPLAINT DETAILS
# ============================================================

@login_required
def complaint_detail(request, pk):

    user = request.user

    # Security:
    # The officer can only view complaints they registered.
    complaint = get_object_or_404(
        Complaint.objects
        .filter(
            reported_by=user
        )
        .select_related(
            "station",
            "station__district",
            "reported_by",
        )
        .prefetch_related(
            "witnesses"
        ),
        pk=pk,
    )

    # --------------------------------------------------------
    # AUDIT LOG
    # --------------------------------------------------------

    log_activity(
        request=request,
        action="VIEW",
        target_model="Complaint",
        target_id=complaint.pk,
        details=(
            f"Viewed complaint "
            f"{complaint.complaint_number}."
        ),
    )

    return render(
        request,
        "complaints/complaint_detail.html",
        {
            "complaint": complaint,
        },
    )


# ============================================================
# EDIT COMPLAINT
# ============================================================

@login_required
def edit_complaint(request, pk):

    user = request.user

    # Security:
    # An officer can only edit a complaint they registered.
    complaint = get_object_or_404(
        Complaint.objects
        .filter(
            reported_by=user
        )
        .select_related(
            "station",
            "station__district",
            "reported_by",
        ),
        pk=pk,
    )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    if request.method == "GET":

        form = ComplaintForm(
            instance=complaint
        )

        # witness_count is not needed for editing because
        # the formset controls the witnesses.
        form.fields[
            "witness_count"
        ].required = False

        witness_formset = ComplaintWitnessFormSet(
            instance=complaint,
            prefix="witnesses",
        )

        return render(
            request,
            "complaints/complaint_edit.html",
            {
                "form": form,
                "witness_formset": witness_formset,
                "complaint": complaint,
            },
        )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    form = ComplaintForm(
        request.POST,
        instance=complaint,
    )

    # The witness formset handles existing, new and deleted
    # witnesses.
    witness_formset = ComplaintWitnessFormSet(
        request.POST,
        instance=complaint,
        prefix="witnesses",
    )

    # witness_count is not used by the edit process
    form.fields[
        "witness_count"
    ].required = False

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    if form.is_valid() and witness_formset.is_valid():

        with transaction.atomic():

            # Update complaint
            complaint = form.save()

            # Make sure the formset remains attached
            # to this complaint.
            witness_formset.instance = complaint

            # Save:
            # - existing witness edits
            # - new witnesses
            # - deleted witnesses
            witness_formset.save()

        # ----------------------------------------------------
        # AUDIT LOG
        # ----------------------------------------------------

        log_activity(
    request=request,
    action="UPDATE",
    target_model="Complaint",
    target_id=complaint.pk,
    details=(
        f"Updated complaint "
        f"{complaint.complaint_number}. "
        f"Station: "
        f"{complaint.station.name if complaint.station else 'N/A'}."
    ),
)

        # After editing, show the complaint details
        return redirect(
            "complaints:detail",
            pk=complaint.pk,
        )

    # --------------------------------------------------------
    # VALIDATION ERROR
    # --------------------------------------------------------

    return render(
        request,
        "complaints/complaint_edit.html",
        {
            "form": form,
            "witness_formset": witness_formset,
            "complaint": complaint,
        },
    )