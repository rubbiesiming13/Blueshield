# apps/records/models.py
import uuid
from accounts.models import User
from django.db import models
from stations.models import PoliceStation
from suspects.models import Suspect


class CriminalOffence(models.Model):

    class Category(models.TextChoices):
        AGAINST_PERSON = (
            "PERSON",
            "Offences Against Person (Assault, Homicide)"
        )
        PROPERTY = (
            "PROPERTY",
            "Property Crimes (Stealing, B&E, Arson)"
        )
        NARCOTICS = (
            "DRUGS",
            "Dangerous Drugs & Homebrew"
        )
        PUBLIC_ORDER = (
            "PUBLIC",
            "Public Disorder & Summary Offences"
        )
        CYBER_FRAUD = (
            "FRAUD",
            "Fraud & Financial Crimes"
        )

    code = models.CharField(
        max_length=20,
        unique=True
    )

    title = models.CharField(
        max_length=150
    )

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.PUBLIC_ORDER
    )

    penalty_summary = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"[{self.code}] {self.title}"


class ArrestRecord(models.Model):

    class CustodyStatus(models.TextChoices):
        DETAINED = "DETAINED", "In Custody (Holding Cell)"
        BAILED_POLICE = "BAILED_POLICE", "Police Bail Granted"
        COURT_BAIL = "COURT_BAIL", "Remanded to Court"
        TRANSFERRED = "TRANSFERRED", "Transferred to Beon Prison / Hospital"
        RELEASED_NO_CHARGE = "RELEASED", "Released without Charge"

    arrest_tracking_id = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    occurrence_book_no = models.CharField(
        max_length=50,
        verbose_name="OB Number"
    )

    # Suspect being arrested
    suspect = models.ForeignKey(
        Suspect,
        on_delete=models.PROTECT,
        related_name="arrests"
    )

    # Case associated with this arrest
    case = models.ForeignKey(
        "cases.Case",
        on_delete=models.PROTECT,
        related_name="arrest_records",
        null=True,
        blank=True
    )

    # Police officer who made the arrest
    arresting_officer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="arrests_made"
    )

    # Police station where the arrest is recorded
    station = models.ForeignKey(
        PoliceStation,
        on_delete=models.PROTECT,
        related_name="station_arrests"
    )

    arrest_datetime = models.DateTimeField()

    arrest_location = models.CharField(
        max_length=200,
        help_text="e.g. Kalibobo, Modilon Road, Meiro Market"
    )

    reason_for_arrest = models.TextField()

    offences = models.ManyToManyField(
        CriminalOffence,
        related_name="linked_arrests"
    )

    property_seized = models.TextField(
        blank=True,
        help_text="Itemized confiscated belongings"
    )

    physical_condition_at_intake = models.TextField(
        blank=True,
        help_text="Injuries / Medical observations"
    )

    custody_status = models.CharField(
        max_length=25,
        choices=CustodyStatus.choices,
        default=CustodyStatus.DETAINED,
    )

    cell_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    bail_amount_pgk = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    bail_receipt_no = models.CharField(
        max_length=50,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):
        if not self.arrest_tracking_id:
            from django.utils import timezone

            year = timezone.now().year
            random_code = str(uuid.uuid4().hex[:6]).upper()

            self.arrest_tracking_id = f"MDG-{year}-{random_code}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.arrest_tracking_id} - {self.suspect.full_name}"