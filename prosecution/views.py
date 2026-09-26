from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import User
from audit_logs.models import AuditLog
from cases.models import Case
from custody.models import CustodyRecord
from investigation.models import InvestigationRecord

from .forms import (
    ProsecutionProcessForm,
    ProsecutionReviewForm,
    ReturnCaseForm,
)
from .models import Prosecution


# ============================================================
# PROSECUTION NUMBER
# ============================================================

def generate_prosecution_number():

    year = timezone.now().year

    last_prosecution = (
        Prosecution.objects
        .filter(
            prosecution_number__startswith=f"PROS-{year}-"
        )
        .order_by("-id")
        .first()
    )

    if last_prosecution:

        try:

            last_number = int(
                last_prosecution.prosecution_number.rsplit(
                    "-",
                    1,
                )[1]
            )

            next_number = last_number + 1

        except (ValueError, IndexError):

            next_number = 1

    else:

        next_number = 1

    return f"PROS-{year}-{next_number:04d}"


# ============================================================
# AUDIT LOGGING
# ============================================================

def _log_prosecution_activity(
    request,
    action,
    prosecution,
    details="",
):

    try:

        AuditLog.objects.create(
            user=(
                request.user
                if request.user.is_authenticated
                else None
            ),
            action=action,
            target_model="Prosecution",
            target_id=str(prosecution.id),
            ip_address=request.META.get(
                "REMOTE_ADDR"
            ),
            details=details,
        )

    except Exception:
        # Audit failure should not destroy the main action.
        pass


# ============================================================
# CASE STATUS
# ============================================================

def _set_case_prosecution_status(case):

    # Your current Case model uses PROSECUTION.
    # The fallback supports an older version that may still
    # contain SUBMITTED_TO_PROSECUTION.

    status = getattr(
        Case.Status,
        "PROSECUTION",
        None,
    )

    if status is None:

        status = getattr(
            Case.Status,
            "SUBMITTED_TO_PROSECUTION",
        )

    case.status = status


# ============================================================
# FIND DIVISION ADMIN / PROSECUTION USER
# ============================================================

def find_prosecution_user(case):

    officer = getattr(
        case,
        "investigating_officer",
        None,
    )

    if officer is None:
        return None

    admins = (
        User.objects
        .filter(
            role="DIVISION_ADMIN",
            is_active=True,
        )
        .select_related(
            "division",
            "district",
            "station",
        )
    )

    station_id = case.station_id

    district_id = (
        case.station.district_id
        if case.station_id
        else None
    )

    # --------------------------------------------------------
    # 1. SAME DIVISION + SAME STATION
    # --------------------------------------------------------

    if officer.division_id and station_id:

        matches = admins.filter(
            division_id=officer.division_id,
            station_id=station_id,
        )

        if matches.count() == 1:
            return matches.first()

        if matches.count() > 1:

            raise ValueError(
                "More than one active Division Admin is "
                "assigned to the same division and station. "
                "Please correct the user assignments."
            )

    # --------------------------------------------------------
    # 2. SAME DIVISION + SAME DISTRICT
    # --------------------------------------------------------

    if officer.division_id and district_id:

        matches = admins.filter(
            division_id=officer.division_id,
            district_id=district_id,
        )

        if matches.count() == 1:
            return matches.first()

        if matches.count() > 1:

            raise ValueError(
                "More than one active Division Admin is "
                "assigned to the same division and district. "
                "Please correct the user assignments."
            )

    # --------------------------------------------------------
    # 3. SAME STATION
    # --------------------------------------------------------

    if station_id:

        matches = admins.filter(
            station_id=station_id,
        )

        if matches.count() == 1:
            return matches.first()

        if matches.count() > 1:

            raise ValueError(
                "More than one active Division Admin is "
                "assigned to this station. Please assign "
                "the officer to the correct division."
            )

    # --------------------------------------------------------
    # 4. SAME DISTRICT
    # --------------------------------------------------------

    if district_id:

        matches = admins.filter(
            district_id=district_id,
        )

        if matches.count() == 1:
            return matches.first()

        if matches.count() > 1:

            raise ValueError(
                "More than one active Division Admin is "
                "assigned to this district. Please assign "
                "the officer to the correct division."
            )

    return None


# ============================================================
# DIVISION ADMIN ACCESS
# ============================================================

