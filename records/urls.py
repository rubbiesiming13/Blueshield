from django.urls import path

from . import views


app_name = "records"


urlpatterns = [

    path(
        "",
        views.record_list,
        name="list",
    ),

    path(
        "create/",
        views.record_create,
        name="create",
    ),

    path(
        "<int:pk>/",
        views.record_detail,
        name="detail",
    ),

    path(
        "<int:pk>/edit/",
        views.record_edit,
        name="edit",
    ),

    path(
        "<int:pk>/delete/",
        views.record_delete,
        name="delete",
    ),

]