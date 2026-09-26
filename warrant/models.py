from django.db import models

from accounts.models import User
from stations.models import PoliceStation
from suspects.models import Suspect
from cases.models import Case


class Warrant(models.Model):

    class WarrantType(models.TextChoices):
        ARREST = "ARREST", "Arrest Warrant"
        SEARCH = "SEARCH", "Search Warrant"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending Approval"
        APPROVED = "APPROVED", "Approved"
        EXECUTED = "EXECUTED", "Executed"
        CANCELLED = "CANCELLED", "Cancelled"
        EXPIRED = "EXPIRED", "Expired"

    warrant_number = models.CharField(
        max_length=50,
        unique=True
    )

    warrant_type = models.CharField(
        max_length=20,
        choices=WarrantType.choices,
        default=WarrantType.ARREST
    )

    suspect = models.ForeignKey(
        Suspect,
        on_delete=models.PROTECT,
        related_name="warrants"
    )

    case = models.ForeignKey(
        Case,
        on_delete=models.PROTECT,
        related_name="warrants",
        null=True,
        blank=True
    )

    station = models.ForeignKey(
        PoliceStation,
        on_delete=models.PROTECT,
        related_name="warrants"
    )

    reason = models.TextField()

    issue_date = models.DateField()

    expiry_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    requested_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="requested_warrants"
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_warrants"
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    executed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.warrant_number} - {self.suspect.full_name}"