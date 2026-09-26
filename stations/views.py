from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import PoliceStation


@login_required
def station_list(request):
    stations = PoliceStation.objects.all()

    return render(
        request,
        "stations/list.html",
        {
            "stations": stations,
        }
    )
