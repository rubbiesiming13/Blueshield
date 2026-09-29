# accounts/views.py

from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.dateparse import parse_date

from .forms import (
    LoginForm,
    SevisPassVerificationForm,
    SevisPassOTPForm,
)

from .models import (
    User,
    SevisPassOTP,
)

from .services import (
    verify_sevispass,
    generate_sevispass_otp,
    verify_sevispass_otp,
    send_sevispass_otp_email,
)

from complaints.models import Complaint
from cases.models import Case
from suspects.models import Suspect
from records.models import ArrestRecord, CriminalOffence
from warrant.models import Warrant
from stations.models import District, PoliceStation
from prosecution.models import Prosecution
from audit_logs.models import AuditLog


# ============================================================
# HELPER - MASK EMAIL ADDRESS
# ============================================================

def mask_email(email):
    """
    Hide most of the email address while still showing
    enough information for the user to identify it.

    Example:
        rubbie@gmail.com
        becomes:
        r*****@gmail.com
    """

    if not email:
        return "registered email address"

    email = email.strip()

    if "@" not in email:
        return "registered email address"

    local_part, domain = email.split("@", 1)

    if not local_part:
        return "registered email address"

    if len(local_part) == 1:
        masked_local = local_part

    elif len(local_part) == 2:
        masked_local = local_part[0] + "*"

    else:
        masked_local = (
            local_part[0]
            + "*" * min(len(local_part) - 1, 5)
        )

    return masked_local + "@" + domain


# ============================================================
# SEVISPASS ID VERIFICATION
# ============================================================

def sevispass_verify_view(request):

    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    # --------------------------------------------------------
    # Clear old verification/pending session data
    # --------------------------------------------------------

    request.session.pop("sevispass_user_id", None)
    request.session.pop("sevispass_verified", None)
    request.session.pop("sevispass_verified_at", None)
    request.session.pop("verified_sevispass_id", None)

    request.session.pop("sevispass_pending_user_id", None)
    request.session.pop("sevispass_pending_sevispass_id", None)
    request.session.pop("sevispass_otp_expires_at", None)
    request.session.pop("sevispass_otp_sent_at", None)
    request.session.pop("sevispass_masked_email", None)

    # --------------------------------------------------------
    # PROCESS SEVISPASS ID
    # --------------------------------------------------------

    if request.method == "POST":

        form = SevisPassVerificationForm(request.POST)

        if form.is_valid():

            sevispass_id = (
                form.cleaned_data["sevispass_id"].strip()
            )

            # ------------------------------------------------
            # FIND ACTIVE USER
            # ------------------------------------------------

            user = verify_sevispass(sevispass_id)

            if user:

                # ------------------------------------------------
                # REQUIRE REGISTERED EMAIL ADDRESS
                # ------------------------------------------------

                email = str(user.email or "").strip()

                if not email:

                    messages.error(
                        request,
                        (
                            "No registered email address is "
                            "available for this account. "
                            "Please contact the system administrator."
                        ),
                    )

                    return render(
                        request,
                        "accounts/sevispass_verify.html",
                        {
                            "form": form,
                        },
                    )

                # ------------------------------------------------
                # STORE PENDING USER
                # ------------------------------------------------

                request.session[
                    "sevispass_pending_user_id"
                ] = user.id

                request.session[
                    "sevispass_pending_sevispass_id"
                ] = user.sevispass_id

                # ------------------------------------------------
                # MASK EMAIL ADDRESS
                # ------------------------------------------------

                masked_email = mask_email(email)

                request.session[
                    "sevispass_masked_email"
                ] = masked_email

                # ------------------------------------------------
                # GENERATE AND SEND OTP
                # ------------------------------------------------

                otp_record = None

                try:

                    otp_record, otp = (
                        generate_sevispass_otp(user)
                    )

                    send_sevispass_otp_email(
                        user,
                        otp,
                    )

                except Exception as e:

                    print("=" * 70)
                    print("SEVISPASS EMAIL ERROR")
                    print("Exception type:", type(e).__name__)
                    print("Exception:", str(e))
                    print("User:", user.username)
                    print("Email:", user.email)
                    print("SMTP TLS:", settings.EMAIL_USE_TLS)
                    print("=" * 70)

    

                    # --------------------------------------------
                    # Prevent an OTP that was not successfully
                    # delivered from remaining usable.
                    # --------------------------------------------

                    if otp_record is not None:

                        otp_record.used = True

                        otp_record.save(
                            update_fields=["used"]
                        )

                    # --------------------------------------------
                    # Remove pending verification data.
                    # --------------------------------------------

                    request.session.pop(
                        "sevispass_pending_user_id",
                        None,
                    )

                    request.session.pop(
                        "sevispass_pending_sevispass_id",
                        None,
                    )

                    request.session.pop(
                        "sevispass_masked_email",
                        None,
                    )

                    request.session.pop(
                        "sevispass_otp_expires_at",
                        None,
                    )

                    request.session.pop(
                        "sevispass_otp_sent_at",
                        None,
                    )

                    messages.error(
                        request,
                        (
                            "We could not send the "
                            "SevisPass verification code "
                            "to your registered email address. "
                            "Please check the email configuration "
                            "or contact the system administrator."
                        ),
                    )

                    return render(
                        request,
                        "accounts/sevispass_verify.html",
                        {
                            "form": form,
                        },
                    )


                # ------------------------------------------------
                # STORE OTP INFORMATION IN SESSION
                # ------------------------------------------------

                request.session[
                    "sevispass_otp_expires_at"
                ] = otp_record.expires_at.isoformat()

                request.session[
                    "sevispass_otp_sent_at"
                ] = timezone.now().isoformat()

                # ------------------------------------------------
                # SUCCESS
                # ------------------------------------------------

                messages.success(
                    request,
                    (
                        "SevisPass ID verified. "
                        f"A 6-digit verification code has "
                        f"been sent to {masked_email}."
                    ),
                )

                return redirect(
                    "accounts:sevispass_otp"
                )

            # ------------------------------------------------
            # INVALID SEVISPASS ID
            # ------------------------------------------------

            messages.error(
                request,
                (
                    "SevisPass verification failed. "
                    "Please check your SevisPass ID "
                    "or contact the system administrator."
                ),
            )

    else:

        form = SevisPassVerificationForm()

    return render(
        request,
        "accounts/sevispass_verify.html",
        {
            "form": form,
        },
    )


