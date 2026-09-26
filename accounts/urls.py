from django.urls import path

from . import views
from . import admin_views


app_name = "accounts"


urlpatterns = [

    # ==========================================================
    # AUTHENTICATION
    # ==========================================================

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    path(
        "sevispass/",
        views.sevispass_verify_view,
        name="sevispass_verify"
    ),
        path(
        "sevispass/otp/",
        views.sevispass_otp_view,
        name="sevispass_otp"
    ),



    # ==========================================================
    # DASHBOARD
    # ==========================================================

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),


    # ==========================================================
    # PPC DIRECTORIES
    # ==========================================================

    path(
        "police-stations/",
        views.police_stations,
        name="police_stations"
    ),

    path(
        "police-officers/",
        views.police_officers,
        name="police_officers"
    ),


    # ==========================================================
    # REPORTS
    # ==========================================================

    path(
        "reports/arrests/",
        views.arrest_report,
        name="arrest_report"
    ),

    path(
        "reports/districts/",
        views.district_report,
        name="district_report"
    ),

    path(
        "reports/crime-summary/",
        views.overall_crime_summary,
        name="overall_crime_summary"
    ),


    # ==========================================================
    # PPC / SYSTEM ADMINISTRATION
    # ==========================================================

    # -------------------------
    # User Management
    # -------------------------

    path(
        "admin/users/",
        admin_views.admin_users,
        name="admin_users"
    ),

    path(
        "admin/users/create/",
        admin_views.admin_user_create,
        name="admin_user_create"
    ),

    path(
        "admin/users/<int:user_id>/edit/",
        admin_views.admin_user_edit,
        name="admin_user_edit"
    ),

    path(
        "admin/users/<int:user_id>/toggle/",
        admin_views.admin_user_toggle,
        name="admin_user_toggle"
    ),


    # -------------------------
    # Police Officers
    # -------------------------

    path(
        "admin/officers/",
        admin_views.admin_officers,
        name="admin_officers"
    ),


    # -------------------------
    # Police Stations
    # -------------------------

    path(
        "admin/stations/",
        admin_views.admin_stations,
        name="admin_stations"
    ),


    # -------------------------
    # Criminal Offences
    # -------------------------

    path(
        "admin/offences/",
        admin_views.admin_offences,
        name="admin_offences"
    ),


    # -------------------------
    # Arrest Records
    # -------------------------

    path(
        "admin/arrests/",
        admin_views.admin_arrests,
        name="admin_arrests"
    ),


    # -------------------------
    # Cases
    # -------------------------

    path(
        "admin/cases/",
        admin_views.admin_cases,
        name="admin_cases"
    ),


    # -------------------------
    # Suspects
    # -------------------------

    path(
        "admin/suspects/",
        admin_views.admin_suspects,
        name="admin_suspects"
    ),


    # -------------------------
    # Audit Logs
    # -------------------------

    path(
        "admin/audit-logs/",
        admin_views.admin_audit_logs,
        name="admin_audit_logs"
    ),


    # -------------------------
    # Statistics
    # -------------------------

    path(
        "admin/statistics/",
        admin_views.admin_statistics,
        name="admin_statistics"
    ),


    # -------------------------
    # System Settings
    # -------------------------

    path(
        "admin/settings/",
        admin_views.admin_settings,
        name="admin_settings"
    ),
]