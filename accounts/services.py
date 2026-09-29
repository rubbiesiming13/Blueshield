import secrets

from datetime import timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone

from .models import User, SevisPassOTP

# ============================================================
# GENERATE TEST SEVISPASS ID
# ============================================================


def generate_blueshield_username():
    """
    Generate the next BlueShield system username.

    Format:
        BS-0001
        BS-0002
        BS-0003
    """

    number = 1

    while True:

        username = f"BS-{number:04d}"

        if not User.objects.filter(
            username=username
        ).exists():

            return username

        number += 1


def generate_temporary_password():
    """
    Generate a temporary password for a new
    BlueShield user account.
    """

    alphabet = (
        "ABCDEFGHJKLMNPQRSTUVWXYZ"
        "abcdefghijkmnopqrstuvwxyz"
        "23456789"
        "@#$%"
    )

    password = "".join(
        secrets.choice(alphabet)
        for _ in range(12)
    )

    return password

def generate_sevispass_id():
    """
    Generate a unique test SevisPass ID
    for the BlueShield prototype.
    """

    while True:

        random_part = secrets.token_hex(4).upper()

        sevispass_id = (
            f"PNG-SP-{timezone.now().year}-"
            f"{random_part}"
        )

        if not User.objects.filter(
            sevispass_id=sevispass_id
        ).exists():

            return sevispass_id


# ============================================================
# GENERATE SEVISPASS OTP
# ============================================================

def generate_sevispass_otp(user):
    """
    Generate a 6-digit one-time PIN for
    test SevisPass verification.

    OTP expires after 10 minutes.
    """

    # --------------------------------------------------------
    # Invalidate previous unused OTPs
    # --------------------------------------------------------

    SevisPassOTP.objects.filter(
        user=user,
        used=False
    ).update(
        used=True
    )

    # --------------------------------------------------------
    # Generate 6-digit OTP
    # --------------------------------------------------------

    otp = f"{secrets.randbelow(1000000):06d}"

    # --------------------------------------------------------
    # Store hashed OTP
    # --------------------------------------------------------

    otp_record = SevisPassOTP.objects.create(

        user=user,

        otp_hash=make_password(
            otp
        ),

        expires_at=(
            timezone.now()
            + timedelta(minutes=3)
        ),
    )

    return otp_record, otp


# ============================================================
# VERIFY SEVISPASS OTP
# ============================================================

def verify_sevispass_otp(user, otp):
    """
    Verify the latest valid SevisPass OTP.

    Security:
    - OTP is valid for 3 minutes.
    - Maximum 5 verification attempts.
    - OTP is invalidated after successful verification.
    - OTP is invalidated after the maximum attempts are reached.
    """

    if not user:
        return False

    otp = str(otp).strip()

    if len(otp) != 6 or not otp.isdigit():
        return False

    otp_record = (
        SevisPassOTP.objects
        .filter(
            user=user,
            used=False
        )
        .order_by(
            "-created_at"
        )
        .first()
    )

    if not otp_record:
        return False

    # --------------------------------------------------------
    # CHECK EXPIRATION
    # --------------------------------------------------------

    if otp_record.is_expired():

        otp_record.used = True

        otp_record.save(
            update_fields=["used"]
        )

        return False

    # --------------------------------------------------------
    # CHECK MAXIMUM ATTEMPTS
    # --------------------------------------------------------

    if otp_record.attempts >= 5:

        otp_record.used = True

        otp_record.save(
            update_fields=["used"]
        )

        return False

    # --------------------------------------------------------
    # RECORD ATTEMPT
    # --------------------------------------------------------

    otp_record.attempts += 1

    otp_record.save(
        update_fields=["attempts"]
    )

    # --------------------------------------------------------
    # VERIFY OTP
    # --------------------------------------------------------

    if not check_password(
        otp,
        otp_record.otp_hash
    ):

        # Invalidate after 5th failed attempt
        if otp_record.attempts >= 5:

            otp_record.used = True

            otp_record.save(
                update_fields=["used"]
            )

        return False

    # --------------------------------------------------------
    # SUCCESSFUL VERIFICATION
    # --------------------------------------------------------

    otp_record.used = True

    otp_record.verified_at = timezone.now()

    otp_record.save(
        update_fields=[
            "used",
            "verified_at"
        ]
    )

    user.sevispass_verified = True

    user.sevispass_verified_at = timezone.now()

    user.save(
        update_fields=[
            "sevispass_verified",
            "sevispass_verified_at"
        ]
    )

    return True

# ============================================================
# VERIFY SEVISPASS ID
# ============================================================

def verify_sevispass(sevispass_id):
    """
    Find an active BlueShield user using their
    registered SevisPass ID.

    The user does not need to be SevisPass verified yet.
    OTP verification is responsible for completing
    the verification process.
    """

    if not sevispass_id:
        return None

    try:

        user = (
            User.objects
            .select_related(
                "district",
                "station",
                "division"
            )
            .get(
                sevispass_id=sevispass_id,
                is_active=True
            )
        )

        return user

    except User.DoesNotExist:

        return None



# ============================================================
# SYSTEM ACTIVITY / AUDIT LOGGING
# ============================================================

def log_activity(
    request,
    action,
    target_model,
    target_id="",
    details="",
):
    """
    Record an important user activity in BlueShield.

    Records:
    - User who performed the action
    - Action performed
    - Record affected
    - IP address
    - Additional details
    """

    from audit_logs.models import AuditLog

    user = (
        request.user
        if request.user.is_authenticated
        else None
    )

    ip_address = request.META.get(
        "REMOTE_ADDR"
    )

    AuditLog.objects.create(
        user=user,
        action=action,
        target_model=target_model,
        target_id=str(target_id),
        ip_address=ip_address,
        details=details,
    )