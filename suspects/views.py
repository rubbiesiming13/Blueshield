from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.utils import timezone

from .forms import SuspectForm
from .models import Suspect


# ============================================================
# GENERATE SUSPECT NUMBER
# ============================================================

def generate_suspect_number():

    year = timezone.now().year

    last_suspect = (
        Suspect.objects
        .filter(
            suspect_number__startswith=f"SUS-{year}-"
        )
        .order_by("-id")
        .first()
    )

    if last_suspect:

        try:
            last_number = int(
                last_suspect.suspect_number.rsplit("-", 1)[1]
            )

            next_number = last_number + 1

        except (ValueError, IndexError):

            next_number = 1

    else:

        next_number = 1

    return f"SUS-{year}-{next_number:04d}"


# ============================================================
# LIST SUSPECTS
# ============================================================

@login_required(login_url="accounts:login")
def list_suspects(request):

    suspects = (
        Suspect.objects
        .filter(
            station=request.user.station
        )
        .select_related(
            "case",
            "station",
            "registered_by",
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "suspects/suspect_list.html",
        {
            "suspects": suspects,
            "user": request.user,
        }
    )


# ============================================================
# CREATE / REGISTER SUSPECT
# ============================================================

@login_required(login_url="accounts:login")
def create_suspect(request):

    if request.user.role != "OFFICER":

        messages.error(
            request,
            "You do not have permission to register suspects."
        )

        return redirect("accounts:dashboard")

    if not request.user.station:

        messages.error(
            request,
            "Your account is not assigned to a police station. "
            "Please contact the system administrator."
        )

        return redirect("accounts:dashboard")

    if request.method == "POST":

        form = SuspectForm(
            request.POST,
            request.FILES,
            user=request.user
        )

        if form.is_valid():

            suspect = form.save(commit=False)

            # ==================================================
            # AUTOMATIC BLUE SHIELD INFORMATION
            # ==================================================

            suspect.suspect_number = generate_suspect_number()

            # Automatically record the officer
            suspect.registered_by = request.user

            # Automatically record the police station
            suspect.station = request.user.station

            # Automatically record the officer's district
            if request.user.district:
                suspect.district = request.user.district.name
            else:
                suspect.district = (
                    request.user.station.district.name
                )

            suspect.save()

            messages.success(
                request,
                f"Suspect {suspect.suspect_number} "
                "was successfully registered."
            )

            return redirect("suspects:list")

    else:

        form = SuspectForm(
            user=request.user
        )

    return render(
        request,
        "suspects/create.html",
        {
            "form": form,
            "officer": request.user,
            "station": request.user.station,
            "district": request.user.district,
            "case_details": form.case_details,
        }
    )
# ============================================================
# VIEW SUSPECT DETAILS
# ============================================================

@login_required(login_url="accounts:login")
def suspect_detail(request, pk):

    suspect = get_object_or_404(
        Suspect.objects.select_related(
            "case",
            "station",
            "registered_by",
        ),
        pk=pk,
        station=request.user.station
    )

    return render(
        request,
        "suspects/detail.html",
        {
            "suspect": suspect
        }
    )


# ============================================================
# EDIT SUSPECT
# ============================================================

@login_required(login_url="accounts:login")
def edit_suspect(request, pk):

    suspect = get_object_or_404(
        Suspect,
        pk=pk,
        station=request.user.station
    )

    if request.user.role != "OFFICER":

        messages.error(
            request,
            "You do not have permission to edit suspect records."
        )

        return redirect("suspects:list")

    if request.method == "POST":

        form = SuspectForm(
            request.POST,
            request.FILES,
            instance=suspect
        )

        if form.is_valid():

            suspect = form.save(commit=False)

            # Keep system information protected
            suspect.registered_by = suspect.registered_by
            suspect.station = suspect.station

            # Automatically keep the officer's district
            if request.user.district:
                suspect.district = request.user.district.name
            else:
                suspect.district = request.user.station.district.name

            # Home province is NOT overwritten.
            # It comes from the officer's form input.

            suspect.save()

            messages.success(
                request,
                f"Suspect {suspect.full_name} "
                "was successfully updated."
            )

            return redirect(
                "suspects:detail",
                pk=suspect.pk
            )

    else:

        form = SuspectForm(
            instance=suspect
        )

    return render(
        request,
        "suspects/edit.html",
        {
            "form": form,
            "suspect": suspect
        }
    )


# ============================================================
# DELETE SUSPECT
# ============================================================

@login_required(login_url="accounts:login")
def delete_suspect(request, pk):

    suspect = get_object_or_404(
        Suspect,
        pk=pk,
        station=request.user.station
    )

    if request.user.role != "OFFICER":

        messages.error(
            request,
            "You do not have permission to delete suspect records."
        )

        return redirect("suspects:list")

    if request.method == "POST":

        suspect_name = suspect.full_name

        suspect.delete()

        messages.success(
            request,
            f"Suspect {suspect_name} was successfully deleted."
        )

        return redirect("suspects:list")

    return render(
        request,
        "suspects/delete.html",
        {
            "suspect": suspect
        }
    )