from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .services import (
    generate_blueshield_username,
    generate_sevispass_id,
    generate_temporary_password,
)

from .models import User
from .admin_forms import (
    AdminUserCreateForm,
    AdminUserUpdateForm,
)

from stations.models import PoliceStation
from records.models import ArrestRecord, CriminalOffence
from cases.models import Case
from suspects.models import Suspect
from audit_logs.models import AuditLog
from django.db.models import Count
from django.db.models.functions import TruncMonth

from complaints.models import Complaint

# ============================================================
# ADMIN ACCESS CONTROL
# ============================================================

def admin_required(view_func):
    """
    Allow only BlueShield PPC / System Administrator accounts.
    """

    @login_required
    def wrapper(request, *args, **kwargs):

        if request.user.role != "ADMIN":
            return render(
                request,
                "403.html",
                {
                    "message": (
                        "You do not have permission to access "
                        "the System Administration area."
                    )
                },
                status=403,
            )

        return view_func(request, *args, **kwargs)

    return wrapper


# ============================================================
# USER MANAGEMENT
# ============================================================

@admin_required
def admin_users(request):

    users = (
        User.objects
        .select_related(
            "station",
            "district",
            "division",
        )
        .order_by(
            "last_name",
            "first_name",
        )
    )

    context = {
        "users": users,
        "total_users": users.count(),
    }

    return render(
        request,
        "dashboards/admin/users.html",
        context,
    )


# ============================================================
# CREATE USER
# ============================================================

@admin_required
def admin_user_create(request):

    if request.method == "POST":

        form = AdminUserCreateForm(
            request.POST
        )

        if form.is_valid():

            with transaction.atomic():

                # ------------------------------------------------
                # Generate BlueShield username
                # ------------------------------------------------

                username = (
                    generate_blueshield_username()
                )

                # ------------------------------------------------
                # Generate temporary BlueShield password
                # ------------------------------------------------

                temporary_password = (
                    generate_temporary_password()
                )

                # ------------------------------------------------
                # Generate test SevisPass ID
                # ------------------------------------------------

                sevispass_id = (
                    generate_sevispass_id()
                )

                # ------------------------------------------------
                # Save user
                # ------------------------------------------------

                user = form.save(
                    commit=False
                )

                user.username = username

                user.set_password(
                    temporary_password
                )

                user.sevispass_id = (
                    sevispass_id
                )

                # User is NOT verified yet.
                # Verification happens after OTP verification.

                user.sevispass_verified = False

                user.sevispass_verified_at = None

                user.save()

            # ----------------------------------------------------
            # Show generated credentials once
            # ----------------------------------------------------

            messages.success(
                request,
                (
                    "User account created successfully. "
                    "The generated credentials are shown below."
                ),
            )

            return render(
                request,
                "dashboards/admin/user_form.html",
                {
                    "form": AdminUserCreateForm(),

                    "page_title": "User Created",

                    "submit_text": "Create User",

                    "created_user": user,

                    "generated_username": (
                        username
                    ),

                    "generated_password": (
                        temporary_password
                    ),

                    "generated_sevispass_id": (
                        sevispass_id
                    ),

                    "credentials_generated": True,
                },
            )

    else:

        form = AdminUserCreateForm()

    return render(
        request,
        "dashboards/admin/user_form.html",
        {
            "form": form,
            "page_title": "Create User",
            "submit_text": "Create User",
        },
    )


# ============================================================
# EDIT USER
# ============================================================

@admin_required
def admin_user_edit(request, user_id):

    user = get_object_or_404(
        User,
        id=user_id,
    )

    if request.method == "POST":

        form = AdminUserUpdateForm(
            request.POST,
            instance=user,
        )

        if form.is_valid():

            with transaction.atomic():

                user = form.save()

            messages.success(
                request,
                (
                    f"User account for "
                    f"{user.get_full_name() or user.username} "
                    "was updated successfully."
                ),
            )

            return redirect(
                "accounts:admin_users"
            )

    else:

        form = AdminUserUpdateForm(
            instance=user,
        )

    return render(
        request,
        "dashboards/admin/user_form.html",
        {
            "form": form,
            "user_account": user,
            "page_title": "Edit User",
            "submit_text": "Save Changes",
        },
    )