# ============================================================
# SEVISPASS OTP VERIFICATION USING GMAIL SMTP
# ============================================================

def sevispass_otp_view(request):

    # --------------------------------------------------------
    # USER MUST HAVE A PENDING SEVISPASS VERIFICATION
    # --------------------------------------------------------

    pending_user_id = request.session.get(
        "sevispass_pending_user_id"
    )

    if not pending_user_id:

        messages.error(
            request,
            (
                "Your SevisPass verification session "
                "has expired. Please start again."
            ),
        )

        return redirect(
            "accounts:sevispass_verify"
        )

    # --------------------------------------------------------
    # GET USER
    # --------------------------------------------------------

    try:

        user = (
            User.objects
            .select_related(
                "district",
                "station",
                "division",
            )
            .get(
                id=pending_user_id,
                is_active=True,
            )
        )

    except User.DoesNotExist:

        request.session.flush()

        messages.error(
            request,
            (
                "The BlueShield account could not be found. "
                "Please contact the system administrator."
            ),
        )

        return redirect(
            "accounts:sevispass_verify"
        )

    # --------------------------------------------------------
    # GET REGISTERED EMAIL
    # --------------------------------------------------------

    email = str(user.email or "").strip()

    if not email:

        request.session.flush()

        messages.error(
            request,
            (
                "No registered email address is "
                "available for this account."
            ),
        )

        return redirect(
            "accounts:sevispass_verify"
        )

    # --------------------------------------------------------
    # CONFIRM PENDING SEVISPASS ID MATCHES USER
    # --------------------------------------------------------

    pending_sevispass_id = request.session.get(
        "sevispass_pending_sevispass_id"
    )

    if (
        pending_sevispass_id
        and pending_sevispass_id != user.sevispass_id
    ):

        request.session.flush()

        messages.error(
            request,
            (
                "The SevisPass verification session is "
                "invalid. Please start again."
            ),
        )

        return redirect(
            "accounts:sevispass_verify"
        )

    # --------------------------------------------------------
    # MASK EMAIL
    # --------------------------------------------------------

    masked_email = request.session.get(
        "sevispass_masked_email"
    )

    if not masked_email:

        masked_email = mask_email(email)

        request.session[
            "sevispass_masked_email"
        ] = masked_email

    # --------------------------------------------------------
    # OTP EXPIRY
    # --------------------------------------------------------

    otp_expires_at = request.session.get(
        "sevispass_otp_expires_at"
    )

    # --------------------------------------------------------
    # ALWAYS INITIALIZE OTP FORM
    # --------------------------------------------------------

    form = SevisPassOTPForm()

    # --------------------------------------------------------
    # PROCESS POST REQUEST
    # --------------------------------------------------------

    if request.method == "POST":

        action = request.POST.get(
            "action",
            "verify",
        ).strip()

        # ====================================================
        # VERIFY OTP
        # ====================================================

        if action == "verify":

            form = SevisPassOTPForm(
                request.POST
            )

            if form.is_valid():

                otp = form.cleaned_data["otp"]

                verified = verify_sevispass_otp(
                    user,
                    otp,
                )

                if verified:

                    # ----------------------------------------
                    # SET SUCCESSFUL SEVISPASS SESSION
                    # ----------------------------------------

                    request.session[
                        "sevispass_verified"
                    ] = True

                    request.session[
                        "sevispass_user_id"
                    ] = user.id

                    request.session[
                        "verified_sevispass_id"
                    ] = user.sevispass_id

                    request.session[
                        "sevispass_verified_at"
                    ] = timezone.now().isoformat()

                    # ----------------------------------------
                    # REMOVE TEMPORARY OTP DATA
                    # ----------------------------------------

                    request.session.pop(
                        "sevispass_pending_user_id",
                        None,
                    )

                    request.session.pop(
                        "sevispass_pending_sevispass_id",
                        None,
                    )

                    request.session.pop(
                        "sevispass_otp_expires_at",
                        None,
                    )

                    request.session.pop(
                        "sevispass_otp_sent_at",
                        None,
                    )

                    request.session.pop(
                        "sevispass_masked_email",
                        None,
                    )

                    # ----------------------------------------
                    # SUCCESS MESSAGE
                    # ----------------------------------------

                    
                    return redirect(
                        "accounts:login"
                    )

                # --------------------------------------------
                # INVALID OTP
                # --------------------------------------------

                messages.error(
                    request,
                    (
                        "The verification code is incorrect, "
                        "expired, or has already been used. "
                        "Please try again."
                    ),
                )

            else:

                messages.error(
                    request,
                    (
                        "Please enter the 6-digit "
                        "verification code."
                    ),
                )

        # ====================================================
        # RESEND OTP
        # ====================================================

        elif action == "resend":

            # ------------------------------------------------
            # SERVER-SIDE RESEND COOLDOWN
            # ------------------------------------------------

            last_sent_at = request.session.get(
                "sevispass_otp_sent_at"
            )

            can_resend = True

            if last_sent_at:

                try:

                    last_sent_time = (
                        datetime.fromisoformat(
                            last_sent_at
                        )
                    )

                    # Make sure datetime is timezone-aware.
                    if timezone.is_naive(
                        last_sent_time
                    ):

                        last_sent_time = (
                            timezone.make_aware(
                                last_sent_time
                            )
                        )

                    seconds_since_last_send = (
                        timezone.now()
                        - last_sent_time
                    ).total_seconds()

                    if seconds_since_last_send < 30:

                        can_resend = False

                except (
                    ValueError,
                    TypeError,
                ):

                    can_resend = True

            # ------------------------------------------------
            # COOLDOWN STILL ACTIVE
            # ------------------------------------------------

            if not can_resend:

                messages.warning(
                    request,
                    (
                        "Please wait 30 seconds "
                        "before requesting another "
                        "verification code."
                    ),
                )

            # ------------------------------------------------
            # SEND NEW OTP
            # ------------------------------------------------

            else:

                otp_record = None

                try:

                    # ----------------------------------------
                    # GENERATE NEW OTP
                    # ----------------------------------------

                    otp_record, otp = (
                        generate_sevispass_otp(
                            user
                        )
                    )

                    # ----------------------------------------
                    # SEND NEW OTP THROUGH GMAIL
                    # ----------------------------------------

                    send_sevispass_otp_email(
                        user,
                        otp,
                    )

                except Exception:

                    # ----------------------------------------
                    # Prevent an undelivered OTP from
                    # remaining usable.
                    # ----------------------------------------

                    if otp_record is not None:

                        otp_record.used = True

                        otp_record.save(
                            update_fields=["used"]
                        )

                    messages.error(
                        request,
                        (
                            "We could not send a new "
                            "verification code. Please "
                            "try again or contact the "
                            "system administrator."
                        ),
                    )

                else:

                    # ----------------------------------------
                    # UPDATE SESSION
                    # ----------------------------------------

                    request.session[
                        "sevispass_otp_expires_at"
                    ] = (
                        otp_record
                        .expires_at
                        .isoformat()
                    )

                    request.session[
                        "sevispass_otp_sent_at"
                    ] = timezone.now().isoformat()

                    request.session[
                        "sevispass_masked_email"
                    ] = mask_email(
                        user.email
                    )

                    # Update local values too.
                    masked_email = (
                        request.session[
                            "sevispass_masked_email"
                        ]
                    )

                    otp_expires_at = (
                        request.session[
                            "sevispass_otp_expires_at"
                        ]
                    )

                    messages.success(
                        request,
                        (
                            "A new verification code has "
                            f"been sent to {masked_email}."
                        ),
                    )

        # ====================================================
        # INVALID ACTION
        # ====================================================

        else:

            messages.error(
                request,
                "Invalid SevisPass verification request.",
            )

    # --------------------------------------------------------
    # GET CURRENT OTP RECORD
    # --------------------------------------------------------

    otp_record = (
        SevisPassOTP.objects
        .filter(
            user=user,
            used=False,
        )
        .order_by(
            "-created_at"
        )
        .first()
    )

    # --------------------------------------------------------
    # CALCULATE REMAINING ATTEMPTS
    # --------------------------------------------------------

    max_attempts = 5

    if otp_record:

        attempts_remaining = max(
            0,
            max_attempts - otp_record.attempts,
        )

    else:

        attempts_remaining = 0

    # --------------------------------------------------------
    # RENDER OTP PAGE
    # --------------------------------------------------------

    return render(
        request,
        "accounts/sevispass_otp.html",
        {
            "form": form,
            "masked_email": masked_email,
            "otp_expires_at": otp_expires_at,
            "attempts_remaining": attempts_remaining,
            "max_attempts": max_attempts,
        },
    )


