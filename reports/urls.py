from django.urls import path

from . import views


app_name = "reports"


urlpatterns = [

    # ========================================================
    # STATION COMMANDER
    # ========================================================

    path(
        "commander/",
        views.commander_reports,
        name="commander_reports",
    ),

    path(
        "create/",
        views.create_report,
        name="create",
    ),

    path(
        "<int:report_id>/submit/",
        views.submit_report,
        name="submit",
    ),

    # ========================================================
    # PPC MONTHLY REPORT REVIEW
    # ========================================================

    path(
        "ppc/",
        views.ppc_reports,
        name="ppc_reports",
    ),

    path(
        "ppc/<int:report_id>/review/",
        views.review_report,
        name="review",
    ),

    # ========================================================
    # MONTHLY REPORT DETAIL
    # ========================================================

    path(
        "<int:report_id>/",
        views.report_detail,
        name="detail",
    ),

    # ========================================================
    # PPC REPORTING DASHBOARD
    # ========================================================

    path(
        "dashboard/",
        views.reports_dashboard,
        name="dashboard",
    ),

    # ========================================================
    # ARREST REPORTS
    # ========================================================

    path(
        "arrests/",
        views.arrest_report,
        name="arrests",
    ),

    path(
        "arrests/pdf/",
        views.arrest_report_pdf,
        name="arrests_pdf",
    ),

    path(
        "arrests/csv/",
        views.arrest_report_csv,
        name="arrests_csv",
    ),

    # ========================================================
    # CRIME REPORTS
    # ========================================================

    path(
        "crime/",
        views.crime_report,
        name="crime",
    ),

    path(
        "crime/pdf/",
        views.crime_report_pdf,
        name="crime_pdf",
    ),

    path(
        "crime/csv/",
        views.crime_report_csv,
        name="crime_csv",
    ),

    # ========================================================
    # CUSTODY / PRISON REPORTS
    # ========================================================

    path(
        "custody/",
        views.custody_report,
        name="custody",
    ),

    path(
        "custody/pdf/",
        views.custody_report_pdf,
        name="custody_pdf",
    ),

    path(
        "custody/csv/",
        views.custody_report_csv,
        name="custody_csv",
    ),

    # ========================================================
    # ANALYTICS
    # ========================================================

    path(
        "analytics/",
        views.analytics,
        name="analytics",
    ),
]