
from .models import AuditLog


def get_client_ip(request):
    """
    Get the user's IP address from the request.
    """

    if not request:
        return None

    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def create_audit_log(
    request,
    action,
    target_model,
    target_id="",
    details=""
):
    """
    Create an AuditLog entry for a BlueShield action.
    """

    user = None

    if request and hasattr(request, "user"):
        if request.user.is_authenticated:
            user = request.user

    return AuditLog.objects.create(
        user=user,
        action=action,
        target_model=target_model,
        target_id=str(target_id),
        ip_address=get_client_ip(request),
        details=details
    )