# ============================================================
# BLUESHIELD LOGIN
# ============================================================

def login_view(request):

    if request.user.is_authenticated:

        return redirect(
            "accounts:dashboard"
        )

    # --------------------------------------------------------
    # REQUIRE SUCCESSFUL SEVISPASS VERIFICATION
    # --------------------------------------------------------

    if not request.session.get(
        "sevispass_verified"
    ):

        return redirect(
            "accounts:sevispass_verify"
        )

    # --------------------------------------------------------
    # GET VERIFIED SEVISPASS USER
    # --------------------------------------------------------

    sevispass_user_id = request.session.get(
        "sevispass_user_id"
    )

    verified_sevispass_id = request.session.get(
        "verified_sevispass_id"
    )

    if not sevispass_user_id or not verified_sevispass_id:

        request.session.flush()

        messages.error(
            request,
            (
                "Your SevisPass verification session "
                "is incomplete. Please verify again."
            ),
        )

        return redirect(
            "accounts:sevispass_verify"
        )

    try:

        sevispass_user = (
            User.objects
            .select_related(
                "district",
                "station",
                "division",
            )
            .get(
                id=sevispass_user_id,
                is_active=True,
            )
        )

    except User.DoesNotExist:

        request.session.flush()

        messages.error(
            request,
            (
                "Your SevisPass verification session "
                "has expired. Please verify again."
            ),
        )

        return redirect(
            "accounts:sevispass_verify"
        )

    # --------------------------------------------------------
    # CONFIRM SESSION SEVISPASS ID MATCHES USER
    # --------------------------------------------------------

    if verified_sevispass_id != sevispass_user.sevispass_id:

        request.session.flush()

        messages.error(
            request,
            (
                "Your SevisPass verification session "
                "is invalid. Please verify again."
            ),
        )

        return redirect(
            "accounts:sevispass_verify"
        )

    # --------------------------------------------------------
    # PROCESS BLUESHIELD LOGIN
    # --------------------------------------------------------

    if request.method == "POST":

        form = LoginForm(
            request.POST
        )

        if form.is_valid():

            username = (
                form.cleaned_data[
                    "username"
                ].strip()
            )

            password = (
                form.cleaned_data[
                    "password"
                ]
            )

            # ------------------------------------------------
            # AUTHENTICATE BLUESHIELD ACCOUNT
            # ------------------------------------------------

            user = authenticate(
                request,
                username=username,
                password=password,
            )

            # ------------------------------------------------
            # INVALID USERNAME OR PASSWORD
            # ------------------------------------------------

            if user is None:

                messages.error(
                    request,
                    (
                        "Invalid BlueShield username "
                        "or password."
                    ),
                )

                return render(
                    request,
                    "accounts/login.html",
                    {
                        "form": form,
                        "sevispass_user": sevispass_user,
                    },
                )

            # ------------------------------------------------
            # CHECK ACTIVE ACCOUNT
            # ------------------------------------------------

            if not user.is_active:

                messages.error(
                    request,
                    "Your BlueShield account is inactive.",
                )

                return redirect(
                    "accounts:login"
                )

            # ------------------------------------------------
            # CONFIRM SAME USER
            # ------------------------------------------------

            if user.id != sevispass_user.id:

                messages.error(
                    request,
                    (
                        "The BlueShield account does not "
                        "match the verified SevisPass identity."
                    ),
                )

                request.session.flush()

                return redirect(
                    "accounts:sevispass_verify"
                )

            # ------------------------------------------------
            # CONFIRM USER SEVISPASS ID
            # ------------------------------------------------

            if user.sevispass_id != verified_sevispass_id:

                messages.error(
                    request,
                    (
                        "The BlueShield account does not "
                        "match the verified SevisPass identity."
                    ),
                )

                request.session.flush()

                return redirect(
                    "accounts:sevispass_verify"
                )

            # ------------------------------------------------
            # CONFIRM SEVISPASS IS STILL VERIFIED
            # ------------------------------------------------

            if not user.sevispass_verified:

                messages.error(
                    request,
                    (
                        "Your SevisPass identity verification "
                        "is no longer active. Please verify again."
                    ),
                )

                request.session.flush()

                return redirect(
                    "accounts:sevispass_verify"
                )

            # ------------------------------------------------
            # COMPLETE DJANGO LOGIN
            # ------------------------------------------------

            login(
                request,
                user,
            )

            # ------------------------------------------------
            # RECORD LOGIN IN AUDIT LOG
            # ------------------------------------------------

            AuditLog.objects.create(
                user=user,
                action=AuditLog.Action.LOGIN,
                target_model="User",
                target_id=str(user.id),
                ip_address=request.META.get(
                    "REMOTE_ADDR"
                ),
                details=(
                    "User successfully logged into "
                    "BlueShield. "
                    f"Role: {user.get_role_display()}. "
                    "Station: "
                    f"{user.station.name if user.station else 'N/A'}. "
                    "District: "
                    f"{user.district.name if user.district else 'N/A'}."
                ),
            )

            # ------------------------------------------------
            # KEEP VERIFIED SEVISPASS INFORMATION
            # ------------------------------------------------

            request.session[
                "sevispass_verified"
            ] = True

            request.session[
                "sevispass_user_id"
            ] = user.id

            request.session[
                "verified_sevispass_id"
            ] = user.sevispass_id

            request.session[
                "sevispass_verified_at"
            ] = timezone.now().isoformat()

            # ------------------------------------------------
            # WELCOME MESSAGE
            # ------------------------------------------------

            messages.success(
                request,
                (
                    f"Welcome to BlueShield, "
                    f"{user.get_full_name() or user.username}."
                ),
            )

            # ------------------------------------------------
            # ROLE IS AUTOMATICALLY DETERMINED
            # ------------------------------------------------

            return redirect(
                "accounts:dashboard"
            )

    else:

        form = LoginForm()

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
            "sevispass_user": sevispass_user,
        },
    )