def division_admin_can_access_case(
    user,
    prosecution,
):

    if user.role != "DIVISION_ADMIN":
        return False

    # The system assigned the prosecution to this user.
    if prosecution.prosecutor_id == user.id:
        return True

    return False


# ============================================================
# BASE PROSECUTION QUERY
# ============================================================

def get_user_prosecutions(user):

    queryset = (
        Prosecution.objects
        .select_related(
            "case",
            "case__station",
            "case__station__district",
            "case__suspect",
            "case__offence",
            "case__investigating_officer",
            "prosecutor",
            "investigation",
        )
        .order_by("-updated_at")
    )

    # --------------------------------------------------------
    # DIVISION ADMIN
    # --------------------------------------------------------

    if user.role == "DIVISION_ADMIN":

        return queryset.filter(
            prosecutor=user
        )

    # --------------------------------------------------------
    # PPC / SYSTEM ADMIN
    # --------------------------------------------------------

    if user.role == "ADMIN":

        return queryset

    # --------------------------------------------------------
    # POLICE OFFICER
    # --------------------------------------------------------

    if user.role == "OFFICER":

        return queryset.filter(
            case__investigating_officer=user
        )

    # --------------------------------------------------------
    # STATION COMMANDER
    # --------------------------------------------------------

    if user.role == "STATION_COMMANDER":

        return queryset.filter(
            case__station_id=user.station_id
        )

    return Prosecution.objects.none()


# ============================================================
# PROSECUTION DASHBOARD
# ============================================================

@login_required(login_url="accounts:login")
def prosecution_dashboard(request):

    user = request.user

    if user.role not in [
        "DIVISION_ADMIN",
        "ADMIN",
    ]:

        messages.error(
            request,
            (
                "You do not have permission to access "
                "the Prosecution Dashboard."
            )
        )

        return redirect(
            "accounts:dashboard"
        )

    prosecutions = get_user_prosecutions(
        user
    )

    # ========================================================
    # WORK QUEUE
    # ========================================================

    submitted_count = prosecutions.filter(
        status=Prosecution.Status.SUBMITTED
    ).count()

    under_review_count = prosecutions.filter(
        status=Prosecution.Status.UNDER_REVIEW
    ).count()

    returned_count = prosecutions.filter(
        status=Prosecution.Status.RETURNED
    ).count()

    ready_for_court_count = prosecutions.filter(
        status=Prosecution.Status.READY_FOR_COURT
    ).count()

    committal_count = prosecutions.filter(
        status=Prosecution.Status.COMMITTAL
    ).count()

    summary_trial_count = prosecutions.filter(
        status=Prosecution.Status.SUMMARY_TRIAL
    ).count()

    referred_count = prosecutions.filter(
        status=Prosecution.Status.REFERRED
    ).count()

    completed_count = prosecutions.filter(
        status=Prosecution.Status.COMPLETED
    ).count()

    # ========================================================
    # RECENT PROSECUTIONS
    # ========================================================

    recent_prosecutions = prosecutions[:10]

    # ========================================================
    # RECENT PROSECUTION ACTIVITY
    # ========================================================

    recent_activity = (
        AuditLog.objects
        .filter(
            target_model="Prosecution"
        )
        .select_related(
            "user"
        )
        .order_by(
            "-timestamp"
        )[:10]
    )

    return render(
        request,
        "prosecution/dashboard.html",
        {
            "submitted_count": submitted_count,
            "under_review_count": under_review_count,
            "returned_count": returned_count,
            "ready_for_court_count": ready_for_court_count,

            "committal_count": committal_count,
            "summary_trial_count": summary_trial_count,
            "referred_count": referred_count,
            "completed_count": completed_count,

            "recent_prosecutions": recent_prosecutions,
            "recent_activity": recent_activity,

            "prosecutions": prosecutions,
        }
    )


# ============================================================
# PROSECUTION LIST / WORK QUEUE
# ============================================================

