import csv
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from cases.models import Case
from complaints.models import Complaint
from evidence.models import Evidence
from prosecution.models import Prosecution
from records.models import ArrestRecord
from suspects.models import Suspect
from warrant.models import Warrant
from stations.models import District, PoliceStation

from .forms import MonthlyReportForm
from .models import MonthlyReport


# ============================================================
# ROLE HELPERS
# ============================================================

def ppc_only(view_func):
    """
    Only PPC / System Administrator can access the PPC reports.
    """

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("accounts:login")

        if request.user.role != "ADMIN":
            messages.error(
                request,
                "Only the PPC / System Administrator can access this page."
            )
            return redirect("accounts:dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper


def commander_only(view_func):
    """
    Only Station Commanders can access Station Commander reports.
    """

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("accounts:login")

        if request.user.role != "STATION_COMMANDER":
            messages.error(
                request,
                "Only Police Station Commanders can access this page."
            )
            return redirect("accounts:dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper


# ============================================================
# MONTHLY STATISTICS
# ============================================================

def calculate_monthly_statistics(station, year, month):
    """
    Calculate BlueShield statistics for one station and one month.

    Statistics are calculated automatically from existing records.
    """

    start_date = datetime(year, month, 1)

    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    start_date = timezone.make_aware(start_date)
    end_date = timezone.make_aware(end_date)

    # --------------------------------------------------------
    # COMPLAINTS
    # --------------------------------------------------------

    total_complaints = Complaint.objects.filter(
        station=station,
        created_at__gte=start_date,
        created_at__lt=end_date,
    ).count()

    # --------------------------------------------------------
    # CASES
    # --------------------------------------------------------

    station_cases = Case.objects.filter(
        station=station,
        created_at__gte=start_date,
        created_at__lt=end_date,
    )

    total_cases = station_cases.count()

    total_open_cases = station_cases.filter(
        status=Case.Status.OPEN
    ).count()

    total_investigation_cases = station_cases.filter(
        status=Case.Status.UNDER_INVESTIGATION
    ).count()

    total_warrant_requests = Warrant.objects.filter(
        station=station,
        created_at__gte=start_date,
        created_at__lt=end_date,
    ).count()

    # --------------------------------------------------------
    # ARRESTS
    # --------------------------------------------------------

    station_arrests = ArrestRecord.objects.filter(
        station=station,
        arrest_datetime__gte=start_date,
        arrest_datetime__lt=end_date,
    )

    total_arrests = station_arrests.count()

    total_in_custody = station_arrests.filter(
        custody_status=ArrestRecord.CustodyStatus.DETAINED
    ).count()

    total_released = station_arrests.filter(
        custody_status=ArrestRecord.CustodyStatus.RELEASED_NO_CHARGE
    ).count()

    # --------------------------------------------------------
    # EVIDENCE
    # --------------------------------------------------------

    total_evidence = Evidence.objects.filter(
        case__station=station,
        created_at__gte=start_date,
        created_at__lt=end_date,
    ).count()

    # --------------------------------------------------------
    # PROSECUTION
    # --------------------------------------------------------

    total_prosecution_cases = Prosecution.objects.filter(
        case__station=station,
        submission_date__gte=start_date,
        submission_date__lt=end_date,
    ).count()

    return {
        "total_complaints": total_complaints,
        "total_cases": total_cases,
        "total_open_cases": total_open_cases,
        "total_investigation_cases": total_investigation_cases,
        "total_warrant_requests": total_warrant_requests,
        "total_arrests": total_arrests,
        "total_in_custody": total_in_custody,
        "total_released": total_released,
        "total_evidence": total_evidence,
        "total_prosecution_cases": total_prosecution_cases,
    }


def update_monthly_report_statistics(report):
    """
    Update all automatically calculated statistics for a report.
    """

    statistics = calculate_monthly_statistics(
        report.station,
        report.year,
        report.month,
    )

    for field, value in statistics.items():
        setattr(report, field, value)

    report.save(
        update_fields=list(statistics.keys()) + ["updated_at"]
    )

    return report


# ============================================================
# STATION COMMANDER
# ============================================================

@login_required(login_url="accounts:login")
@commander_only
def commander_reports(request):
    """
    Station Commander sees only reports belonging to
    their assigned station.
    """

    reports = MonthlyReport.objects.filter(
        station=request.user.station
    ).select_related(
        "district",
        "station",
        "prepared_by",
        "reviewed_by",
    )

    return render(
        request,
        "reports/commander_reports.html",
        {
            "reports": reports,
        }
    )


# ============================================================
# CREATE MONTHLY REPORT
# ============================================================

@login_required(login_url="accounts:login")
@commander_only
def create_report(request):

    if not request.user.station:
        messages.error(
            request,
            "Your account is not assigned to a police station."
        )
        return redirect("accounts:dashboard")

    if not request.user.district:
        messages.error(
            request,
            "Your account is not assigned to a district."
        )
        return redirect("accounts:dashboard")

    if request.method == "POST":

        form = MonthlyReportForm(request.POST)

        if form.is_valid():

            year = form.cleaned_data["year"]
            month = form.cleaned_data["month"]

            # ------------------------------------------------
            # Prevent duplicate monthly report
            # ------------------------------------------------

            existing = MonthlyReport.objects.filter(
                year=year,
                month=month,
                station=request.user.station,
            ).first()

            if existing:
                messages.warning(
                    request,
                    (
                        f"A monthly report already exists for "
                        f"{existing.month_name} {existing.year}."
                    )
                )

                return redirect(
                    "reports:detail",
                    report_id=existing.id
                )

            report = form.save(commit=False)

            # ------------------------------------------------
            # SECURITY:
            # Automatically assign station/district/user
            # ------------------------------------------------

            report.station = request.user.station
            report.district = request.user.district
            report.prepared_by = request.user
            report.status = MonthlyReport.Status.DRAFT

            report.save()

            # ------------------------------------------------
            # Calculate statistics automatically
            # ------------------------------------------------

            update_monthly_report_statistics(report)

            messages.success(
                request,
                f"Monthly report {report.report_number} created successfully."
            )

            return redirect(
                "reports:detail",
                report_id=report.id
            )

    else:

        current_date = timezone.localdate()

        form = MonthlyReportForm(
            initial={
                "year": current_date.year,
                "month": current_date.month,
            }
        )

    return render(
        request,
        "reports/create.html",
        {
            "form": form,
        }
    )


# ============================================================
# MONTHLY REPORT DETAIL
# ============================================================

@login_required(login_url="accounts:login")
def report_detail(request, report_id):

    report = get_object_or_404(
        MonthlyReport.objects.select_related(
            "district",
            "station",
            "prepared_by",
            "reviewed_by",
        ),
        id=report_id,
    )

    # --------------------------------------------------------
    # Station Commander can only see own station
    # --------------------------------------------------------

    if request.user.role == "STATION_COMMANDER":

        if report.station_id != request.user.station_id:
            messages.error(
                request,
                "You do not have permission to view this report."
            )
            return redirect("reports:commander_reports")

    # --------------------------------------------------------
    # PPC can see all reports
    # --------------------------------------------------------

    elif request.user.role != "ADMIN":

        messages.error(
            request,
            "You do not have permission to view this report."
        )

        return redirect("accounts:dashboard")

    return render(
        request,
        "reports/detail.html",
        {
            "report": report,
        }
    )


# ============================================================
# SUBMIT MONTHLY REPORT TO PPC
# ============================================================

@login_required(login_url="accounts:login")
@commander_only
@require_POST
def submit_report(request, report_id):

    report = get_object_or_404(
        MonthlyReport,
        id=report_id,
        station=request.user.station,
    )

    # --------------------------------------------------------
    # Only draft or returned reports can be submitted
    # --------------------------------------------------------

    if report.status not in [
        MonthlyReport.Status.DRAFT,
        MonthlyReport.Status.RETURNED,
    ]:
        messages.error(
            request,
            "This report cannot be submitted in its current status."
        )

        return redirect(
            "reports:detail",
            report_id=report.id
        )

    # --------------------------------------------------------
    # Refresh automatic statistics before submission
    # --------------------------------------------------------

    update_monthly_report_statistics(report)

    report.status = MonthlyReport.Status.SUBMITTED
    report.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    messages.success(
        request,
        (
            f"Report {report.report_number} has been submitted "
            "to the PPC for review."
        )
    )

    return redirect(
        "reports:detail",
        report_id=report.id
    )


# ============================================================
# PPC REPORTS
# ============================================================

@login_required(login_url="accounts:login")
@ppc_only
def ppc_reports(request):

    reports = MonthlyReport.objects.select_related(
        "district",
        "station",
        "prepared_by",
        "reviewed_by",
    )

    status_filter = request.GET.get("status")

    if status_filter:
        reports = reports.filter(
            status=status_filter
        )

    return render(
        request,
        "reports/ppc_reports.html",
        {
            "reports": reports,
            "status_choices": MonthlyReport.Status.choices,
            "selected_status": status_filter,
        }
    )


# ============================================================
# PPC REVIEW
# ============================================================

@login_required(login_url="accounts:login")
@ppc_only
def review_report(request, report_id):

    report = get_object_or_404(
        MonthlyReport.objects.select_related(
            "district",
            "station",
            "prepared_by",
        ),
        id=report_id,
    )

    if request.method == "POST":

        action = request.POST.get("action")
        review_comments = request.POST.get(
            "review_comments",
            ""
        ).strip()

        # ----------------------------------------------------
        # APPROVE
        # ----------------------------------------------------

        if action == "approve":

            report.status = MonthlyReport.Status.APPROVED
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.review_comments = review_comments

            report.save(
                update_fields=[
                    "status",
                    "reviewed_by",
                    "reviewed_at",
                    "review_comments",
                    "updated_at",
                ]
            )

            messages.success(
                request,
                (
                    f"Report {report.report_number} has been "
                    "approved successfully."
                )
            )

        # ----------------------------------------------------
        # REVIEWED
        # ----------------------------------------------------

        elif action == "review":

            report.status = MonthlyReport.Status.REVIEWED
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.review_comments = review_comments

            report.save(
                update_fields=[
                    "status",
                    "reviewed_by",
                    "reviewed_at",
                    "review_comments",
                    "updated_at",
                ]
            )

            messages.success(
                request,
                f"Report {report.report_number} has been marked as reviewed."
            )

        # ----------------------------------------------------
        # RETURN
        # ----------------------------------------------------

        elif action == "return":

            if not review_comments:

                messages.error(
                    request,
                    "Please provide review comments when returning a report."
                )

                return redirect(
                    "reports:review",
                    report_id=report.id
                )

            report.status = MonthlyReport.Status.RETURNED
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.review_comments = review_comments

            report.save(
                update_fields=[
                    "status",
                    "reviewed_by",
                    "reviewed_at",
                    "review_comments",
                    "updated_at",
                ]
            )

            messages.warning(
                request,
                (
                    f"Report {report.report_number} has been returned "
                    "to the Station Commander for correction."
                )
            )

        else:

            messages.error(
                request,
                "Invalid review action."
            )

        return redirect(
            "reports:review",
            report_id=report.id
        )

    return render(
        request,
        "reports/review.html",
        {
            "report": report,
        }
    )


# ============================================================
# PPC REPORTS DASHBOARD
# ============================================================

@login_required(login_url="accounts:login")
@ppc_only
def reports_dashboard(request):

    context = {

        "total_arrests": ArrestRecord.objects.count(),

        "total_cases": Case.objects.count(),

        "total_suspects": Suspect.objects.count(),

        "total_warrants": Warrant.objects.count(),

        "total_prosecutions": Prosecution.objects.count(),

        "detained": ArrestRecord.objects.filter(
            custody_status=ArrestRecord.CustodyStatus.DETAINED
        ).count(),

        "transferred": ArrestRecord.objects.filter(
            custody_status=ArrestRecord.CustodyStatus.TRANSFERRED
        ).count(),

        "monthly_reports": MonthlyReport.objects.count(),

        "submitted_reports": MonthlyReport.objects.filter(
            status=MonthlyReport.Status.SUBMITTED
        ).count(),

        "approved_reports": MonthlyReport.objects.filter(
            status=MonthlyReport.Status.APPROVED
        ).count(),

        "returned_reports": MonthlyReport.objects.filter(
            status=MonthlyReport.Status.RETURNED
        ).count(),
    }

    return render(
        request,
        "reports/dashboard.html",
        context
    )


# ============================================================
# ARREST REPORT
# ============================================================

@login_required(login_url="accounts:login")
@ppc_only
def arrest_report(request):

    arrests = (
        ArrestRecord.objects
        .select_related(
            "suspect",
            "case",
            "arresting_officer",
            "station",
        )
        .prefetch_related("offences")
        .order_by("-arrest_datetime")
    )

    return render(
        request,
        "reports/arrest_report.html",
        {
            "arrests": arrests
        }
    )


# ============================================================
# ARREST PDF
# ============================================================

@login_required(login_url="accounts:login")
@ppc_only
def arrest_report_pdf(request):

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="blueshield_arrest_report.pdf"'

    document = SimpleDocTemplate(
        response,
        pagesize=landscape(A4)
    )

    data = [
        [
            "Arrest ID",
            "Case",
            "Suspect",
            "Station",
            "Officer",
            "Date",
            "Custody"
        ]
    ]

    arrests = (
        ArrestRecord.objects
        .select_related(
            "suspect",
            "case",
            "arresting_officer",
            "station"
        )
        .order_by("-arrest_datetime")
    )

    for arrest in arrests:

        officer_name = "-"

        if arrest.arresting_officer:
            officer_name = (
                arrest.arresting_officer.get_full_name()
                or arrest.arresting_officer.username
            )

        data.append([
            arrest.arrest_tracking_id,
            arrest.case.case_number if arrest.case else "-",
            arrest.suspect.full_name,
            arrest.station.name,
            officer_name,
            arrest.arrest_datetime.strftime("%d/%m/%Y"),
            arrest.get_custody_status_display(),
        ])

    table = Table(
        data,
        repeatRows=1
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.grey
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7
            ),
        ])
    )

    document.build([table])

    return response