# ============================================================
# LOGOUT
# ============================================================

@login_required
def logout_view(request):

    # --------------------------------------------------------
    # RECORD LOGOUT BEFORE DJANGO LOGOUT
    # --------------------------------------------------------

    AuditLog.objects.create(
        user=request.user,
        action=AuditLog.Action.LOGOUT,
        target_model="User",
        target_id=str(request.user.id),
        ip_address=request.META.get(
            "REMOTE_ADDR"
        ),
        details=(
            "User securely logged out of BlueShield."
        ),
    )

    # --------------------------------------------------------
    # LOGOUT
    # --------------------------------------------------------

    logout(request)

    request.session.flush()

    messages.success(
        request,
        "You have been securely logged out of BlueShield.",
    )

    return redirect(
        "accounts:sevispass_verify"
    )


# ============================================================
# MONTH DATE RANGES
# ============================================================

def get_month_ranges():

    today = timezone.localdate()

    current_month_start = today.replace(
        day=1
    )

    previous_month_end = (
        current_month_start
        - timedelta(days=1)
    )

    previous_month_start = (
        previous_month_end.replace(
            day=1
        )
    )

    return (
        current_month_start,
        today,
        previous_month_start,
        previous_month_end,
    )


# ============================================================
# POLICE OFFICERS
# ============================================================

@login_required
def police_officers(request):

    officers = (
        User.objects
        .filter(
            role="OFFICER"
        )
        .select_related(
            "district",
            "station",
            "division",
        )
        .order_by(
            "username"
        )
    )

    return render(
        request,
        "dashboards/police_officers.html",
        {
            "officers": officers,
        },
    )


# ============================================================
# POLICE STATIONS
# ============================================================

@login_required
def police_stations(request):

    stations = (
        PoliceStation.objects
        .select_related(
            "district"
        )
        .order_by(
            "district__name",
            "name",
        )
    )

    return render(
        request,
        "dashboards/police_stations.html",
        {
            "stations": stations,
        },
    )


# ============================================================
# DASHBOARD
# ============================================================

