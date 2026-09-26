from django.urls import path

from . import views


app_name = "prosecution"


urlpatterns = [

    # ========================================================
    # PROSECUTION DASHBOARD
    # ========================================================

    path(
        "dashboard/",
        views.prosecution_dashboard,
        name="dashboard",
    ),

    # ========================================================
    # MAIN PROSECUTION CASE QUEUE
    # ========================================================

    path(
        "",
        views.prosecution_list,
        name="list",
    ),

    path(
        "cases/",
        views.prosecution_list,
        name="cases",
    ),

    # ========================================================
    # POLICE OFFICER - CASE FILE PREPARATION
    # ========================================================

    path(
        "prepare/<int:case_id>/",
        views.prepare_case_file,
        name="prepare_case_file",
    ),

    # ========================================================
    # POLICE OFFICER - SUBMIT CASE FILE
    # ========================================================

    path(
        "submit/<int:case_id>/",
        views.submit_case_file,
        name="submit_case_file",
    ),

    # ========================================================
    # DIVISION ADMIN / PROSECUTION - REVIEW
    # ========================================================

    path(
        "review/<int:prosecution_id>/",
        views.review,
        name="review",
    ),

    # ========================================================
    # DIVISION ADMIN / PROSECUTION - PROCESS
    # ========================================================

    path(
        "process/<int:prosecution_id>/",
        views.process,
        name="process",
    ),

    # ========================================================
    # DIVISION ADMIN / PROSECUTION - RETURN
    # ========================================================

    path(
        "return/<int:prosecution_id>/",
        views.return_case,
        name="return_case",
    ),

    # ========================================================
    # COMMITTAL
    # ========================================================

    path(
        "committal/<int:prosecution_id>/",
        views.committal_checklist,
        name="committal_checklist",
    ),

    path(
        "committal/<int:prosecution_id>/status/",
        views.committal_status,
        name="committal_status",
    ),

    # ========================================================
    # SUMMARY TRIAL
    # ========================================================

    path(
        "summary-trial/<int:prosecution_id>/status/",
        views.summary_trial_status,
        name="summary_trial_status",
    ),
]