# ============================================================
# ARREST CSV
# ============================================================

@login_required(login_url="accounts:login")
@ppc_only
def arrest_report_csv(request):

    response = HttpResponse(
        content_type="text/csv"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="blueshield_arrest_report.csv"'

    writer = csv.writer(response)

    writer.writerow([
        "Arrest Tracking ID",
        "Case Number",
        "Suspect",
        "Station",
        "Officer",
        "Arrest Date",
        "Custody Status"
    ])

    arrests = (
        ArrestRecord.objects
        .select_related(
            "suspect",
            "case",
            "arresting_officer",
            "station"
        )
        .order_by("-arrest_datetime")
    )

    for arrest in arrests:

        officer_name = "-"

        if arrest.arresting_officer:
            officer_name = (
                arrest.arresting_officer.get_full_name()
                or arrest.arresting_officer.username
            )

        writer.writerow([
            arrest.arrest_tracking_id,
            arrest.case.case_number if arrest.case else "",
            arrest.suspect.full_name,
            arrest.station.name,
            officer_name,
            arrest.arrest_datetime.strftime("%d/%m/%Y"),
            arrest.get_custody_status_display(),
        ])

    return response


# ============================================================
# CRIME REPORT
# ============================================================

@login_required(login_url="accounts:login")
@ppc_only
def crime_report(request):

    cases = (
        Case.objects
        .select_related(
            "offence",
            "suspect",
            "station",
            "station__district",
            "investigating_officer"
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "reports/crime_report.html",
        {
            "cases": cases
        }
    )


# ============================================================
# CRIME PDF
# ============================================================

@login_required(login_url="accounts:login")
@ppc_only
def crime_report_pdf(request):

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="blueshield_crime_report.pdf"'

    document = SimpleDocTemplate(
        response,
        pagesize=landscape(A4)
    )

    data = [[
        "Case Number",
        "Offence",
        "Suspect",
        "District",
        "Station",
        "Location",
        "Status"
    ]]

    cases = (
        Case.objects
        .select_related(
            "offence",
            "suspect",
            "station",
            "station__district"
        )
        .order_by("-created_at")
    )

    for case in cases:

        data.append([
            case.case_number,
            case.offence.title,
            case.suspect.full_name if case.suspect else "-",
            case.station.district.name,
            case.station.name,
            case.location,
            case.get_status_display(),
        ])

    table = Table(
        data,
        repeatRows=1
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.grey
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7
            ),
        ])
    )

    document.build([table])

    return response