@login_required(login_url="accounts:login")
def prosecution_list(request):

    user = request.user

    prosecutions = get_user_prosecutions(
        user
    )

    # ========================================================
    # STATUS FILTER
    # ========================================================

    selected_status = request.GET.get(
        "status",
        ""
    ).strip()

    valid_statuses = {
        value
        for value, label
        in Prosecution.Status.choices
    }

    if selected_status in valid_statuses:

        prosecutions = prosecutions.filter(
            status=selected_status
        )

    else:

        selected_status = ""

    # ========================================================
    # SEARCH
    # ========================================================

    search = request.GET.get(
        "q",
        ""
    ).strip()

    if search:

        prosecutions = prosecutions.filter(
            Q(
                prosecution_number__icontains=search
            )
            |
            Q(
                case__case_number__icontains=search
            )
            |
            Q(
                case__offence__title__icontains=search
            )
            |
            Q(
                case__station__name__icontains=search
            )
        )

    return render(
        request,
        "prosecution/prosecution_list.html",
        {
            "prosecutions": prosecutions,
            "selected_status": selected_status,
            "search": search,
            "status_choices": Prosecution.Status.choices,
        }
    )


# ============================================================
# PREPARE CASE FILE
# ============================================================

@login_required(login_url="accounts:login")
def prepare_case_file(request, case_id):

    case = get_object_or_404(
        Case.objects.select_related(
            "complaint",
            "suspect",
            "offence",
            "station",
            "station__district",
            "investigating_officer",
        ),
        pk=case_id,
        investigating_officer=request.user,
    )

    # --------------------------------------------------------
    # INVESTIGATION
    # --------------------------------------------------------

    investigations = (
        InvestigationRecord.objects
        .filter(
            case=case
        )
        .select_related(
            "investigating_officer"
        )
        .order_by(
            "-created_at"
        )
    )

    # --------------------------------------------------------
    # STATEMENTS
    # --------------------------------------------------------

    statements = (
        case.statements
        .select_related(
            "recorded_by"
        )
        .order_by(
            "-created_at"
        )
    )

    # --------------------------------------------------------
    # EVIDENCE
    # --------------------------------------------------------

    evidence = (
        case.evidence
        .select_related(
            "collected_by",
            "arrest",
        )
        .order_by(
            "-created_at"
        )
    )

    # --------------------------------------------------------
    # ARRESTS
    # --------------------------------------------------------

    arrests = (
        case.arrest_records
        .select_related(
            "suspect",
            "arresting_officer",
            "station",
        )
        .prefetch_related(
            "offences"
        )
        .order_by(
            "-arrest_datetime"
        )
    )

    # --------------------------------------------------------
    # WARRANTS
    # --------------------------------------------------------

    warrants = (
        case.warrants
        .select_related(
            "suspect",
            "station",
            "requested_by",
            "approved_by",
        )
        .order_by(
            "-created_at"
        )
    )

    # --------------------------------------------------------
    # CUSTODY
    # --------------------------------------------------------

    custody_records = (
        CustodyRecord.objects
        .filter(
            arrest__case=case
        )
        .select_related(
            "arrest",
            "arrest__suspect",
            "custody_officer",
        )
        .order_by(
            "-created_at"
        )
    )

    # ========================================================
    # COMPLETENESS
    # ========================================================

    has_case = True

    has_complaint = (
        case.complaint_id is not None
    )

    has_suspect = (
        case.suspect_id is not None
    )

    has_investigation = (
        investigations.exists()
    )

    has_statements = (
        statements.exists()
    )

    has_evidence = (
        evidence.exists()
    )

    has_arrest = (
        arrests.exists()
    )

    has_warrant = (
        warrants.exists()
    )

    has_custody = (
        custody_records.exists()
    )

    # The core case-file requirements are:
    # case + suspect + investigation.

    core_complete = (
        has_case
        and has_suspect
        and has_investigation
    )

    case_file_ready = core_complete

    # ========================================================
    # PREPARE
    # ========================================================

    if request.method == "POST":

        if not case_file_ready:

            messages.error(
                request,
                (
                    "The case file cannot be prepared because "
                    "required information is missing."
                )
            )

        else:

            case.status = (
                Case.Status.CASE_FILE_PREPARED
            )

            case.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            messages.success(
                request,
                (
                    f"Case {case.case_number} "
                    "has been prepared successfully."
                )
            )

            return redirect(
                "prosecution:prepare_case_file",
                case_id=case.id,
            )

    return render(
        request,
        "prosecution/prepare_case_file.html",
        {
            "case": case,

            "investigations": investigations,
            "statements": statements,
            "evidence": evidence,
            "arrests": arrests,
            "warrants": warrants,
            "custody_records": custody_records,

            "has_case": has_case,
            "has_complaint": has_complaint,
            "has_suspect": has_suspect,
            "has_investigation": has_investigation,
            "has_statements": has_statements,
            "has_evidence": has_evidence,
            "has_arrest": has_arrest,
            "has_warrant": has_warrant,
            "has_custody": has_custody,

            "core_complete": core_complete,
            "case_file_ready": case_file_ready,
        }
    )


