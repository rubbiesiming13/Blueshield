from django.db import models


class Province(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    code = models.CharField(
        max_length=20,
        unique=True,
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

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class District(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    # Keep this as text for now.
    # Existing BlueShield data already uses values such as "Madang".
    province = models.CharField(
        max_length=100,
        default="Madang"
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
        return f"{self.name} - {self.province}"


class PoliceStation(models.Model):

    name = models.CharField(
        max_length=150
    )

    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        related_name="stations"
    )

    # Keep this as text for now.
    # Existing BlueShield data already uses values such as "Madang".
    province = models.CharField(
        max_length=100,
        default="Madang"
    )

    commander_name = models.CharField(
        max_length=150,
        blank=True
    )

    phone_number = models.CharField(
        max_length=30,
        blank=True
    )

    address = models.TextField(
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
        return f"{self.name} - {self.district.name}"