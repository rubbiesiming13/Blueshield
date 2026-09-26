from django.db import models

from accounts.models import User
from cases.models import Case
from investigation.models import InvestigationRecord


class Prosecution(models.Model):

    # ============================================================
    # PROSECUTION STATUS
    # ============================================================

    class Status(models.TextChoices):

        SUBMITTED = (
            "SUBMITTED",
            "Submitted for Prosecution"
        )

        UNDER_REVIEW = (
            "UNDER_REVIEW",
            "Under Review"
        )

        RETURNED = (
            "RETURNED",
            "Returned for Further Information"
        )

        READY_FOR_COURT = (
            "READY_FOR_COURT",
            "Ready for Court"
        )

        COMMITTAL = (
            "COMMITTAL",
            "Committal Proceedings"
        )

        SUMMARY_TRIAL = (
            "SUMMARY_TRIAL",
            "Summary Trial"
        )

        REFERRED = (
            "REFERRED",
            "Referred to Court"
        )

        COMPLETED = (
            "COMPLETED",
            "Prosecution Completed"
        )

        CLOSED = (
            "CLOSED",
            "Closed"
        )

    # ============================================================
    # PROCEEDING STATUS
    # ============================================================

    class ProceedingStatus(models.TextChoices):

        NOT_STARTED = (
            "NOT_STARTED",
            "Not Started"
        )

        IN_PROGRESS = (
            "IN_PROGRESS",
            "In Progress"
        )

        COMPLETED = (
            "COMPLETED",
            "Completed"
        )

    # ============================================================
    # CASE
    # ============================================================

    case = models.OneToOneField(
        Case,
        on_delete=models.PROTECT,
        related_name="prosecution",
    )

    # ============================================================
    # INVESTIGATION
    # ============================================================

    investigation = models.ForeignKey(
        InvestigationRecord,
        on_delete=models.PROTECT,
        related_name="prosecutions",
        null=True,
        blank=True,
    )

    # ============================================================
    # PROSECUTION IDENTIFICATION
    # ============================================================

    prosecution_number = models.CharField(
        max_length=50,
        unique=True,
    )

    # ============================================================
    # ASSIGNED PROSECUTOR
    # ============================================================

    prosecutor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="prosecutions",
    )

    # ============================================================
    # STATUS
    # ============================================================

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.SUBMITTED,
    )

    submission_date = models.DateTimeField(
        auto_now_add=True,
    )

    # ============================================================
    # CASE FILE REVIEW
    # ============================================================

    case_file_complete = models.BooleanField(
        default=False,
    )

    evidence_reviewed = models.BooleanField(
        default=False,
    )

    investigation_reviewed = models.BooleanField(
        default=False,
    )

    arrest_reviewed = models.BooleanField(
        default=False,
    )

    warrant_reviewed = models.BooleanField(
        default=False,
    )

    custody_reviewed = models.BooleanField(
        default=False,
    )

    # ============================================================
    # COMMITTAL PROCEEDINGS
    # ============================================================

    committal_status = models.CharField(
        max_length=30,
        choices=ProceedingStatus.choices,
        default=ProceedingStatus.NOT_STARTED,
    )

    committal_date = models.DateField(
        null=True,
        blank=True,
    )

    committal_notes = models.TextField(
        blank=True,
    )

    # ============================================================
    # SUMMARY TRIAL
    # ============================================================

    summary_trial_status = models.CharField(
        max_length=30,
        choices=ProceedingStatus.choices,
        default=ProceedingStatus.NOT_STARTED,
    )

    summary_trial_date = models.DateField(
        null=True,
        blank=True,
    )

    summary_trial_notes = models.TextField(
        blank=True,
    )

    # ============================================================
    # PROSECUTION REVIEW
    # ============================================================

    review_comments = models.TextField(
        blank=True,
    )

    return_reason = models.TextField(
        blank=True,
    )

    decision = models.TextField(
        blank=True,
    )

    # ============================================================
    # FORWARDING TO COURT
    # ============================================================

    forwarded_to_court = models.BooleanField(
        default=False,
    )

    forwarded_date = models.DateTimeField(
        null=True,
        blank=True,
    )

    # ============================================================
    # AUDIT / TIMESTAMPS
    # ============================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return (
            f"{self.prosecution_number} - "
            f"{self.case.case_number}"
        )