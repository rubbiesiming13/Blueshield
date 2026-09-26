from django.urls import path

from . import views


app_name = "cases"


urlpatterns = [

    path(
        "register/",
        views.register_case,
        name="register_case"
    ),

    path(
        "list/",
        views.case_list,
        name="list"
    ),

    path(
        "<int:case_id>/",
        views.case_detail,
        name="detail"
    ),

]