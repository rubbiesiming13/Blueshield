from django.urls import path
from . import views

app_name = "suspects"

urlpatterns = [
# List all suspects
path("", views.list_suspects, name="list"),


# Register a new suspect
path("create/", views.create_suspect, name="create"),

# View suspect details
path("<int:pk>/", views.suspect_detail, name="detail"),

# Edit suspect
path("<int:pk>/edit/", views.edit_suspect, name="edit"),

# Delete suspect
path("<int:pk>/delete/", views.delete_suspect, name="delete"),


]
