from django.urls import path

from . import views


app_name = "investigation"


urlpatterns = [

    path(
        "",
        views.investigation_list,
        name="list"
    ),

    path(
        "create/",
        views.investigation_create,
        name="create"
    ),

    path(
        "<int:pk>/",
        views.investigation_detail,
        name="detail"
    ),

    path(
        "<int:pk>/update/",
        views.investigation_update,
        name="update"
    ),

    path(
        "<int:pk>/delete/",
        views.investigation_delete,
        name="delete"
    ),

    path(
        "workspace/<int:case_id>/",
        views.investigation_workspace,
        name="workspace"
    ),

]