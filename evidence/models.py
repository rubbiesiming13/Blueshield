from django.db import models
from accounts.models import User
from cases.models import Case
from records.models import ArrestRecord


class Evidence(models.Model):

    class EvidenceType(models.TextChoices):
        DOCUMENT = "DOCUMENT", "Document"
        PHYSICAL = "PHYSICAL", "Physical Evidence"
        DIGITAL = "DIGITAL", "Digital Evidence"
        PHOTOGRAPH = "PHOTOGRAPH", "Photograph"
        VIDEO = "VIDEO", "Video"
        AUDIO = "AUDIO", "Audio Recording"
        WEAPON = "WEAPON", "Weapon"
        DRUG = "DRUG", "Drug / Substance"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        COLLECTED = "COLLECTED", "Collected"
        IN_STORAGE = "IN_STORAGE", "In Storage"
        TRANSFERRED = "TRANSFERRED", "Transferred"
        SUBMITTED_COURT = "SUBMITTED_COURT", "Submitted to Court"
        RETURNED = "RETURNED", "Returned"
        DISPOSED = "DISPOSED", "Disposed"

    evidence_number = models.CharField(
        max_length=50,
        unique=True
    )

    case = models.ForeignKey(
        Case,
        on_delete=models.PROTECT,
        related_name="evidence"
    )

    arrest = models.ForeignKey(
        ArrestRecord,
        on_delete=models.PROTECT,
        related_name="evidence",
        null=True,
        blank=True
    )

    evidence_type = models.CharField(
        max_length=20,
        choices=EvidenceType.choices
    )

    description = models.TextField()

    location_found = models.CharField(
        max_length=200
    )

    collected_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="evidence_collected"
    )

    date_collected = models.DateTimeField()

    storage_location = models.CharField(
        max_length=200,
        blank=True
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.COLLECTED
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
        return f"{self.evidence_number} - {self.description[:50]}"