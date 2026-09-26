from django.urls import path
from . import views

app_name = "complaints"

urlpatterns = [
    # Complaint list
    path("", views.complaint_list, name="list"),

    # Create complaint
    path("create/", views.create_complaint, name="create_complaint"),

    # View one complaint
    path("<int:pk>/", views.complaint_detail, name="detail"),

    # Edit one complaint
    path("<int:pk>/edit/", views.edit_complaint, name="edit"),
]