# ============================================================
# CRIME CSV
# ============================================================

@login_required(login_url="accounts:login")
@ppc_only
def crime_report_csv(request):

    response = HttpResponse(
        content_type="text/csv"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="blueshield_crime_report.csv"'

    writer = csv.writer(response)

    writer.writerow([
        "Case Number",
        "Offence",
        "Suspect",
        "District",
        "Station",
        "Location",
        "Status"
    ])

    cases = (
        Case.objects
        .select_related(
            "offence",
            "suspect",
            "station",
            "station__district"
        )
        .order_by("-created_at")
    )

    for case in cases:

        writer.writerow([
            case.case_number,
            case.offence.title,
            case.suspect.full_name if case.suspect else "",
            case.station.district.name,
            case.station.name,
            case.location,
            case.get_status_display(),
        ])

    return response


# ============================================================
# CUSTODY / PRISON REPORT
# ============================================================

@login_required(login_url="accounts:login")
@ppc_only
def custody_report(request):

    arrests = (
        ArrestRecord.objects
        .select_related(
            "suspect",
            "case",
            "station"
        )
        .order_by("-arrest_datetime")
    )

    return render(
        request,
        "reports/custody_report.html",
        {
            "arrests": arrests
        }
    )


# ============================================================
# CUSTODY PDF
# ============================================================

@login_required(login_url="accounts:login")
@ppc_only
def custody_report_pdf(request):

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="blueshield_custody_report.pdf"'

    document = SimpleDocTemplate(
        response,
        pagesize=landscape(A4)
    )

    data = [[
        "Arrest ID",
        "Case",
        "Suspect",
        "Station",
        "Custody Status",
        "Cell",
        "Bail Amount"
    ]]

    arrests = (
        ArrestRecord.objects
        .select_related(
            "suspect",
            "case",
            "station"
        )
        .order_by("-arrest_datetime")
    )

    for arrest in arrests:

        data.append([
            arrest.arrest_tracking_id,
            arrest.case.case_number if arrest.case else "-",
            arrest.suspect.full_name,
            arrest.station.name,
            arrest.get_custody_status_display(),
            arrest.cell_number or "-",
            (
                str(arrest.bail_amount_pgk)
                if arrest.bail_amount_pgk is not None
                else "-"
            ),
        ])

    table = Table(
        data,
        repeatRows=1
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.grey
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7
            ),
        ])
    )

    document.build([table])

    return response


