
import secrets

from datetime import timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.utils import timezone

from .models import User, SevisPassOTP


# ============================================================
# BLUESHIELD USERNAME GENERATOR
# ============================================================

def generate_blueshield_username():
    """
    Generate a unique BlueShield username.
    """

    while True:

        username = (
            f"BS-"
            f"{secrets.token_hex(3).upper()}"
        )

        if not User.objects.filter(
            username=username
        ).exists():

            return username


# ============================================================
# TEMPORARY PASSWORD GENERATOR
# ============================================================

def generate_temporary_password():
    """
    Generate a temporary password for a newly
    created BlueShield user.
    """

    return (
        f"BS!"
        f"{secrets.token_urlsafe(8)}"
    )


# ============================================================
# SEVISPASS ID GENERATOR
# ============================================================

def generate_sevispass_id():
    """
    Generate a unique SevisPass ID.

    Example:
        PNG-SP-2026-4A5B9D1
    """

    year = timezone.now().year

    while True:

        sevispass_id = (
            f"PNG-SP-"
            f"{year}-"
            f"{secrets.token_hex(4).upper()}"
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
    Generate a secure 6-digit SevisPass OTP.

    Security features:
        - Uses Python secrets for random generation.
        - OTP is valid for 3 minutes.
        - OTP is stored as a password hash.
        - Previous unused OTPs are invalidated.
        - Plain OTP is returned only for email delivery.
    """

    # --------------------------------------------------------
    # Invalidate previous unused OTPs
    # --------------------------------------------------------

    SevisPassOTP.objects.filter(
        user=user,
        used=False,
    ).update(
        used=True
    )

    # --------------------------------------------------------
    # Generate secure 6-digit OTP
    # --------------------------------------------------------

    otp = (
        f"{secrets.randbelow(1_000_000):06d}"
    )

    # --------------------------------------------------------
    # Hash OTP before storing it
    # --------------------------------------------------------

    otp_hash = make_password(
        otp
    )

    # --------------------------------------------------------
    # Set 3-minute expiry
    # --------------------------------------------------------

    now = timezone.now()

    expires_at = (
        now +
        timedelta(minutes=3)
    )

    # --------------------------------------------------------
    # Create OTP record
    # --------------------------------------------------------

    otp_record = SevisPassOTP.objects.create(
        user=user,
        otp_hash=otp_hash,
        created_at=now,
        expires_at=expires_at,
        used=False,
        attempts=0,
    )

    return otp_record, otp


# ============================================================
# SEND SEVISPASS OTP BY EMAIL
# ============================================================

def send_sevispass_otp_email(user, otp):
    """
    Send the SevisPass OTP to the user's registered email
    address using Django's configured Gmail SMTP server.
    """

    # --------------------------------------------------------
    # Make sure the user has an email address
    # --------------------------------------------------------

    if not user.email:

        raise ValueError(
            "This BlueShield account does not have a "
            "registered email address."
        )

    # --------------------------------------------------------
    # Email subject
    # --------------------------------------------------------

    subject = (
        "BlueShield SevisPass Verification Code"
    )

    # --------------------------------------------------------
    # Email message
    # --------------------------------------------------------

    message = f"""
Hello {user.first_name or user.username},

Your BlueShield SevisPass verification code is:

{otp}

This verification code is valid for 3 minutes.

For your security:

- Do not share this code with anyone.
- BlueShield staff will never ask you to provide your OTP.
- If you did not request this verification code, you can safely ignore this email.

Regards,

BlueShield
Madang Provincial Police Command
SevisPass Security System
""".strip()

    # --------------------------------------------------------
    # Send email
    # --------------------------------------------------------

    try:

        sent_count = send_mail(
            subject=subject,
            message=message,
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
        )

    except Exception:

        raise RuntimeError(
            "The SevisPass OTP email could not be sent."
        )

    # --------------------------------------------------------
    # Confirm successful delivery request
    # --------------------------------------------------------

    if sent_count != 1:

        raise RuntimeError(
            "The SevisPass OTP email could not be sent."
        )

    return True


# ============================================================
# VERIFY SEVISPASS OTP
# ============================================================

def verify_sevispass_otp(user, otp):
    """
    Verify the latest unused SevisPass OTP.

    Security rules:
        - OTP must contain exactly 6 digits.
        - OTP must not be expired.
        - Maximum 5 attempts.
        - OTP can only be used once.
        - OTP is marked as used after successful verification.
    """

    # --------------------------------------------------------
    # Validate OTP format
    # --------------------------------------------------------

    if not otp:

        return False

    otp = str(otp).strip()

    if (
        len(otp) != 6
        or not otp.isdigit()
    ):

        return False

    # --------------------------------------------------------
    # Get latest unused OTP
    # --------------------------------------------------------

    otp_record = (
        SevisPassOTP.objects
        .filter(
            user=user,
            used=False,
        )
        .order_by("-created_at")
        .first()
    )

    if not otp_record:

        return False

    # --------------------------------------------------------
    # Check expiry
    # --------------------------------------------------------

    if otp_record.is_expired():

        otp_record.used = True

        otp_record.save(
            update_fields=[
                "used"
            ]
        )

        return False

    # --------------------------------------------------------
    # Maximum attempts
    # --------------------------------------------------------

    MAX_ATTEMPTS = 5

    if otp_record.attempts >= MAX_ATTEMPTS:

        otp_record.used = True

        otp_record.save(
            update_fields=[
                "used"
            ]
        )

        return False

    # --------------------------------------------------------
    # Increase attempt counter
    # --------------------------------------------------------

    otp_record.attempts += 1

    otp_record.save(
        update_fields=[
            "attempts"
        ]
    )

    # --------------------------------------------------------
    # Compare entered OTP with stored hash
    # --------------------------------------------------------

    if not check_password(
        otp,
        otp_record.otp_hash,
    ):

        # Invalidate OTP after fifth failed attempt.

        if otp_record.attempts >= MAX_ATTEMPTS:

            otp_record.used = True

            otp_record.save(
                update_fields=[
                    "used"
                ]
            )

        return False

    # --------------------------------------------------------
    # OTP is correct
    # --------------------------------------------------------

    now = timezone.now()

    otp_record.used = True
    otp_record.verified_at = now

    otp_record.save(
        update_fields=[
            "used",
            "verified_at",
        ]
    )

    # --------------------------------------------------------
    # Mark SevisPass as verified
    # --------------------------------------------------------

    user.sevispass_verified = True
    user.sevispass_verified_at = now

    user.save(
        update_fields=[
            "sevispass_verified",
            "sevispass_verified_at",
        ]
    )

    return True


# ============================================================
# VERIFY SEVISPASS ID
# ============================================================

def verify_sevispass(sevispass_id):
    """
    Find an active BlueShield user using their SevisPass ID.

    The user must have:
        - a matching SevisPass ID
        - an active account
    """

    if not sevispass_id:

        return None

    sevispass_id = sevispass_id.strip()

    user = (
        User.objects
        .select_related(
            "district",
            "station",
            "division",
        )
        .filter(
            sevispass_id=sevispass_id,
            is_active=True,
        )
        .first()
    )

    return user


# ============================================================
# ACTIVITY LOGGING
# ============================================================

def log_activity(
    *,
    user,
    action,
    request=None,
    target_model="",
    target_id=None,
    details="",
):
    """
    Create a BlueShield audit log entry.
    """

    from audit_logs.models import AuditLog

    ip_address = None

    if request:

        forwarded_for = request.META.get(
            "HTTP_X_FORWARDED_FOR"
        )

        if forwarded_for:

            ip_address = (
                forwarded_for
                .split(",")[0]
                .strip()
            )

        else:

            ip_address = request.META.get(
                "REMOTE_ADDR"
            )

    return AuditLog.objects.create(
        user=user,
        action=action,
        target_model=target_model,
        target_id=target_id,
        ip_address=ip_address,
        details=details,
    )

