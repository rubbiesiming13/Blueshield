from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import role_required
from cases.models import Case
from evidence.models import Evidence

from .forms import (
    InvestigationRecordForm,
    StatementForm,
    EvidenceForm,
)

from .models import (
    InvestigationRecord,
    Statement,
)


# ============================================================
# INVESTIGATION LIST
# ============================================================

@login_required(login_url="accounts:login")
def investigation_list(request):

    investigations = (
        InvestigationRecord.objects
        .select_related(
            "case",
            "investigating_officer",
        )
        .filter(
            investigating_officer=request.user
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "investigation/investigation_list.html",
        {
            "investigations": investigations
        }
    )


# ============================================================
# INVESTIGATION DETAIL
# ============================================================

@login_required(login_url="accounts:login")
def investigation_detail(request, pk):

    investigation = get_object_or_404(
        InvestigationRecord.objects.select_related(
            "case",
            "investigating_officer",
        ),
        pk=pk,
        investigating_officer=request.user
    )

    return render(
        request,
        "investigation/investigation_detail.html",
        {
            "investigation": investigation
        }
    )


# ============================================================
# CREATE INVESTIGATION RECORD
# ============================================================

@login_required(login_url="accounts:login")
@role_required("OFFICER")
def investigation_create(request):

    if request.method == "POST":

        form = InvestigationRecordForm(
            request.POST,
            user=request.user
        )

        if form.is_valid():

            investigation = form.save(commit=False)

            # ------------------------------------------------
            # GET SELECTED CASE
            # ------------------------------------------------

            case = form.cleaned_data.get("case")

            if not case:

                messages.error(
                    request,
                    "Please select a case before saving the investigation."
                )

                return render(
                    request,
                    "investigation/investigation_form.html",
                    {
                        "form": form,
                        "page_title": "Create Investigation Record",
                    }
                )

            # ------------------------------------------------
            # SECURITY CHECK
            # Officer can only investigate their own cases.
            # ------------------------------------------------

            if case.investigating_officer_id != request.user.id:

                messages.error(
                    request,
                    "You are not authorized to record an investigation for this case."
                )

                return redirect("cases:list")

            # ------------------------------------------------
            # ATTACH CASE AND OFFICER
            # ------------------------------------------------

            investigation.case = case
            investigation.investigating_officer = request.user

            # ------------------------------------------------
            # SAVE INVESTIGATION
            # ------------------------------------------------

            investigation.save()

            # ------------------------------------------------
            # UPDATE CASE STATUS
            # ------------------------------------------------

            case.status = Case.Status.UNDER_INVESTIGATION

            case.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            messages.success(
                request,
                f"Investigation activity saved for {case.case_number}."
            )

            return redirect(
                "investigation:detail",
                pk=investigation.pk
            )

    else:

        form = InvestigationRecordForm(
            user=request.user
        )

    return render(
        request,
        "investigation/investigation_form.html",
        {
            "form": form,
            "page_title": "Create Investigation Record",
        }
    )


# ============================================================
# UPDATE INVESTIGATION RECORD
# ============================================================

@login_required(login_url="accounts:login")
@role_required("OFFICER")
def investigation_update(request, pk):

    investigation = get_object_or_404(
        InvestigationRecord,
        pk=pk,
        investigating_officer=request.user
    )

    if request.method == "POST":

        form = InvestigationRecordForm(
            request.POST,
            instance=investigation,
            user=request.user
        )

        if form.is_valid():

            investigation = form.save(commit=False)

            # Make sure the original case cannot be changed
            # to another officer's case.

            case = form.cleaned_data.get("case")

            if not case:

                messages.error(
                    request,
                    "Please select a case."
                )

                return render(
                    request,
                    "investigation/investigation_form.html",
                    {
                        "form": form,
                        "page_title": "Update Investigation Record",
                        "investigation": investigation,
                    }
                )

            if case.investigating_officer_id != request.user.id:

                messages.error(
                    request,
                    "You are not authorized to use this case."
                )

                return redirect("investigation:list")

            investigation.case = case
            investigation.investigating_officer = request.user

            investigation.save()

            # Keep case status correct.

            case.status = Case.Status.UNDER_INVESTIGATION

            case.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            messages.success(
                request,
                "Investigation record updated successfully."
            )

            return redirect(
                "investigation:detail",
                pk=investigation.pk
            )

    else:

        form = InvestigationRecordForm(
            instance=investigation,
            user=request.user
        )

    return render(
        request,
        "investigation/investigation_form.html",
        {
            "form": form,
            "page_title": "Update Investigation Record",
            "investigation": investigation,
        }
    )


# ============================================================
# DELETE INVESTIGATION RECORD
# ============================================================

@login_required(login_url="accounts:login")
@role_required("OFFICER")
def investigation_delete(request, pk):

    investigation = get_object_or_404(
        InvestigationRecord,
        pk=pk,
        investigating_officer=request.user
    )

    if request.method == "POST":

        investigation.delete()

        messages.success(
            request,
            "Investigation record deleted."
        )

        return redirect(
            "investigation:list"
        )

    return render(
        request,
        "investigation/investigation_confirm_delete.html",
        {
            "investigation": investigation
        }
    )


# ============================================================
# GENERATE EVIDENCE NUMBER
# ============================================================

def generate_evidence_number():

    year = timezone.now().year

    last_evidence = (
        Evidence.objects
        .filter(
            evidence_number__startswith=f"EVD-{year}-"
        )
        .order_by("-id")
        .first()
    )

    if last_evidence:

        try:

            last_number = int(
                last_evidence.evidence_number.rsplit("-", 1)[1]
            )

            next_number = last_number + 1

        except (ValueError, IndexError):

            next_number = 1

    else:

        next_number = 1

    return f"EVD-{year}-{next_number:04d}"


# ============================================================
# INVESTIGATION WORKSPACE
#
# ONE SELECTED CASE
#       ↓
# Investigation Record
#       ↓
# Statement (optional)
#       ↓
# Evidence (optional)
#       ↓
# Save
#       ↓
# Case becomes UNDER INVESTIGATION
#       ↓
# Return to Case Detail
# ============================================================

@login_required(login_url="accounts:login")
@role_required("OFFICER")
def investigation_workspace(request, case_id):

    # --------------------------------------------------------
    # GET SELECTED CASE
    # --------------------------------------------------------

    case = get_object_or_404(
        Case.objects.select_related(
            "complaint",
            "offence",
            "station",
            "suspect",
            "investigating_officer",
        ),
        pk=case_id,
        investigating_officer=request.user
    )

    # --------------------------------------------------------
    # POST REQUEST
    # --------------------------------------------------------

    if request.method == "POST":

        investigation_form = InvestigationRecordForm(
            request.POST,
            prefix="investigation",
            user=request.user
        )

        statement_form = StatementForm(
            request.POST,
            request.FILES,
            prefix="statement"
        )

        evidence_form = EvidenceForm(
            request.POST,
            prefix="evidence"
        )

        # ----------------------------------------------------
        # ATTACH THIS CASE TO ALL FORMS
        # ----------------------------------------------------

        investigation_form.instance.case = case
        statement_form.instance.case = case
        evidence_form.instance.case = case

        # ----------------------------------------------------
        # INVESTIGATION IS REQUIRED
        # ----------------------------------------------------

        investigation_valid = (
            investigation_form.is_valid()
        )

        # ----------------------------------------------------
        # CHECK WHETHER STATEMENT WAS ENTERED
        # ----------------------------------------------------

        statement_entered = any([
            request.POST.get(
                "statement-person",
                ""
            ).strip(),

            request.POST.get(
                "statement-statement",
                ""
            ).strip(),

            request.POST.get(
                "statement-location",
                ""
            ).strip(),

            request.POST.get(
                "statement-statement_type",
                ""
            ).strip(),

            request.POST.get(
                "statement-statement_date",
                ""
            ).strip(),
        ])

        # ----------------------------------------------------
        # CHECK WHETHER EVIDENCE WAS ENTERED
        # ----------------------------------------------------

        evidence_entered = any([
            request.POST.get(
                "evidence-description",
                ""
            ).strip(),

            request.POST.get(
                "evidence-location_found",
                ""
            ).strip(),

            request.POST.get(
                "evidence-evidence_type",
                ""
            ).strip(),

            request.POST.get(
                "evidence-date_collected",
                ""
            ).strip(),

            request.POST.get(
                "evidence-arrest",
                ""
            ).strip(),
        ])

        # ----------------------------------------------------
        # VALIDATE OPTIONAL STATEMENT
        # ----------------------------------------------------

        statement_valid = True

        if statement_entered:

            statement_valid = (
                statement_form.is_valid()
            )

        # ----------------------------------------------------
        # VALIDATE OPTIONAL EVIDENCE
        # ----------------------------------------------------

        evidence_valid = True

        if evidence_entered:

            evidence_valid = (
                evidence_form.is_valid()
            )

        # ----------------------------------------------------
        # SAVE EVERYTHING
        # ----------------------------------------------------

        if (
            investigation_valid
            and statement_valid
            and evidence_valid
        ):

            try:

                with transaction.atomic():

                    # ========================================
                    # 1. SAVE INVESTIGATION
                    # ========================================

                    investigation = (
                        investigation_form.save(
                            commit=False
                        )
                    )

                    investigation.case = case
                    investigation.investigating_officer = (
                        request.user
                    )

                    investigation.save()

                    # ========================================
                    # 2. SAVE STATEMENT IF PROVIDED
                    # ========================================

                    if statement_entered:

                        statement = (
                            statement_form.save(
                                commit=False
                            )
                        )

                        statement.case = case
                        statement.recorded_by = request.user

                        statement.save()

                    # ========================================
                    # 3. SAVE EVIDENCE IF PROVIDED
                    # ========================================

                    if evidence_entered:

                        evidence = (
                            evidence_form.save(
                                commit=False
                            )
                        )

                        evidence.case = case
                        evidence.collected_by = request.user

                        evidence.evidence_number = (
                            generate_evidence_number()
                        )

                        evidence.save()

                    # ========================================
                    # 4. UPDATE CASE STATUS
                    # ========================================

                    case.status = (
                        Case.Status.UNDER_INVESTIGATION
                    )

                    case.save(
                        update_fields=[
                            "status",
                            "updated_at",
                        ]
                    )

                # ============================================
                # SUCCESS
                # ============================================

                messages.success(
                    request,
                    (
                        f"Investigation for "
                        f"{case.case_number} "
                        f"has been saved successfully."
                    )
                )

                # ============================================
                # RETURN TO CASE DETAIL
                # ============================================

                return redirect(
                    "cases:detail",
                    case_id=case.id
                )

            except Exception:

                messages.error(
                    request,
                    (
                        "Unable to save the investigation. "
                        "Please check the information and try again."
                    )
                )

    # --------------------------------------------------------
    # GET REQUEST
    # --------------------------------------------------------

    else:

        investigation_form = InvestigationRecordForm(
            prefix="investigation",
            user=request.user,
            initial={
                "case": case.pk,
                "investigation_date": timezone.now().date(),
            }
        )

        statement_form = StatementForm(
            prefix="statement",
            initial={
                "case": case.pk,
                "statement_date": timezone.now().date(),
            }
        )

        evidence_form = EvidenceForm(
            prefix="evidence",
            initial={
                "case": case.pk,
                "date_collected": timezone.now(),
            }
        )

    # --------------------------------------------------------
    # DISPLAY INVESTIGATION WORKSPACE
    # --------------------------------------------------------

    return render(
        request,
        "investigation/workspace.html",
        {
            "case": case,
            "investigation_form": investigation_form,
            "statement_form": statement_form,
            "evidence_form": evidence_form,
        }
    )