@login_required
def dashboard(request):

    user = request.user

    (
        current_month_start,
        today,
        previous_month_start,
        previous_month_end,
    ) = get_month_ranges()

    dashboard_data = {
        "user": user,
        "role": user.role,
    }

    # ========================================================
    # POLICE OFFICER DASHBOARD
    # ========================================================

    if user.role == "OFFICER":

        station = user.station

        if station:

            # ========================================================
            # OFFICER OWN COMPLAINTS
            # ========================================================

            total_complaints = Complaint.objects.filter(
                reported_by=user
            ).count()

            # ========================================================
            # OFFICER OWN CASES
            # ========================================================

            total_cases = Case.objects.filter(
                investigating_officer=user
            ).count()

            # ========================================================
            # OFFICER OWN ARRESTS
            # ========================================================

            total_arrests = ArrestRecord.objects.filter(
                arresting_officer=user
            ).count()

            # ========================================================
            # OFFICER OWN SUSPECTS
            # ========================================================

            total_suspects = Suspect.objects.filter(
                registered_by=user
            ).count()

            # ========================================================
            # ACTIVE INVESTIGATIONS
            # ========================================================

            active_investigations = Case.objects.filter(
                investigating_officer=user,
                status=Case.Status.UNDER_INVESTIGATION,
            ).count()

            # ========================================================
            # CASES PREPARED FOR REVIEW
            # ========================================================

            cases_for_review = Case.objects.filter(
                investigating_officer=user,
                status=Case.Status.CASE_FILE_PREPARED,
            ).count()

            # ========================================================
            # CLOSED CASES
            # ========================================================

            closed_cases = Case.objects.filter(
                investigating_officer=user,
                status=Case.Status.CLOSED,
            ).count()

            # ========================================================
            # MONTHLY ARRESTS
            # ========================================================

            monthly_arrests = ArrestRecord.objects.filter(
                arresting_officer=user,
                arrest_datetime__date__gte=current_month_start,
                arrest_datetime__date__lte=today,
            ).count()

            # ========================================================
            # RECENT ARRESTS
            # ========================================================

            recent_arrests = (
                ArrestRecord.objects
                .filter(
                    arresting_officer=user
                )
                .select_related(
                    "suspect",
                    "case",
                    "arresting_officer",
                    "station",
                )
                .prefetch_related(
                    "offences"
                )
                .order_by(
                    "-created_at"
                )[:10]
            )

        else:

            total_complaints = 0
            total_cases = 0
            total_arrests = 0
            total_suspects = 0
            active_investigations = 0
            cases_for_review = 0
            closed_cases = 0
            monthly_arrests = 0
            recent_arrests = []

        dashboard_data.update(
            {
                "total_complaints": total_complaints,
                "total_cases": total_cases,
                "total_arrests": total_arrests,
                "total_suspects": total_suspects,
                "active_investigations": active_investigations,
                "cases_for_review": cases_for_review,
                "closed_cases": closed_cases,
                "monthly_arrests": monthly_arrests,
                "recent_arrests": recent_arrests,
            }
        )

        return render(
            request,
            "dashboards/officer_dashboard.html",
            dashboard_data,
        )

    # ========================================================
    # STATION COMMANDER DASHBOARD
    # ========================================================

    elif user.role == "STATION_COMMANDER":

        station = user.station

        if station:

            officer_count = User.objects.filter(
                station=station,
                role="OFFICER",
                is_active=True,
            ).count()

            total_complaints = Complaint.objects.filter(
                station=station
            ).count()

            total_cases = Case.objects.filter(
                station=station
            ).count()

            total_arrests = ArrestRecord.objects.filter(
                station=station
            ).count()

            total_suspects = Suspect.objects.filter(
                station=station
            ).count()

            active_investigations = Case.objects.filter(
                station=station,
                status=Case.Status.UNDER_INVESTIGATION,
            ).count()

            cases_for_review = Case.objects.filter(
                station=station,
                status=Case.Status.CASE_FILE_PREPARED,
            ).count()

            solved_cases = Case.objects.filter(
                station=station,
                status=Case.Status.CLOSED,
            ).count()

            monthly_arrests = ArrestRecord.objects.filter(
                station=station,
                arrest_datetime__date__gte=current_month_start,
                arrest_datetime__date__lte=today,
            ).count()

            officer_activity = (
                User.objects
                .filter(
                    station=station,
                    role="OFFICER",
                    is_active=True,
                )
                .annotate(
                    complaint_count=Count(
                        "complaints_created",
                        distinct=True,
                    ),
                    case_count=Count(
                        "investigated_cases",
                        distinct=True,
                    ),
                    arrest_count=Count(
                        "arrests_made",
                        distinct=True,
                    ),
                )
                .order_by(
                    "-case_count",
                    "-arrest_count",
                )[:10]
            )

            recent_arrests = (
                ArrestRecord.objects
                .filter(
                    station=station
                )
                .select_related(
                    "suspect",
                    "case",
                    "arresting_officer",
                    "station",
                )
                .prefetch_related(
                    "offences"
                )
                .order_by(
                    "-created_at"
                )[:10]
            )

        else:

            officer_count = 0
            total_complaints = 0
            total_cases = 0
            total_arrests = 0
            total_suspects = 0
            active_investigations = 0
            cases_for_review = 0
            solved_cases = 0
            monthly_arrests = 0
            officer_activity = []
            recent_arrests = []

        dashboard_data.update(
            {
                "officer_count": officer_count,
                "total_complaints": total_complaints,
                "total_cases": total_cases,
                "total_arrests": total_arrests,
                "total_suspects": total_suspects,
                "active_investigations": active_investigations,
                "cases_for_review": cases_for_review,
                "solved_cases": solved_cases,
                "monthly_arrests": monthly_arrests,
                "officer_activity": officer_activity,
                "recent_arrests": recent_arrests,
            }
        )

        return render(
            request,
            "dashboards/station_commander_dashboard.html",
            dashboard_data,
        )

    # ========================================================
    # DIVISION ADMIN / PROSECUTION DASHBOARD
    # ========================================================

    elif user.role == "DIVISION_ADMIN":

        division = user.division
        district = user.district

        if division:

            officers = User.objects.filter(
                division=division,
                role="OFFICER",
                is_active=True,
            ).count()

        else:

            officers = 0

        if district:

            commanders = User.objects.filter(
                district=district,
                role="STATION_COMMANDER",
                is_active=True,
            ).count()

            total_complaints = Complaint.objects.filter(
                station__district=district
            ).count()

            total_cases = Case.objects.filter(
                station__district=district
            ).count()

            total_arrests = ArrestRecord.objects.filter(
                station__district=district
            ).count()

            total_suspects = Suspect.objects.filter(
                station__district=district
            ).count()

            active_investigations = Case.objects.filter(
                station__district=district,
                status=Case.Status.UNDER_INVESTIGATION,
            ).count()

            cases_for_review = Case.objects.filter(
                station__district=district,
                status=Case.Status.CASE_FILE_PREPARED,
            ).count()

            solved_cases = Case.objects.filter(
                station__district=district,
                status=Case.Status.CLOSED,
            ).count()

            monthly_arrests = ArrestRecord.objects.filter(
                station__district=district,
                arrest_datetime__date__gte=current_month_start,
                arrest_datetime__date__lte=today,
            ).count()

            pending_prosecutions = Prosecution.objects.filter(
                case__station__district=district,
                status__in=[
                    "SUBMITTED",
                    "UNDER_REVIEW",
                    "RETURNED",
                ],
            ).count()

            recent_arrests = (
                ArrestRecord.objects
                .filter(
                    station__district=district
                )
                .select_related(
                    "suspect",
                    "case",
                    "arresting_officer",
                    "station",
                )
                .prefetch_related(
                    "offences"
                )
                .order_by(
                    "-created_at"
                )[:10]
            )

        else:

            commanders = 0
            total_complaints = 0
            total_cases = 0
            total_arrests = 0
            total_suspects = 0
            active_investigations = 0
            cases_for_review = 0
            solved_cases = 0
            monthly_arrests = 0
            pending_prosecutions = 0
            recent_arrests = []

        dashboard_data.update(
            {
                "officers": officers,
                "commanders": commanders,
                "total_complaints": total_complaints,
                "total_cases": total_cases,
                "total_arrests": total_arrests,
                "total_suspects": total_suspects,
                "active_investigations": active_investigations,
                "cases_for_review": cases_for_review,
                "solved_cases": solved_cases,
                "monthly_arrests": monthly_arrests,
                "pending_prosecutions": pending_prosecutions,
                "recent_arrests": recent_arrests,
            }
        )

        return render(
            request,
            "dashboards/division_admin_dashboard.html",
            dashboard_data,
        )

    # ========================================================
    # PPC / SYSTEM ADMINISTRATOR DASHBOARD
    # ========================================================

    elif user.role == "ADMIN":

        total_complaints = Complaint.objects.count()

        total_officers = User.objects.filter(
            role="OFFICER",
            is_active=True,
        ).count()

        total_commanders = User.objects.filter(
            role="STATION_COMMANDER",
            is_active=True,
        ).count()

        total_stations = PoliceStation.objects.count()

        total_cases = Case.objects.count()

        total_arrests = ArrestRecord.objects.count()

        total_suspects = Suspect.objects.count()

        total_offences = CriminalOffence.objects.count()

        active_investigations = Case.objects.filter(
            status=Case.Status.UNDER_INVESTIGATION
        ).count()

        cases_for_review = Case.objects.filter(
            status=Case.Status.CASE_FILE_PREPARED
        ).count()

        solved_cases = Case.objects.filter(
            status=Case.Status.CLOSED
        ).count()

        current_month_arrests = ArrestRecord.objects.filter(
            arrest_datetime__date__gte=current_month_start,
            arrest_datetime__date__lte=today,
        ).count()

        previous_month_arrests = ArrestRecord.objects.filter(
            arrest_datetime__date__gte=previous_month_start,
            arrest_datetime__date__lte=previous_month_end,
        ).count()

        current_month_suspects = Suspect.objects.filter(
            created_at__date__gte=current_month_start,
            created_at__date__lte=today,
        ).count()

        previous_month_suspects = Suspect.objects.filter(
            created_at__date__gte=previous_month_start,
            created_at__date__lte=previous_month_end,
        ).count()

        current_month_cases = Case.objects.filter(
            created_at__date__gte=current_month_start,
            created_at__date__lte=today,
        ).count()

        previous_month_cases = Case.objects.filter(
            created_at__date__gte=previous_month_start,
            created_at__date__lte=previous_month_end,
        ).count()

        active_warrants = Warrant.objects.filter(
            status__in=[
                Warrant.Status.PENDING,
                Warrant.Status.APPROVED,
            ]
        ).count()

        station_commanders = (
            User.objects
            .filter(
                role="STATION_COMMANDER",
                is_active=True,
            )
            .select_related(
                "station",
                "district",
            )
            .order_by(
                "district__name",
                "station__name",
            )
        )

        district_stats = []

        districts = (
            District.objects
            .all()
            .order_by("name")
        )

        for district in districts:

            district_officers = User.objects.filter(
                district=district,
                role="OFFICER",
                is_active=True,
            ).count()

            district_commanders = User.objects.filter(
                district=district,
                role="STATION_COMMANDER",
                is_active=True,
            ).count()

            district_stations = PoliceStation.objects.filter(
                district=district
            ).count()

            district_cases = Case.objects.filter(
                station__district=district
            ).count()

            district_arrests = ArrestRecord.objects.filter(
                station__district=district
            ).count()

            district_suspects = Suspect.objects.filter(
                district=district
            ).count()

            district_warrants = Warrant.objects.filter(
                case__station__district=district
            ).count()

            district_offences = (
                Case.objects
                .filter(
                    station__district=district
                )
                .values(
                    "offence_id"
                )
                .distinct()
                .count()
            )

            district_solved = Case.objects.filter(
                station__district=district,
                status=Case.Status.CLOSED,
            ).count()

            district_stats.append(
                {
                    "name": district.name,
                    "officers": district_officers,
                    "commanders": district_commanders,
                    "stations": district_stations,
                    "cases": district_cases,
                    "arrests": district_arrests,
                    "suspects": district_suspects,
                    "warrants": district_warrants,
                    "offences": district_offences,
                    "solved": district_solved,
                }
            )

        common_offence_objects = (
            CriminalOffence.objects
            .annotate(
                case_count=Count(
                    "cases",
                    distinct=True,
                )
            )
            .filter(
                case_count__gt=0
            )
            .order_by(
                "-case_count",
                "title",
            )[:10]
        )

        common_offences = []

        for offence in common_offence_objects:

            common_offences.append(
                {
                    "name": offence.title,
                    "code": offence.code,
                    "count": offence.case_count,
                }
            )

        crime_hotspots = []

        hotspot_data = (
            Case.objects
            .filter(
                location__isnull=False
            )
            .exclude(
                location=""
            )
            .values(
                "location",
                "station__district__name",
            )
            .annotate(
                crime_count=Count(
                    "id",
                    distinct=True,
                )
            )
            .order_by(
                "-crime_count",
                "location",
            )[:10]
        )

        for hotspot in hotspot_data:

            district_name = (
                hotspot["station__district__name"]
                or "Unknown District"
            )

            crime_hotspots.append(
                {
                    "location": hotspot["location"],
                    "district": district_name,
                    "crime_count": hotspot["crime_count"],
                }
            )

        crime_summary = []

        for offence in common_offence_objects:

            offence_cases = Case.objects.filter(
                offence_id=offence.id
            )

            offence_case_count = (
                offence_cases.count()
            )

            offence_arrests = (
                ArrestRecord.objects
                .filter(
                    offences=offence
                )
                .distinct()
                .count()
            )

            offence_suspects = (
                offence_cases
                .filter(
                    suspect__isnull=False
                )
                .values(
                    "suspect_id"
                )
                .distinct()
                .count()
            )

            offence_warrants = (
                Warrant.objects
                .filter(
                    case__offence=offence
                )
                .distinct()
                .count()
            )

            crime_summary.append(
                {
                    "offence": offence.title,
                    "code": offence.code,
                    "cases": offence_case_count,
                    "arrests": offence_arrests,
                    "suspects": offence_suspects,
                    "warrants": offence_warrants,
                }
            )

        recent_arrests = (
            ArrestRecord.objects
            .select_related(
                "suspect",
                "case",
                "arresting_officer",
                "station",
            )
            .prefetch_related(
                "offences"
            )
            .order_by(
                "-created_at"
            )[:10]
        )

        recent_complaints = (
            Complaint.objects
            .select_related(
                "reported_by",
                "station",
            )
            .order_by(
                "-created_at"
            )[:5]
        )

        recent_cases = (
            Case.objects
            .select_related(
                "investigating_officer",
                "station",
                "offence",
                "suspect",
            )
            .order_by(
                "-created_at"
            )[:5]
        )

        crime_summary_total_cases = sum(
            item["cases"]
            for item in crime_summary
        )

        crime_summary_total_arrests = sum(
            item["arrests"]
            for item in crime_summary
        )

        crime_summary_total_suspects = sum(
            item["suspects"]
            for item in crime_summary
        )

        crime_summary_total_warrants = sum(
            item["warrants"]
            for item in crime_summary
        )

        dashboard_data.update(
            {
                "total_complaints":
                    total_complaints,

                "total_officers":
                    total_officers,

                "total_commanders":
                    total_commanders,

                "total_stations":
                    total_stations,

                "total_cases":
                    total_cases,

                "total_arrests":
                    total_arrests,

                "total_suspects":
                    total_suspects,

                "total_offences":
                    total_offences,

                "active_investigations":
                    active_investigations,

                "cases_for_review":
                    cases_for_review,

                "solved_cases":
                    solved_cases,

                "current_month_arrests":
                    current_month_arrests,

                "previous_month_arrests":
                    previous_month_arrests,

                "current_month_suspects":
                    current_month_suspects,

                "previous_month_suspects":
                    previous_month_suspects,

                "current_month_cases":
                    current_month_cases,

                "previous_month_cases":
                    previous_month_cases,

                "active_warrants":
                    active_warrants,

                "district_stats":
                    district_stats,

                "common_offences":
                    common_offences,

                "crime_hotspots":
                    crime_hotspots,

                "crime_summary":
                    crime_summary,

                "crime_summary_total_cases":
                    crime_summary_total_cases,

                "crime_summary_total_arrests":
                    crime_summary_total_arrests,

                "crime_summary_total_suspects":
                    crime_summary_total_suspects,

                "crime_summary_total_warrants":
                    crime_summary_total_warrants,

                "station_commanders":
                    station_commanders,

                "recent_arrests":
                    recent_arrests,

                "recent_complaints":
                    recent_complaints,

                "recent_cases":
                    recent_cases,
            }
        )

        return render(
            request,
            "dashboards/admin_dashboard.html",
            dashboard_data,
        )

    # ========================================================
    # UNKNOWN / UNSUPPORTED ROLE
    # ========================================================

    messages.error(
        request,
        (
            "Your BlueShield account has an unsupported role. "
            "Please contact the system administrator."
        ),
    )

    logout(request)

    return redirect(
        "accounts:sevispass_verify"
    )