# ============================================================
# ACTIVATE / DEACTIVATE USER
# ============================================================

@admin_required
def admin_user_toggle(request, user_id):

    if request.method != "POST":

        return redirect(
            "accounts:admin_users"
        )

    user = get_object_or_404(
        User,
        id=user_id,
    )

    # Prevent administrator from deactivating themselves.

    if user.id == request.user.id:

        messages.error(
            request,
            "You cannot deactivate your own administrator account.",
        )

        return redirect(
            "accounts:admin_users"
        )

    user.is_active = not user.is_active

    user.save(
        update_fields=["is_active"]
    )

    if user.is_active:

        messages.success(
            request,
            (
                f"{user.get_full_name() or user.username} "
                "has been activated."
            ),
        )

    else:

        messages.warning(
            request,
            (
                f"{user.get_full_name() or user.username} "
                "has been deactivated."
            ),
        )

    return redirect(
        "accounts:admin_users"
    )


# ============================================================
# POLICE OFFICERS
# ============================================================

@admin_required
def admin_officers(request):

    officers = (
        User.objects
        .filter(
            role="OFFICER"
        )
        .select_related(
            "station",
            "district",
            "division",
        )
        .order_by(
            "last_name",
            "first_name",
        )
    )

    active_officers = officers.filter(
        is_active=True
    ).count()

    inactive_officers = officers.filter(
        is_active=False
    ).count()

    verified_officers = officers.filter(
        sevispass_verified=True
    ).count()

    context = {
        "officers": officers,
        "total_officers": officers.count(),
        "active_officers": active_officers,
        "inactive_officers": inactive_officers,
        "verified_officers": verified_officers,
    }

    return render(
        request,
        "dashboards/admin/officers.html",
        context,
    )

# ============================================================
# POLICE STATIONS
# ============================================================
@admin_required
def admin_stations(request):

    stations = (
        PoliceStation.objects
        .select_related(
            "district",
        )
        .order_by("name")
    )

    total_stations = stations.count()

    active_stations = stations.filter(
        is_active=True
    ).count()

    inactive_stations = stations.filter(
        is_active=False
    ).count()

    total_districts = (
        stations
        .values("district_id")
        .distinct()
        .count()
    )

    context = {
        "stations": stations,
        "total_stations": total_stations,
        "active_stations": active_stations,
        "inactive_stations": inactive_stations,
        "total_districts": total_districts,
    }

    return render(
        request,
        "dashboards/admin/stations.html",
        context,
    )
# ============================================================
# CRIMINAL OFFENCES
# ============================================================

@admin_required
def admin_offences(request):

    offences = (
        CriminalOffence.objects
        .order_by("code")
    )

    context = {
        "offences": offences,
        "total_offences": offences.count(),
    }

    return render(
        request,
        "dashboards/admin/offences.html",
        context,
    )


# ============================================================
# ARREST RECORDS
# ============================================================

@admin_required
def admin_arrests(request):

    arrests = (
        ArrestRecord.objects
        .select_related(
            "suspect",
            "case",
            "arresting_officer",
            "station",
        )
        .order_by(
            "-arrest_datetime"
        )
    )

    context = {
        "arrests": arrests,
        "total_arrests": arrests.count(),
    }

    return render(
        request,
        "dashboards/admin/arrests.html",
        context,
    )


# ============================================================
# CASES
# ============================================================

@admin_required
def admin_cases(request):

    cases = (
        Case.objects
        .select_related(
            "suspect",
            "station",
            "investigating_officer",
            "offence",
        )
        .order_by(
            "-created_at"
        )
    )

    context = {
        "cases": cases,
        "total_cases": cases.count(),
    }

    return render(
        request,
        "dashboards/admin/cases.html",
        context,
    )


# ============================================================
# SUSPECTS
# ============================================================

@admin_required
def admin_suspects(request):

    suspects = (
        Suspect.objects
        .select_related(
            "station",
            "district",
            "province",
            "registered_by",
        )
        .order_by(
            "-created_at"
        )
    )

    context = {
        "suspects": suspects,
        "total_suspects": suspects.count(),
    }

    return render(
        request,
        "dashboards/admin/suspects.html",
        context,
    )