# ============================================================
# SUBMIT CASE FILE
# ============================================================

@login_required(login_url="accounts:login")
def submit_case_file(request, case_id):

    if request.method != "POST":

        return redirect(
            "prosecution:prepare_case_file",
            case_id=case_id,
        )

    case = get_object_or_404(
        Case.objects.select_related(
            "suspect",
            "offence",
            "station",
            "station__district",
            "investigating_officer",
        ),
        pk=case_id,
        investigating_officer=request.user,
    )

    # ========================================================
    # CASE MUST BE PREPARED
    # ========================================================

    if case.status != Case.Status.CASE_FILE_PREPARED:

        messages.error(
            request,
            (
                "The case file must be prepared before "
                "it can be submitted to Prosecution."
            )
        )

        return redirect(
            "prosecution:prepare_case_file",
            case_id=case.id,
        )

    # ========================================================
    # LATEST INVESTIGATION
    # ========================================================

    latest_investigation = (
        case.investigations
        .select_related(
            "investigating_officer"
        )
        .order_by(
            "-created_at"
        )
        .first()
    )

    if not latest_investigation:

        messages.error(
            request,
            (
                "The case cannot be submitted because "
                "no investigation record exists."
            )
        )

        return redirect(
            "prosecution:prepare_case_file",
            case_id=case.id,
        )

    # ========================================================
    # FIND PROSECUTION USER
    # ========================================================

    try:

        prosecutor = find_prosecution_user(
            case
        )

    except ValueError as exc:

        messages.error(
            request,
            str(exc)
        )

        return redirect(
            "prosecution:prepare_case_file",
            case_id=case.id,
        )

    if prosecutor is None:

        messages.error(
            request,
            (
                "The case cannot be submitted because "
                "no active Division Admin / Prosecution "
                "user has been assigned to the appropriate "
                "division, station or district."
            )
        )

        return redirect(
            "prosecution:prepare_case_file",
            case_id=case.id,
        )

    # ========================================================
    # CREATE OR RESUBMIT
    # ========================================================

    try:

        with transaction.atomic():

            existing_prosecution = (
                Prosecution.objects
                .select_for_update()
                .filter(
                    case=case
                )
                .first()
            )

            # ------------------------------------------------
            # EXISTING PROSECUTION
            # ------------------------------------------------

            if existing_prosecution:

                # Only RETURNED cases can be resubmitted.
                if (
                    existing_prosecution.status
                    != Prosecution.Status.RETURNED
                ):

                    messages.warning(
                        request,
                        (
                            f"Case {case.case_number} has "
                            "already been submitted to "
                            "Prosecution."
                        )
                    )

                    return redirect(
                        "prosecution:list"
                    )

                # --------------------------------------------
                # RESUBMIT RETURNED CASE
                # --------------------------------------------

                existing_prosecution.investigation = (
                    latest_investigation
                )

                existing_prosecution.prosecutor = (
                    prosecutor
                )

                existing_prosecution.status = (
                    Prosecution.Status.SUBMITTED
                )

                existing_prosecution.case_file_complete = True

                existing_prosecution.investigation_reviewed = False
                existing_prosecution.evidence_reviewed = False
                existing_prosecution.arrest_reviewed = False
                existing_prosecution.warrant_reviewed = False
                existing_prosecution.custody_reviewed = False

                existing_prosecution.return_reason = ""

                existing_prosecution.decision = ""

                existing_prosecution.forwarded_to_court = False
                existing_prosecution.forwarded_date = None

                existing_prosecution.committal_status = (
                    Prosecution.ProceedingStatus.NOT_STARTED
                )
                existing_prosecution.committal_date = None
                existing_prosecution.committal_notes = ""

                existing_prosecution.summary_trial_status = (
                    Prosecution.ProceedingStatus.NOT_STARTED
                )
                existing_prosecution.summary_trial_date = None
                existing_prosecution.summary_trial_notes = ""

                existing_prosecution.save()

                prosecution = (
                    existing_prosecution
                )

                action_message = (
                    f"Case {case.case_number} has been "
                    "resubmitted to Prosecution."
                )

                audit_details = (
                    "Returned prosecution case was "
                    "corrected and resubmitted by the "
                    "investigating officer."
                )

            # ------------------------------------------------
            # FIRST SUBMISSION
            # ------------------------------------------------

            else:

                prosecution = Prosecution.objects.create(
                    case=case,

                    investigation=(
                        latest_investigation
                    ),

                    prosecution_number=(
                        generate_prosecution_number()
                    ),

                    prosecutor=prosecutor,

                    status=(
                        Prosecution.Status.SUBMITTED
                    ),

                    case_file_complete=True,

                    investigation_reviewed=False,
                    evidence_reviewed=False,
                    arrest_reviewed=False,
                    warrant_reviewed=False,
                    custody_reviewed=False,
                )

                action_message = (
                    f"Case {case.case_number} was "
                    "submitted to Prosecution successfully."
                )

                audit_details = (
                    "Police Officer submitted a prepared "
                    "case file for prosecution review."
                )

            # ------------------------------------------------
            # CASE STATUS
            # ------------------------------------------------

            _set_case_prosecution_status(
                case
            )

            case.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        _log_prosecution_activity(
            request,
            AuditLog.Action.CREATE
            if prosecution.created_at == prosecution.updated_at
            else AuditLog.Action.UPDATE,
            prosecution,
            audit_details,
        )

        messages.success(
            request,
            action_message,
        )

        return redirect(
            "prosecution:list"
        )

    except Exception as exc:

        messages.error(
            request,
            (
                "Unable to submit the case file. "
                "Please check the case information and "
                "Prosecution assignment."
            )
        )

        return redirect(
            "prosecution:prepare_case_file",
            case_id=case.id,
        )