# ============================================================
# REPORT DATE FILTER HELPER
# ============================================================

def apply_report_date_filter(
    queryset,
    date_field,
    start_date,
    end_date,
):

    if start_date:

        queryset = queryset.filter(
            **{
                f"{date_field}__date__gte": start_date
            }
        )

    if end_date:

        queryset = queryset.filter(
            **{
                f"{date_field}__date__lte": end_date
            }
        )

    return queryset


# ============================================================
# ARREST REPORT
# ============================================================

@login_required
def arrest_report(request):

    if request.user.role != "ADMIN":

        return render(
            request,
            "403.html",
            {
                "message": (
                    "You do not have permission to access "
                    "the Arrest Report."
                )
            },
            status=403,
        )

    start_date = parse_date(
        request.GET.get("start_date", "")
    )

    end_date = parse_date(
        request.GET.get("end_date", "")
    )

    district_id = request.GET.get(
        "district"
    )

    arrests = (
        ArrestRecord.objects
        .select_related(
            "suspect",
            "case",
            "case__offence",
            "arresting_officer",
            "station",
            "station__district",
        )
        .order_by(
            "-arrest_datetime"
        )
    )

    arrests = apply_report_date_filter(
        arrests,
        "arrest_datetime",
        start_date,
        end_date,
    )

    if district_id:

        arrests = arrests.filter(
            station__district_id=district_id
        )

    total_arrests = arrests.count()

    district_statistics = (
        arrests
        .values(
            "station__district__name"
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "-total"
        )
    )

    station_statistics = (
        arrests
        .values(
            "station__name",
            "station__district__name",
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "-total"
        )
    )

    offence_statistics = (
        arrests
        .filter(
            case__offence__isnull=False
        )
        .values(
            "case__offence__code",
            "case__offence__title",
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "-total"
        )
    )

    districts = District.objects.order_by(
        "name"
    )

    context = {
        "arrests": arrests,
        "districts": districts,
        "total_arrests": total_arrests,
        "district_statistics":
            district_statistics,
        "station_statistics":
            station_statistics,
        "offence_statistics":
            offence_statistics,
        "start_date": (
            start_date.strftime("%Y-%m-%d")
            if start_date
            else ""
        ),
        "end_date": (
            end_date.strftime("%Y-%m-%d")
            if end_date
            else ""
        ),
        "selected_district":
            district_id,
    }

    return render(
        request,
        "reports/arrest_report.html",
        context,
    )


