
from django.conf import settings
from django.db import models


class AuditLog(models.Model):

    class Action(models.TextChoices):
        LOGIN = "LOGIN", "Officer Login"
        LOGOUT = "LOGOUT", "Officer Logout"
        VIEW = "VIEW", "Viewed Sensitive File"
        CREATE = "CREATE", "Created Record"
        UPDATE = "UPDATE", "Updated Record"
        DELETE = "DELETE", "Deleted Record"
        PRINT_EXPORT = "PRINT", "Exported / Printed Record"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    action = models.CharField(
        max_length=20,
        choices=Action.choices
    )

    target_model = models.CharField(
        max_length=50
    )

    target_id = models.CharField(
        max_length=50
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    details = models.TextField(
        blank=True
    )

    class Meta:
        ordering = ["-timestamp"]