# ============================================================
# REVIEW CASE
# ============================================================

@login_required(login_url="accounts:login")
def review(request, prosecution_id):

    prosecution = get_object_or_404(
        Prosecution.objects.select_related(
            "case",
            "case__complaint",
            "case__suspect",
            "case__offence",
            "case__station",
            "case__station__district",
            "case__investigating_officer",
            "prosecutor",
            "investigation",
            "investigation__investigating_officer",
        ),
        pk=prosecution_id,
    )

    user = request.user

    # ========================================================
    # ACCESS CONTROL
    # ========================================================

    if user.role == "DIVISION_ADMIN":

        if not division_admin_can_access_case(
            user,
            prosecution,
        ):

            messages.error(
                request,
                "You do not have access to this prosecution case."
            )

            return redirect(
                "prosecution:list"
            )

    elif user.role == "ADMIN":

        pass

    else:

        messages.error(
            request,
            (
                "Only Division Admin / Prosecution users "
                "can review prosecution cases."
            )
        )

        return redirect(
            "prosecution:list"
        )

    case = prosecution.case

    # ========================================================
    # GET CASE INFORMATION
    # ========================================================

    investigations = (
        InvestigationRecord.objects
        .filter(
            case=case
        )
        .select_related(
            "investigating_officer"
        )
        .order_by(
            "-created_at"
        )
    )

    statements = (
        case.statements
        .select_related(
            "recorded_by"
        )
        .order_by(
            "-created_at"
        )
    )

    evidence = (
        case.evidence
        .select_related(
            "collected_by",
            "arrest",
        )
        .order_by(
            "-created_at"
        )
    )

    arrests = (
        case.arrest_records
        .select_related(
            "suspect",
            "arresting_officer",
            "station",
        )
        .prefetch_related(
            "offences"
        )
        .order_by(
            "-arrest_datetime"
        )
    )

    warrants = (
        case.warrants
        .select_related(
            "suspect",
            "station",
            "requested_by",
            "approved_by",
        )
        .order_by(
            "-created_at"
        )
    )

    custody_records = (
        CustodyRecord.objects
        .filter(
            arrest__case=case
        )
        .select_related(
            "arrest",
            "arrest__suspect",
            "custody_officer",
        )
        .order_by(
            "-created_at"
        )
    )

    # ========================================================
    # START REVIEW
    # ========================================================

    if (
        request.method == "GET"
        and prosecution.status
        == Prosecution.Status.SUBMITTED
    ):

        prosecution.status = (
            Prosecution.Status.UNDER_REVIEW
        )

        prosecution.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        _log_prosecution_activity(
            request,
            AuditLog.Action.VIEW,
            prosecution,
            (
                "Division Admin opened the prosecution "
                "case for formal review."
            ),
        )

    # ========================================================
    # REVIEW FORM
    # ========================================================

    if request.method == "POST":

        form = ProsecutionReviewForm(
            request.POST,
            instance=prosecution,
        )

        if form.is_valid():

            prosecution = form.save(
                commit=False
            )

            all_requirements_reviewed = (
                prosecution.case_file_complete
                and prosecution.investigation_reviewed
                and prosecution.evidence_reviewed
                and prosecution.arrest_reviewed
                and prosecution.warrant_reviewed
                and prosecution.custody_reviewed
            )

            if all_requirements_reviewed:

                prosecution.status = (
                    Prosecution.Status.READY_FOR_COURT
                )

                message = (
                    f"Case {case.case_number} has passed "
                    "the prosecution review and is ready "
                    "for court processing."
                )

            else:

                prosecution.status = (
                    Prosecution.Status.UNDER_REVIEW
                )

                message = (
                    f"Review information for "
                    f"{case.case_number} has been saved."
                )

            prosecution.save()

            _set_case_prosecution_status(
                case
            )

            case.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            _log_prosecution_activity(
                request,
                AuditLog.Action.UPDATE,
                prosecution,
                (
                    "Prosecution review checklist updated. "
                    f"Status: {prosecution.get_status_display()}."
                ),
            )

            messages.success(
                request,
                message,
            )

            return redirect(
                "prosecution:review",
                prosecution_id=prosecution.id,
            )

    else:

        form = ProsecutionReviewForm(
            instance=prosecution,
        )

    return render(
        request,
        "prosecution/review.html",
        {
            "prosecution": prosecution,
            "case": case,

            "investigations": investigations,
            "statements": statements,
            "evidence": evidence,
            "arrests": arrests,
            "warrants": warrants,
            "custody_records": custody_records,

            "form": form,
        }
    )


