from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustodyRecordForm
from .models import CustodyRecord


@login_required(login_url="accounts:login")
def custody_list(request):

    custody_records = CustodyRecord.objects.select_related(
        "arrest",
        "suspect",
        "station",
        "custody_officer",
    ).order_by("-created_at")

    return render(
        request,
        "custody/custody_list.html",
        {
            "custody_records": custody_records
        }
    )


@login_required(login_url="accounts:login")
def custody_detail(request, pk):

    custody = get_object_or_404(
        CustodyRecord.objects.select_related(
            "arrest",
            "suspect",
            "station",
            "custody_officer",
        ),
        pk=pk
    )

    return render(
        request,
        "custody/custody_detail.html",
        {
            "custody": custody
        }
    )


@login_required(login_url="accounts:login")
def custody_create(request):

    if request.method == "POST":

        form = CustodyRecordForm(request.POST)

        if form.is_valid():

            custody = form.save()

            messages.success(
                request,
                "Custody record created successfully."
            )

            return redirect(
                "custody:detail",
                pk=custody.pk
            )

    else:

        form = CustodyRecordForm()

    return render(
        request,
        "custody/custody_form.html",
        {
            "form": form,
            "page_title": "Record Custody"
        }
    )


@login_required(login_url="accounts:login")
def custody_update(request, pk):

    custody = get_object_or_404(
        CustodyRecord,
        pk=pk
    )

    if request.method == "POST":

        form = CustodyRecordForm(
            request.POST,
            instance=custody
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Custody record updated successfully."
            )

            return redirect(
                "custody:detail",
                pk=custody.pk
            )

    else:

        form = CustodyRecordForm(
            instance=custody
        )

    return render(
        request,
        "custody/custody_form.html",
        {
            "form": form,
            "custody": custody,
            "page_title": "Update Custody Record"
        }
    )


@login_required(login_url="accounts:login")
def custody_delete(request, pk):

    custody = get_object_or_404(
        CustodyRecord,
        pk=pk
    )

    if request.method == "POST":

        custody.delete()

        messages.success(
            request,
            "Custody record deleted successfully."
        )

        return redirect("custody:list")

    return render(
        request,
        "custody/custody_confirm_delete.html",
        {
            "custody": custody
        }
    )