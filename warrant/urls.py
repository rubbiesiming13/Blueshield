from django.urls import path

from . import views


app_name = "warrant"


urlpatterns = [
    path("", views.warrant_list, name="list"),
    path("create/", views.warrant_create, name="create"),
]