# ============================================================
# PROSECUTION PROCESSING
# ============================================================

@login_required(login_url="accounts:login")
def process(request, prosecution_id):

    prosecution = get_object_or_404(
        Prosecution.objects.select_related(
            "case",
            "case__station",
            "case__station__district",
            "case__suspect",
            "case__offence",
            "prosecutor",
        ),
        pk=prosecution_id,
    )

    user = request.user

    # ========================================================
    # ACCESS CONTROL
    # ========================================================

    if user.role == "DIVISION_ADMIN":

        if not division_admin_can_access_case(
            user,
            prosecution,
        ):

            messages.error(
                request,
                "You do not have access to this prosecution case."
            )

            return redirect(
                "prosecution:list"
            )

    elif user.role == "ADMIN":

        pass

    else:

        messages.error(
            request,
            (
                "Only Division Admin / Prosecution users "
                "can process prosecution cases."
            )
        )

        return redirect(
            "prosecution:list"
        )

    # ========================================================
    # REVIEW MUST BE COMPLETED
    # ========================================================

    allowed_statuses = [
        Prosecution.Status.READY_FOR_COURT,
        Prosecution.Status.COMMITTAL,
        Prosecution.Status.SUMMARY_TRIAL,
        Prosecution.Status.REFERRED,
    ]

    if prosecution.status not in allowed_statuses:

        messages.error(
            request,
            (
                "The prosecution case must complete "
                "review before court processing can continue."
            )
        )

        return redirect(
            "prosecution:review",
            prosecution_id=prosecution.id,
        )

    # ========================================================
    # PROCESS FORM
    # ========================================================

    if request.method == "POST":

        form = ProsecutionProcessForm(
            request.POST,
            instance=prosecution,
        )

        if form.is_valid():

            prosecution = form.save(
                commit=False
            )

            committal_status = (
                prosecution.committal_status
            )

            summary_status = (
                prosecution.summary_trial_status
            )

            # ------------------------------------------------
            # DETERMINE PROSECUTION STATUS
            # ------------------------------------------------

            if prosecution.forwarded_to_court:

                prosecution.status = (
                    Prosecution.Status.REFERRED
                )

                prosecution.forwarded_date = (
                    prosecution.forwarded_date
                    or timezone.now()
                )

            elif (
                committal_status
                == Prosecution.ProceedingStatus.IN_PROGRESS
            ):

                prosecution.status = (
                    Prosecution.Status.COMMITTAL
                )

            elif (
                summary_status
                == Prosecution.ProceedingStatus.IN_PROGRESS
            ):

                prosecution.status = (
                    Prosecution.Status.SUMMARY_TRIAL
                )

            elif (
                committal_status
                == Prosecution.ProceedingStatus.COMPLETED
            ):

                prosecution.status = (
                    Prosecution.Status.REFERRED
                )

                prosecution.forwarded_to_court = True

                prosecution.forwarded_date = (
                    prosecution.forwarded_date
                    or timezone.now()
                )

            elif (
                summary_status
                == Prosecution.ProceedingStatus.COMPLETED
            ):

                prosecution.status = (
                    Prosecution.Status.REFERRED
                )

                prosecution.forwarded_to_court = True

                prosecution.forwarded_date = (
                    prosecution.forwarded_date
                    or timezone.now()
                )

            else:

                prosecution.status = (
                    Prosecution.Status.READY_FOR_COURT
                )

            prosecution.save()

            # ------------------------------------------------
            # MAIN CASE STATUS
            # ------------------------------------------------

            if prosecution.status in [
                Prosecution.Status.COMPLETED,
                Prosecution.Status.CLOSED,
            ]:

                prosecution.case.status = (
                    Case.Status.CLOSED
                )

            else:

                _set_case_prosecution_status(
                    prosecution.case
                )

            prosecution.case.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            _log_prosecution_activity(
                request,
                AuditLog.Action.UPDATE,
                prosecution,
                (
                    "Prosecution processing updated. "
                    f"Status: {prosecution.get_status_display()}."
                ),
            )

            messages.success(
                request,
                (
                    f"Prosecution processing for "
                    f"{prosecution.case.case_number} "
                    "has been updated."
                )
            )

            return redirect(
                "prosecution:process",
                prosecution_id=prosecution.id,
            )

    else:

        form = ProsecutionProcessForm(
            instance=prosecution,
        )

    return render(
        request,
        "prosecution/process.html",
        {
            "prosecution": prosecution,
            "case": prosecution.case,
            "form": form,
        }
    )