# ============================================================
# AUDIT LOGS
# ============================================================

# ============================================================
# AUDIT LOGS
# ============================================================

@admin_required
def admin_audit_logs(request):

    audit_logs = (
        AuditLog.objects
        .select_related("user")
        .order_by(
            "-timestamp"
        )
    )

    total_audit_logs = audit_logs.count()

    login_logs = audit_logs.filter(
        action=AuditLog.Action.LOGIN
    ).count()

    create_logs = audit_logs.filter(
        action=AuditLog.Action.CREATE
    ).count()

    update_logs = audit_logs.filter(
        action=AuditLog.Action.UPDATE
    ).count()

    delete_logs = audit_logs.filter(
        action=AuditLog.Action.DELETE
    ).count()

    context = {
        "audit_logs": audit_logs,
        "total_audit_logs": total_audit_logs,
        "login_logs": login_logs,
        "create_logs": create_logs,
        "update_logs": update_logs,
        "delete_logs": delete_logs,
    }

    return render(
        request,
        "dashboards/admin/audit_logs.html",
        context,
    )

# ============================================================
# STATISTICS
# ============================================================

# ============================================================
# STATISTICS
# ============================================================

@admin_required
def admin_statistics(request):

    # ========================================================
    # OVERALL TOTALS
    # ========================================================

    total_users = User.objects.count()

    total_officers = User.objects.filter(
        role="OFFICER"
    ).count()

    total_division_admins = User.objects.filter(
        role="DIVISION_ADMIN"
    ).count()

    total_station_commanders = User.objects.filter(
        role="STATION_COMMANDER"
    ).count()

    total_stations = PoliceStation.objects.count()

    total_active_stations = PoliceStation.objects.filter(
        is_active=True
    ).count()

    total_complaints = Complaint.objects.count()

    total_cases = Case.objects.count()

    total_suspects = Suspect.objects.count()

    total_arrests = ArrestRecord.objects.count()

    total_offences = CriminalOffence.objects.count()

    # ========================================================
    # CASE STATUS
    # ========================================================

    closed_cases = Case.objects.filter(
        status=Case.Status.CLOSED
    ).count()

    active_cases = (
        total_cases - closed_cases
    )

    case_status_data = (
        Case.objects
        .values("status")
        .annotate(
            total=Count("id")
        )
        .order_by("-total")
    )

    case_status_stats = []

    status_labels = dict(
        Case.Status.choices
    )

    for item in case_status_data:

        case_status_stats.append(
            {
                "status": item["status"],
                "label": status_labels.get(
                    item["status"],
                    item["status"],
                ),
                "total": item["total"],
            }
        )

    # ========================================================
    # OFFENCE STATISTICS
    # ========================================================

    offence_stats = (
    Case.objects
    .filter(
        offence__isnull=False
    )
    .values(
        "offence__code",
        "offence__title",
    )
    .annotate(
        total=Count("id")
    )
    .order_by(
        "-total"
    )[:10]
)
    # ========================================================
    # DISTRICT CASE STATISTICS
    # ========================================================

    district_case_stats = (
        Case.objects
        .filter(
            station__isnull=False,
            station__district__isnull=False,
        )
        .values(
            "station__district__name"
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "-total"
        )
    )

    # ========================================================
    # DISTRICT ARREST STATISTICS
    # ========================================================

    district_arrest_stats = (
        ArrestRecord.objects
        .filter(
            station__isnull=False,
            station__district__isnull=False,
        )
        .values(
            "station__district__name"
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "-total"
        )
    )

    # ========================================================
    # POLICE STATION STATISTICS
    # ========================================================

    station_case_stats = (
        Case.objects
        .filter(
            station__isnull=False
        )
        .values(
            "station__id",
            "station__name",
            "station__district__name",
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "-total"
        )
    )

    station_arrest_stats = (
        ArrestRecord.objects
        .filter(
            station__isnull=False
        )
        .values(
            "station__id",
            "station__name",
            "station__district__name",
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "-total"
        )
    )

    # --------------------------------------------------------
    # Combine station cases + arrests
    # --------------------------------------------------------

    station_statistics = {}

    for station in station_case_stats:

        station_id = station["station__id"]

        station_statistics[station_id] = {
            "station": station["station__name"],
            "district": station[
                "station__district__name"
            ],
            "cases": station["total"],
            "arrests": 0,
        }

    for station in station_arrest_stats:

        station_id = station["station__id"]

        if station_id not in station_statistics:

            station_statistics[station_id] = {
                "station": station["station__name"],
                "district": station[
                    "station__district__name"
                ],
                "cases": 0,
                "arrests": 0,
            }

        station_statistics[
            station_id
        ]["arrests"] = station["total"]

    station_statistics = list(
        station_statistics.values()
    )

    station_statistics.sort(
        key=lambda item: (
            item["cases"] + item["arrests"]
        ),
        reverse=True,
    )

    # ========================================================
    # MONTHLY STATISTICS
    # ========================================================

    monthly_case_stats = (
        Case.objects
        .annotate(
            month=TruncMonth(
                "created_at"
            )
        )
        .values("month")
        .annotate(
            total=Count("id")
        )
        .order_by("month")
    )

    monthly_arrest_stats = (
        ArrestRecord.objects
        .annotate(
            month=TruncMonth(
                "arrest_datetime"
            )
        )
        .values("month")
        .annotate(
            total=Count("id")
        )
        .order_by("month")
    )

    monthly_case_data = []

    for item in monthly_case_stats:

        month = item["month"]

        if month:

            monthly_case_data.append(
                {
                    "month": month.strftime(
                        "%b %Y"
                    ),
                    "total": item["total"],
                }
            )

    monthly_arrest_data = []

    for item in monthly_arrest_stats:

        month = item["month"]

        if month:

            monthly_arrest_data.append(
                {
                    "month": month.strftime(
                        "%b %Y"
                    ),
                    "total": item["total"],
                }
            )

    # ========================================================
    # RECENT ACTIVITY
    # ========================================================

    recent_arrests = (
        ArrestRecord.objects
        .select_related(
            "suspect",
            "case",
            "station",
        )
        .order_by(
            "-arrest_datetime"
        )[:10]
    )

    recent_cases = (
        Case.objects
        .select_related(
            "suspect",
            "station",
            "offence",
        )
        .order_by(
            "-created_at"
        )[:10]
    )

    recent_complaints = (
        Complaint.objects
        .select_related(
            "station",
            "reported_by",
        )
        .order_by(
            "-created_at"
        )[:10]
    )

    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        # ----------------------------------------------------
        # Overall totals
        # ----------------------------------------------------

        "total_users": total_users,
        "total_officers": total_officers,
        "total_division_admins": total_division_admins,
        "total_station_commanders": total_station_commanders,

        "total_stations": total_stations,
        "total_active_stations": total_active_stations,

        "total_complaints": total_complaints,
        "total_cases": total_cases,
        "total_suspects": total_suspects,
        "total_arrests": total_arrests,
        "total_offences": total_offences,

        # ----------------------------------------------------
        # Case statistics
        # ----------------------------------------------------

        "active_cases": active_cases,
        "closed_cases": closed_cases,
        "case_status_stats": case_status_stats,

        # ----------------------------------------------------
        # Crime statistics
        # ----------------------------------------------------

        "offence_stats": offence_stats,

        # ----------------------------------------------------
        # District statistics
        # ----------------------------------------------------

        "district_case_stats": district_case_stats,
        "district_arrest_stats": district_arrest_stats,

        # ----------------------------------------------------
        # Station statistics
        # ----------------------------------------------------

        "station_statistics": station_statistics,

        # ----------------------------------------------------
        # Monthly statistics
        # ----------------------------------------------------

        "monthly_case_data": monthly_case_data,
        "monthly_arrest_data": monthly_arrest_data,

        # ----------------------------------------------------
        # Recent activity
        # ----------------------------------------------------

        "recent_arrests": recent_arrests,
        "recent_cases": recent_cases,
        "recent_complaints": recent_complaints,
    }

    return render(
        request,
        "dashboards/admin/statistics.html",
        context,
    )

# ============================================================
# SYSTEM SETTINGS
# ============================================================

@admin_required
def admin_settings(request):

    return render(
        request,
        "dashboards/admin/settings.html",
    )