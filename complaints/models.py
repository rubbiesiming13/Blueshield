from django.conf import settings
from django.db import models


class Complaint(models.Model):

    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("UNDER_REVIEW", "Under Review"),
        ("CONVERTED", "Converted to Case"),
        ("CLOSED", "Closed"),
    ]

    COMPLAINANT_ROLE_CHOICES = [
        ("VICTIM", "Victim"),
        ("WITNESS", "Witness"),
        ("VICTIM_WITNESS", "Victim & Witness"),
        ("OTHER", "Other / Complainant"),
    ]

    # =========================================================
    # COMPLAINT / OB INFORMATION
    # =========================================================

    complaint_number = models.CharField(
        max_length=30,
        unique=True
    )

    complainant_name = models.CharField(
        max_length=150
    )

    complainant_phone = models.CharField(
        max_length=30,
        blank=True
    )

    complainant_address = models.TextField(
        blank=True
    )

    complainant_role = models.CharField(
        max_length=30,
        choices=COMPLAINANT_ROLE_CHOICES,
        default="OTHER"
    )

    # =========================================================
    # PERSON'S STATEMENT
    # =========================================================

    complainant_statement = models.TextField(
        blank=True,
        help_text=(
            "Statement provided from the perspective of the "
            "person reporting the complaint."
        )
    )

    # =========================================================
    # INCIDENT INFORMATION
    # =========================================================

    complaint_type = models.CharField(
        max_length=100,
        default="GENERAL"
    )

    incident_date = models.DateField()

    incident_location = models.CharField(
        max_length=255
    )

    description = models.TextField()

    # =========================================================
    # POLICE STATION
    # Automatically assigned from logged-in user
    # =========================================================

    station = models.ForeignKey(
        "stations.PoliceStation",
        on_delete=models.PROTECT,
        related_name="complaints"
    )

    # =========================================================
    # OFFICER WHO CREATED THE COMPLAINT
    # Automatically assigned from logged-in user
    # =========================================================

    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="complaints_created"
    )

    # =========================================================
    # STATUS
    # =========================================================

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="OPEN"
    )

    # =========================================================
    # TIMESTAMPS
    # =========================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # =========================================================
    # DISPLAY
    # =========================================================

    def __str__(self):
        return self.complaint_number


# =============================================================
# COMPLAINT WITNESSES
# =============================================================

class ComplaintWitness(models.Model):

    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name="witnesses"
    )

    # =========================================================
    # WITNESS INFORMATION
    # =========================================================

    full_name = models.CharField(
        max_length=150
    )

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    # =========================================================
    # WITNESS STATEMENT
    # =========================================================

    statement = models.TextField(
        help_text=(
            "Record what the witness personally saw or heard."
        )
    )

    # =========================================================
    # TIMESTAMP
    # =========================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # =========================================================
    # DISPLAY
    # =========================================================

    def __str__(self):
        return f"{self.full_name} - {self.complaint.complaint_number}"