# ============================================================
# RETURN CASE FOR CORRECTION
# ============================================================

@login_required(login_url="accounts:login")
def return_case(request, prosecution_id):

    prosecution = get_object_or_404(
        Prosecution.objects.select_related(
            "case",
            "case__station",
            "case__station__district",
            "case__investigating_officer",
        ),
        pk=prosecution_id,
    )

    user = request.user

    # ========================================================
    # ACCESS CONTROL
    # ========================================================

    if user.role == "DIVISION_ADMIN":

        if not division_admin_can_access_case(
            user,
            prosecution,
        ):

            messages.error(
                request,
                "You do not have access to this prosecution case."
            )

            return redirect(
                "prosecution:list"
            )

    elif user.role == "ADMIN":

        pass

    else:

        messages.error(
            request,
            (
                "Only Division Admin / Prosecution users "
                "can return prosecution cases."
            )
        )

        return redirect(
            "prosecution:list"
        )

    # ========================================================
    # RETURNING IS ALLOWED BEFORE COURT PROCESSING
    # ========================================================

    allowed_statuses = [
        Prosecution.Status.SUBMITTED,
        Prosecution.Status.UNDER_REVIEW,
        Prosecution.Status.READY_FOR_COURT,
    ]

    if prosecution.status not in allowed_statuses:

        messages.error(
            request,
            (
                "This prosecution case cannot be returned "
                "at its current processing stage."
            )
        )

        return redirect(
            "prosecution:list"
        )

    # ========================================================
    # RETURN FORM
    # ========================================================

    if request.method == "POST":

        form = ReturnCaseForm(
            request.POST,
            instance=prosecution,
        )

        if form.is_valid():

            prosecution = form.save(
                commit=False
            )

            prosecution.status = (
                Prosecution.Status.RETURNED
            )

            # Reset review cycle
            prosecution.case_file_complete = False
            prosecution.investigation_reviewed = False
            prosecution.evidence_reviewed = False
            prosecution.arrest_reviewed = False
            prosecution.warrant_reviewed = False
            prosecution.custody_reviewed = False

            # Return the case from prosecution
            prosecution.forwarded_to_court = False
            prosecution.forwarded_date = None

            prosecution.save()

            # ------------------------------------------------
            # SEND CASE BACK TO OFFICER
            # ------------------------------------------------

            prosecution.case.status = (
                Case.Status.INVESTIGATION
            )

            prosecution.case.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            _log_prosecution_activity(
                request,
                AuditLog.Action.UPDATE,
                prosecution,
                (
                    "Prosecution case returned to the "
                    "investigating officer for correction. "
                    f"Reason: {prosecution.return_reason}"
                ),
            )

            messages.success(
                request,
                (
                    f"Case {prosecution.case.case_number} "
                    "has been returned to the Police Officer "
                    "for correction."
                )
            )

            return redirect(
                "prosecution:list"
            )

    else:

        form = ReturnCaseForm(
            instance=prosecution,
        )

    return render(
        request,
        "prosecution/return_case.html",
        {
            "prosecution": prosecution,
            "case": prosecution.case,
            "form": form,
        }
    )


