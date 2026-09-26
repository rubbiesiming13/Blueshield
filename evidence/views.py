
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EvidenceForm
from .models import Evidence


@login_required(login_url="accounts:login")
def evidence_list(request):

    evidences = Evidence.objects.select_related(
        "case",
        "arrest",
        "collected_by",
    ).order_by("-created_at")

    return render(
        request,
        "evidence/evidence_list.html",
        {
            "evidences": evidences,
        }
    )


@login_required(login_url="accounts:login")
def evidence_detail(request, pk):

    evidence = get_object_or_404(
        Evidence.objects.select_related(
            "case",
            "arrest",
            "collected_by",
        ),
        pk=pk
    )

    return render(
        request,
        "evidence/evidence_detail.html",
        {
            "evidence": evidence,
        }
    )


@login_required(login_url="accounts:login")
def evidence_create(request):

    if request.method == "POST":

        form = EvidenceForm(request.POST)

        if form.is_valid():

            evidence = form.save(commit=False)

            # Automatically record the logged-in officer
            # as the person who collected the evidence.
            evidence.collected_by = request.user

            evidence.save()

            messages.success(
                request,
                "Evidence has been successfully recorded."
            )

            return redirect(
                "evidence:detail",
                pk=evidence.pk
            )

    else:

        form = EvidenceForm()

    return render(
        request,
        "evidence/evidence_form.html",
        {
            "form": form,
            "page_title": "Record Evidence",
        }
    )


@login_required(login_url="accounts:login")
def evidence_update(request, pk):

    evidence = get_object_or_404(
        Evidence,
        pk=pk
    )

    if request.method == "POST":

        form = EvidenceForm(
            request.POST,
            instance=evidence
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Evidence has been updated successfully."
            )

            return redirect(
                "evidence:detail",
                pk=evidence.pk
            )

    else:

        form = EvidenceForm(
            instance=evidence
        )

    return render(
        request,
        "evidence/evidence_form.html",
        {
            "form": form,
            "evidence": evidence,
            "page_title": "Update Evidence",
        }
    )


@login_required(login_url="accounts:login")
def evidence_delete(request, pk):

    evidence = get_object_or_404(
        Evidence,
        pk=pk
    )

    if request.method == "POST":

        evidence.delete()

        messages.success(
            request,
            "Evidence has been deleted."
        )

        return redirect(
            "evidence:list"
        )

    return render(
        request,
        "evidence/evidence_confirm_delete.html",
        {
            "evidence": evidence,
        }
    )

