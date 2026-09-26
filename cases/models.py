from django.db import models

from accounts.models import User
from stations.models import PoliceStation
from suspects.models import Suspect
from records.models import CriminalOffence


class Case(models.Model):

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        UNDER_INVESTIGATION = "INVESTIGATION", "Under Investigation"
        WARRANT_REQUESTED = "WARRANT", "Warrant Requested"
        ARRESTED = "ARRESTED", "Arrested"
        IN_CUSTODY = "CUSTODY", "In Custody"
        CASE_FILE_PREPARED = "FILE_PREPARED", "Case File Prepared"
        SUBMITTED_TO_PROSECUTION = "PROSECUTION", "Submitted to Prosecution"
        CLOSED = "CLOSED", "Closed"

    class Priority(models.TextChoices):
        NORMAL = "NORMAL", "Normal"
        HIGH = "HIGH", "High"
        URGENT = "URGENT", "Urgent"

    complaint = models.ForeignKey(
        "complaints.Complaint",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="cases"
    )

    case_number = models.CharField(
        max_length=50,
        unique=True
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    offence = models.ForeignKey(
        CriminalOffence,
        on_delete=models.PROTECT,
        related_name="cases"
    )

    suspect = models.ForeignKey(
        Suspect,
        on_delete=models.PROTECT,
        related_name="cases",
        null=True,
        blank=True
    )

    investigating_officer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="investigated_cases"
    )

    station = models.ForeignKey(
        PoliceStation,
        on_delete=models.PROTECT,
        related_name="cases"
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.OPEN
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL
    )

    incident_date = models.DateTimeField()

    location = models.CharField(
        max_length=200
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_cases"
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True
    )
    

    def __str__(self):
        return f"{self.case_number} - {self.title}"
