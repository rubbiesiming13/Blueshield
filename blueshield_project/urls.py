from django.contrib import admin
from django.urls import include, path

import blueshield_project.views as views


urlpatterns = [

    # =========================
    # BlueShield Homepage
    # =========================
    path("", views.home, name="home"),

    # =========================
    # Admin
    # =========================
    path("admin/", admin.site.urls),

    # =========================
    # Accounts / Authentication
    # =========================
    path("accounts/", include("accounts.urls")),

    # =========================
    # BlueShield Modules
    # =========================
    path("complaints/", include("complaints.urls")),
    path("cases/", include("cases.urls")),
    path("suspects/", include("suspects.urls")),
    path("investigation/", include("investigation.urls")),
    path("evidence/", include("evidence.urls")),
    path("custody/", include("custody.urls")),
    path("prosecution/", include("prosecution.urls")),
    path("records/", include("records.urls")),
    path("police-ai/", include("chatbot.urls")),
    path("reports/", include("reports.urls")),

 

    # =========================
    # Other Modules
    # =========================
    path("stations/", include("stations.urls")),
    path("warrant/", include("warrant.urls")),
]