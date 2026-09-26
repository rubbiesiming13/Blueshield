from django.db import models

from accounts.models import User
from stations.models import PoliceStation


class Suspect(models.Model):

    GENDER_CHOICES = [
        ("MALE", "Male"),
        ("FEMALE", "Female"),
        ("OTHER", "Other"),
    ]

    ID_TYPE_CHOICES = [
        ("NATIONAL_ID", "National ID"),
        ("VOTER_ID", "Voter ID"),
        ("PASSPORT", "Passport"),
        ("DRIVER_LICENSE", "Driver's License"),
        ("OTHER", "Other"),
    ]

    ROLE_CHOICES = [
        ("MAIN", "Main Suspect"),
        ("CO", "Co-Suspect"),
        ("POI", "Person of Interest"),
    ]

    # ============================================================
    # IDENTIFICATION
    # ============================================================

    suspect_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True
    )

    national_id_or_voter_no = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    id_type = models.CharField(
        max_length=30,
        choices=ID_TYPE_CHOICES,
        blank=True,
        null=True
    )

    # ============================================================
    # PERSONAL INFORMATION
    # ============================================================

    first_name = models.CharField(
        max_length=60
    )

    middle_name = models.CharField(
        max_length=60,
        blank=True
    )

    last_name = models.CharField(
        max_length=60
    )

    alias = models.CharField(
        max_length=100,
        blank=True,
        help_text="Known nickname or alias"
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    nationality = models.CharField(
        max_length=60,
        default="Papua New Guinean"
    )

    occupation = models.CharField(
        max_length=100,
        blank=True
    )

    # ============================================================
    # CONTACT INFORMATION
    # ============================================================

    phone_number = models.CharField(
        max_length=30,
        blank=True
    )

    residential_address = models.TextField(
        help_text="Current residential address"
    )

    village = models.CharField(
    max_length=100,
    blank=True
     )

    district = models.CharField(
    max_length=100,
    blank=True
    )

    province_name = models.CharField(
    max_length=100,
    blank=True,
    null=True
    )

    province = models.ForeignKey(
    "stations.Province",
    on_delete=models.PROTECT,
    related_name="suspects",
    null=True,
    blank=True
    )

    # ============================================================
    # ADDITIONAL IDENTIFICATION
    # ============================================================

    identifying_marks = models.TextField(
        blank=True,
        help_text="Scars, tattoos, birthmarks or other identifying features"
    )

    mugshot = models.ImageField(
        upload_to="mugshots/%Y/%m/",
        blank=True,
        null=True
    )

    fingerprint_record_code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # ============================================================
    # CASE CONNECTION
    # ============================================================

    case = models.ForeignKey(
        "cases.Case",
        on_delete=models.PROTECT,
        related_name="suspect_records",
        null=True,
        blank=True
    )

    suspect_role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="MAIN"
    )

    notes = models.TextField(
        blank=True
    )

    # ============================================================
    # BLUE SHIELD SYSTEM INFORMATION
    # ============================================================

    registered_by = models.ForeignKey(
    User,
    on_delete=models.PROTECT,
    related_name="suspects_registered",
    null=True,
    blank=True
)

    station = models.ForeignKey(
    PoliceStation,
    on_delete=models.PROTECT,
    related_name="registered_suspects",
    null=True,
    blank=True
)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # ============================================================
    # DISPLAY NAME
    # ============================================================

    @property
    def full_name(self):

        name = self.first_name

        if self.middle_name:
            name += f" {self.middle_name}"

        name += f" {self.last_name}"

        if self.alias:
            name += f" (a.k.a {self.alias})"

        return name

    def __str__(self):

        if self.suspect_number:
            return f"{self.suspect_number} - {self.full_name}"

        return self.full_name