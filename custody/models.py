
from django.db import models

from accounts.models import User
from records.models import ArrestRecord


class CustodyRecord(models.Model):

    class Status(models.TextChoices):
        DETAINED = "DETAINED", "Detained"
        BAIL = "BAIL", "Released on Bail"
        COURT_REMAND = "COURT_REMAND", "Remanded to Court"
        TRANSFERRED = "TRANSFERRED", "Transferred"
        RELEASED = "RELEASED", "Released"
        PRISON = "PRISON", "Transferred to Prison"

    # Arrest associated with this custody record
    arrest = models.ForeignKey(
        ArrestRecord,
        on_delete=models.PROTECT,
        related_name="custody_records"
    )

    # Officer responsible for custody
    custody_officer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="custody_records"
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DETAINED
    )

    cell_number = models.CharField(
        max_length=30,
        blank=True
    )

    detention_start = models.DateTimeField()

    detention_end = models.DateTimeField(
        null=True,
        blank=True
    )

    bail_amount_pgk = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    bail_receipt_number = models.CharField(
        max_length=50,
        blank=True
    )

    transfer_destination = models.CharField(
        max_length=200,
        blank=True
    )

    release_reason = models.TextField(
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.arrest.suspect.full_name} - "
            f"{self.get_status_display()}"
        )