# ============================================================
# DISTRICT REPORT
# ============================================================

@login_required
def district_report(request):

    if request.user.role != "ADMIN":

        return render(
            request,
            "403.html",
            {
                "message": (
                    "You do not have permission to access "
                    "the District Report."
                )
            },
            status=403,
        )

    start_date = parse_date(
        request.GET.get("start_date", "")
    )

    end_date = parse_date(
        request.GET.get("end_date", "")
    )

    complaints = Complaint.objects.all()
    cases = Case.objects.all()
    suspects = Suspect.objects.all()
    arrests = ArrestRecord.objects.all()

    complaints = apply_report_date_filter(
        complaints,
        "created_at",
        start_date,
        end_date,
    )

    cases = apply_report_date_filter(
        cases,
        "created_at",
        start_date,
        end_date,
    )

    suspects = apply_report_date_filter(
        suspects,
        "created_at",
        start_date,
        end_date,
    )

    arrests = apply_report_date_filter(
        arrests,
        "arrest_datetime",
        start_date,
        end_date,
    )

    districts = District.objects.order_by(
        "name"
    )

    district_statistics = []

    for district in districts:

        district_cases = cases.filter(
            station__district=district
        )

        district_complaints = complaints.filter(
            station__district=district
        )

        district_arrests = arrests.filter(
            station__district=district
        )

        district_suspects = suspects.filter(
            district=district
        )

        active_cases = district_cases.exclude(
            status=Case.Status.CLOSED
        ).count()

        closed_cases = district_cases.filter(
            status=Case.Status.CLOSED
        ).count()

        district_statistics.append(
            {
                "district": district,

                "stations":
                    district.stations.count(),

                "active_stations": (
                    district.stations
                    .filter(
                        is_active=True
                    )
                    .count()
                ),

                "complaints": (
                    district_complaints.count()
                ),

                "cases":
                    district_cases.count(),

                "active_cases":
                    active_cases,

                "closed_cases":
                    closed_cases,

                "suspects":
                    district_suspects.count(),

                "arrests":
                    district_arrests.count(),
            }
        )

    context = {
        "district_statistics":
            district_statistics,

        "start_date": (
            start_date.strftime("%Y-%m-%d")
            if start_date
            else ""
        ),

        "end_date": (
            end_date.strftime("%Y-%m-%d")
            if end_date
            else ""
        ),

        "total_districts":
            len(district_statistics),

        "total_complaints":
            complaints.count(),

        "total_cases":
            cases.count(),

        "total_suspects":
            suspects.count(),

        "total_arrests":
            arrests.count(),
    }

    return render(
        request,
        "reports/district_report.html",
        context,
    )


