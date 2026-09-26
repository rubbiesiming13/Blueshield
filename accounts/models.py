from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Division(models.Model):

    name = models.CharField(
        max_length=150,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


class User(AbstractUser):

    ROLE_CHOICES = [
        ("OFFICER", "Police Officer"),
        ("DIVISION_ADMIN", "Division Admin"),
        ("STATION_COMMANDER", "Station Commander"),
        ("ADMIN", "PPC / System Admin"),
    ]

    # =========================================================
    # POLICE INFORMATION
    # =========================================================

    badge_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )

    rank = models.CharField(
        max_length=100,
        blank=True
    )

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default="OFFICER"
    )

    # =========================================================
    # MOBILE PHONE
    # =========================================================

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    # =========================================================
    # LOCATION ASSIGNMENT
    # =========================================================

    district = models.ForeignKey(
        "stations.District",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )

    station = models.ForeignKey(
        "stations.PoliceStation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="officers"
    )

    # =========================================================
    # DIVISION ASSIGNMENT
    # =========================================================

    division = models.ForeignKey(
        Division,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )

    # =========================================================
    # SEVISPASS
    # =========================================================

    sevispass_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    sevispass_verified = models.BooleanField(
        default=False
    )

    sevispass_verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # =========================================================
    # VALIDATE USER ASSIGNMENT
    # =========================================================

    def clean(self):

        super().clean()

        errors = {}

        # -----------------------------------------------------
        # POLICE OFFICER
        # Must have district and station
        # -----------------------------------------------------

        if self.role == "OFFICER":

            if not self.district:
                errors["district"] = (
                    "Police Officer must be assigned to a district."
                )

            if not self.station:
                errors["station"] = (
                    "Police Officer must be assigned to a police station."
                )

        # -----------------------------------------------------
        # STATION COMMANDER
        # Must have district and station
        # -----------------------------------------------------

        elif self.role == "STATION_COMMANDER":

            if not self.district:
                errors["district"] = (
                    "Station Commander must be assigned to a district."
                )

            if not self.station:
                errors["station"] = (
                    "Station Commander must be assigned to a police station."
                )

        # -----------------------------------------------------
        # DIVISION ADMIN
        # Must have division, district and station
        # -----------------------------------------------------

        elif self.role == "DIVISION_ADMIN":

            if not self.division:
                errors["division"] = (
                    "Division Admin must be assigned to a division."
                )

            if not self.district:
                errors["district"] = (
                    "Division Admin must be assigned to a district."
                )

            if not self.station:
                errors["station"] = (
                    "Division Admin must be assigned to a police station."
                )

        # -----------------------------------------------------
        # ADMIN / PPC
        # Sees the whole Madang Province
        # -----------------------------------------------------

        elif self.role == "ADMIN":

            pass

        # -----------------------------------------------------
        # CHECK STATION BELONGS TO DISTRICT
        # -----------------------------------------------------

        if self.station and self.district:

            if self.station.district_id != self.district_id:

                errors["station"] = (
                    f"{self.station.name} does not belong to "
                    f"{self.district.name} District."
                )

        # -----------------------------------------------------
        # RETURN VALIDATION ERRORS
        # -----------------------------------------------------

        if errors:

            raise ValidationError(errors)

    def __str__(self):

        name = (
            self.get_full_name()
            or self.username
        )

        return (
            f"{self.badge_number or self.username} - {name}"
        )


class SevisPassOTP(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sevispass_otps"
    )

    otp_hash = models.CharField(
        max_length=128
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField()

    used = models.BooleanField(
        default=False
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    attempts = models.PositiveIntegerField(
        default=0
    )

    def is_expired(self):

        return timezone.now() >= self.expires_at

    def __str__(self):

        return (
            f"SevisPass OTP - "
            f"{self.user.username}"
        )