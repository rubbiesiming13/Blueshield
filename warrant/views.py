from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Warrant


@login_required
def warrant_list(request):
    warrants = Warrant.objects.all().order_by("-created_at")

    return render(
        request,
        "warrant/list.html",
        {
            "warrants": warrants,
        }
    )


@login_required
def warrant_create(request):
    return render(
        request,
        "warrant/create.html"
    )