# ============================================================
# CUSTODY CSV
# ============================================================

@login_required(login_url="accounts:login")
@ppc_only
def custody_report_csv(request):

    response = HttpResponse(
        content_type="text/csv"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="blueshield_custody_report.csv"'

    writer = csv.writer(response)

    writer.writerow([
        "Arrest ID",
        "Case Number",
        "Suspect",
        "Station",
        "Custody Status",
        "Cell Number",
        "Bail Amount PGK"
    ])

    arrests = (
        ArrestRecord.objects
        .select_related(
            "suspect",
            "case",
            "station"
        )
        .order_by("-arrest_datetime")
    )

    for arrest in arrests:

        writer.writerow([
            arrest.arrest_tracking_id,
            arrest.case.case_number if arrest.case else "",
            arrest.suspect.full_name,
            arrest.station.name,
            arrest.get_custody_status_display(),
            arrest.cell_number or "",
            (
                arrest.bail_amount_pgk
                if arrest.bail_amount_pgk is not None
                else ""
            ),
        ])

    return response


# ============================================================
# CRIME ANALYTICS
# ============================================================

@login_required(login_url="accounts:login")
@ppc_only
def analytics(request):

    district_data = (
        Case.objects
        .values(
            "station__district__name"
        )
        .annotate(
            case_count=Count("id")
        )
        .order_by("-case_count")
    )

    offence_data = (
        Case.objects
        .values(
            "offence__title"
        )
        .annotate(
            case_count=Count("id")
        )
        .order_by("-case_count")
    )

    hotspot_data = (
        Case.objects
        .exclude(
            location__isnull=True
        )
        .exclude(
            location__exact=""
        )
        .values(
            "location",
            "station__district__name"
        )
        .annotate(
            crime_count=Count("id")
        )
        .order_by("-crime_count")[:10]
    )

    context = {

        "district_data": district_data,

        "offence_data": offence_data,

        "hotspot_data": hotspot_data,

        "total_cases": Case.objects.count(),

        "total_arrests": ArrestRecord.objects.count(),

        "total_suspects": Suspect.objects.count(),

        "total_stations": PoliceStation.objects.filter(
            is_active=True
        ).count(),

    }

    return render(
        request,
        "reports/analytics.html",
        context
    )