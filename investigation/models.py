from django.db import models
from django.conf import settings


class InvestigationRecord(models.Model):

    case = models.ForeignKey(
        "cases.Case",
        on_delete=models.PROTECT,
        related_name="investigations"
    )

    investigating_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="investigation_records"
    )

    investigation_date = models.DateField()

    activity = models.CharField(
        max_length=255,
        help_text="Brief description of the investigation activity"
    )

    location = models.CharField(
        max_length=255,
        blank=True
    )

    findings = models.TextField(
        blank=True
    )

    action_taken = models.TextField(
        blank=True
    )

    investigation_notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.case.case_number} - {self.activity}"


class Statement(models.Model):

    STATEMENT_TYPE_CHOICES = [
        ("VICTIM", "Victim"),
        ("WITNESS", "Witness"),
        ("SUSPECT", "Suspect"),
        ("OTHER", "Other"),
    ]

    case = models.ForeignKey(
        "cases.Case",
        on_delete=models.PROTECT,
        related_name="statements"
    )

    person = models.CharField(
        max_length=150
    )

    statement_type = models.CharField(
        max_length=20,
        choices=STATEMENT_TYPE_CHOICES
    )

    statement_date = models.DateField()

    statement_time = models.TimeField(
        blank=True,
        null=True
    )

    location = models.CharField(
        max_length=255,
        blank=True
    )

    statement = models.TextField()

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="statements_recorded"
    )

    attachment = models.FileField(
        upload_to="statements/%Y/%m/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.case.case_number} - {self.person}"