# ============================================================
# COMMITTAL CHECKLIST
# ============================================================
#
# Uses the main prosecution processing form.
# The focus_section variable can later be used by the template
# to automatically open the Committal section.
# ============================================================

@login_required(login_url="accounts:login")
def committal_checklist(
    request,
    prosecution_id,
):

    prosecution = get_object_or_404(
        Prosecution.objects.select_related(
            "case",
            "case__station",
            "case__station__district",
            "prosecutor",
        ),
        pk=prosecution_id,
    )

    user = request.user

    if user.role == "DIVISION_ADMIN":

        if not division_admin_can_access_case(
            user,
            prosecution,
        ):

            messages.error(
                request,
                "You do not have access to this prosecution case."
            )

            return redirect(
                "prosecution:list"
            )

    elif user.role != "ADMIN":

        messages.error(
            request,
            (
                "Only Division Admin / Prosecution users "
                "can manage committal proceedings."
            )
        )

        return redirect(
            "prosecution:list"
        )

    if prosecution.status not in [
        Prosecution.Status.READY_FOR_COURT,
        Prosecution.Status.COMMITTAL,
        Prosecution.Status.REFERRED,
    ]:

        messages.error(
            request,
            (
                "The case must be ready for court before "
                "committal processing can begin."
            )
        )

        return redirect(
            "prosecution:review",
            prosecution_id=prosecution.id,
        )

    return render(
        request,
        "prosecution/process.html",
        {
            "prosecution": prosecution,
            "case": prosecution.case,
            "form": ProsecutionProcessForm(
                instance=prosecution
            ),
            "focus_section": "committal",
        }
    )


# ============================================================
# COMMITTAL STATUS
# ============================================================

@login_required(login_url="accounts:login")
def committal_status(
    request,
    prosecution_id,
):

    return committal_checklist(
        request,
        prosecution_id,
    )


# ============================================================
# SUMMARY TRIAL STATUS
# ============================================================

@login_required(login_url="accounts:login")
def summary_trial_status(
    request,
    prosecution_id,
):

    prosecution = get_object_or_404(
        Prosecution.objects.select_related(
            "case",
            "case__station",
            "case__station__district",
            "prosecutor",
        ),
        pk=prosecution_id,
    )

    user = request.user

    if user.role == "DIVISION_ADMIN":

        if not division_admin_can_access_case(
            user,
            prosecution,
        ):

            messages.error(
                request,
                "You do not have access to this prosecution case."
            )

            return redirect(
                "prosecution:list"
            )

    elif user.role != "ADMIN":

        messages.error(
            request,
            (
                "Only Division Admin / Prosecution users "
                "can manage summary trials."
            )
        )

        return redirect(
            "prosecution:list"
        )

    if prosecution.status not in [
        Prosecution.Status.READY_FOR_COURT,
        Prosecution.Status.SUMMARY_TRIAL,
        Prosecution.Status.REFERRED,
    ]:

        messages.error(
            request,
            (
                "The case must be ready for court before "
                "summary-trial processing can begin."
            )
        )

        return redirect(
            "prosecution:review",
            prosecution_id=prosecution.id,
        )

    return render(
        request,
        "prosecution/process.html",
        {
            "prosecution": prosecution,
            "case": prosecution.case,
            "form": ProsecutionProcessForm(
                instance=prosecution
            ),
            "focus_section": "summary_trial",
        }
    )