# ============================================================
# OVERALL CRIME SUMMARY
# ============================================================

@login_required
def overall_crime_summary(request):

    if request.user.role != "ADMIN":

        return render(
            request,
            "403.html",
            {
                "message": (
                    "You do not have permission to access "
                    "the Overall Crime Summary."
                )
            },
            status=403,
        )

    start_date = parse_date(
        request.GET.get("start_date", "")
    )

    end_date = parse_date(
        request.GET.get("end_date", "")
    )

    complaints = Complaint.objects.all()

    cases = (
        Case.objects
        .select_related(
            "station",
            "station__district",
            "suspect",
            "offence",
        )
    )

    suspects = Suspect.objects.all()

    arrests = (
        ArrestRecord.objects
        .select_related(
            "station",
            "station__district",
            "suspect",
            "case",
            "case__offence",
        )
    )

    complaints = apply_report_date_filter(
        complaints,
        "created_at",
        start_date,
        end_date,
    )

    cases = apply_report_date_filter(
        cases,
        "created_at",
        start_date,
        end_date,
    )

    suspects = apply_report_date_filter(
        suspects,
        "created_at",
        start_date,
        end_date,
    )

    arrests = apply_report_date_filter(
        arrests,
        "arrest_datetime",
        start_date,
        end_date,
    )

    total_complaints = complaints.count()
    total_cases = cases.count()
    total_suspects = suspects.count()
    total_arrests = arrests.count()

    active_cases = cases.exclude(
        status=Case.Status.CLOSED
    ).count()

    closed_cases = cases.filter(
        status=Case.Status.CLOSED
    ).count()

    status_labels = dict(
        Case.Status.choices
    )

    case_status_statistics = []

    status_data = (
        cases
        .values("status")
        .annotate(
            total=Count("id")
        )
        .order_by(
            "-total"
        )
    )

    for item in status_data:

        case_status_statistics.append(
            {
                "status":
                    item["status"],

                "label":
                    status_labels.get(
                        item["status"],
                        item["status"],
                    ),

                "total":
                    item["total"],
            }
        )

    offence_statistics = (
        cases
        .filter(
            offence__isnull=False
        )
        .values(
            "offence__code",
            "offence__title",
            "offence__category",
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "-total"
        )
    )

    district_statistics = (
        cases
        .filter(
            station__district__isnull=False
        )
        .values(
            "station__district__name"
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "-total"
        )
    )

    monthly_cases = (
        cases
        .annotate(
            month=TruncMonth(
                "created_at"
            )
        )
        .values(
            "month"
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "month"
        )
    )

    monthly_case_statistics = []

    for item in monthly_cases:

        if item["month"]:

            monthly_case_statistics.append(
                {
                    "month":
                        item["month"].strftime(
                            "%b %Y"
                        ),

                    "total":
                        item["total"],
                }
            )

    monthly_arrests = (
        arrests
        .annotate(
            month=TruncMonth(
                "arrest_datetime"
            )
        )
        .values(
            "month"
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "month"
        )
    )

    monthly_arrest_statistics = []

    for item in monthly_arrests:

        if item["month"]:

            monthly_arrest_statistics.append(
                {
                    "month":
                        item["month"].strftime(
                            "%b %Y"
                        ),

                    "total":
                        item["total"],
                }
            )

    monthly_complaints = (
        complaints
        .annotate(
            month=TruncMonth(
                "created_at"
            )
        )
        .values(
            "month"
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "month"
        )
    )

    monthly_complaint_statistics = []

    for item in monthly_complaints:

        if item["month"]:

            monthly_complaint_statistics.append(
                {
                    "month":
                        item["month"].strftime(
                            "%b %Y"
                        ),

                    "total":
                        item["total"],
                }
            )

    context = {
        "total_complaints":
            total_complaints,

        "total_cases":
            total_cases,

        "total_suspects":
            total_suspects,

        "total_arrests":
            total_arrests,

        "active_cases":
            active_cases,

        "closed_cases":
            closed_cases,

        "case_status_statistics":
            case_status_statistics,

        "offence_statistics":
            offence_statistics,

        "district_statistics":
            district_statistics,

        "monthly_case_statistics":
            monthly_case_statistics,

        "monthly_arrest_statistics":
            monthly_arrest_statistics,

        "monthly_complaint_statistics":
            monthly_complaint_statistics,

        "start_date": (
            start_date.strftime("%Y-%m-%d")
            if start_date
            else ""
        ),

        "end_date": (
            end_date.strftime("%Y-%m-%d")
            if end_date
            else ""
        ),
    }

    return render(
        request,
        "reports/crime_summary.html",
        context,
    )