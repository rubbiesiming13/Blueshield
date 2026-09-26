from django.db import models
from django.conf import settings

from stations.models import District, PoliceStation


class MonthlyReport(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        REVIEWED = "REVIEWED", "Reviewed"
        RETURNED = "RETURNED", "Returned"
        APPROVED = "APPROVED", "Approved"

    report_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    year = models.PositiveIntegerField()

    month = models.PositiveSmallIntegerField(
        choices=[
            (1, "January"),
            (2, "February"),
            (3, "March"),
            (4, "April"),
            (5, "May"),
            (6, "June"),
            (7, "July"),
            (8, "August"),
            (9, "September"),
            (10, "October"),
            (11, "November"),
            (12, "December"),
        ]
    )

    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        related_name="monthly_reports"
    )

    station = models.ForeignKey(
        PoliceStation,
        on_delete=models.PROTECT,
        related_name="monthly_reports"
    )

    prepared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="monthly_reports_prepared"
    )

    # =========================
    # RECORD STATISTICS
    # =========================

    total_complaints = models.PositiveIntegerField(default=0)

    total_cases = models.PositiveIntegerField(default=0)

    total_open_cases = models.PositiveIntegerField(default=0)

    total_investigation_cases = models.PositiveIntegerField(default=0)

    total_warrant_requests = models.PositiveIntegerField(default=0)

    total_arrests = models.PositiveIntegerField(default=0)

    total_in_custody = models.PositiveIntegerField(default=0)

    total_released = models.PositiveIntegerField(default=0)

    total_evidence = models.PositiveIntegerField(default=0)

    total_prosecution_cases = models.PositiveIntegerField(default=0)

    # =========================
    # COMMANDER REPORT
    # =========================

    summary = models.TextField(
        blank=True,
        help_text="Monthly operational summary."
    )

    operational_notes = models.TextField(
        blank=True,
        help_text="Important operational activities and observations."
    )

    challenges = models.TextField(
        blank=True,
        help_text="Challenges faced during the reporting period."
    )

    recommendations = models.TextField(
        blank=True,
        help_text="Recommendations from the Station Commander."
    )

    # =========================
    # PPC REVIEW
    # =========================

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="monthly_reports_reviewed"
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    review_comments = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-year", "-month", "-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["year", "month", "station"],
                name="unique_monthly_report_per_station"
            )
        ]

    def save(self, *args, **kwargs):

        if not self.report_number:
            self.report_number = self.generate_report_number()

        super().save(*args, **kwargs)

    def generate_report_number(self):
        prefix = f"RPT-{self.year}-{self.month:02d}"

        existing = MonthlyReport.objects.filter(
            report_number__startswith=prefix
        ).count()

        sequence = existing + 1

        return f"{prefix}-{sequence:04d}"

    @property
    def month_name(self):
        return dict(
            self._meta.get_field("month").choices
        ).get(self.month, "")

    def __str__(self):
        return f"{self.report_number} - {self.station.name}"