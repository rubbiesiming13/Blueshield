# accounts/views.py

from datetime import timedelta

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

from .models import User

from .services import (
    verify_sevispass,
)
import firebase_admin

from firebase_admin import auth
from complaints.models import Complaint
from cases.models import Case
from suspects.models import Suspect
from records.models import ArrestRecord, CriminalOffence
from warrant.models import Warrant
from stations.models import District, PoliceStation
from prosecution.models import Prosecution
from audit_logs.models import AuditLog


# ============================================================
# SEVISPASS ID VERIFICATION
# ============================================================

def sevispass_verify_view(request):

    if request.user.is_authenticated:

        return redirect(
            "accounts:dashboard"
        )

    # --------------------------------------------------------
    # Clear old verification/pending session
    # --------------------------------------------------------

    request.session.pop(
        "sevispass_user_id",
        None
    )

    request.session.pop(
        "sevispass_verified",
        None
    )

    request.session.pop(
        "sevispass_verified_at",
        None
    )

    request.session.pop(
        "verified_sevispass_id",
        None
    )

    request.session.pop(
        "sevispass_pending_user_id",
        None
    )

    request.session.pop(
        "sevispass_pending_sevispass_id",
        None
    )

    request.session.pop(
        "sevispass_otp_expires_at",
        None
    )

    request.session.pop(
        "simulated_sevispass_otp",
        None
    )

    request.session.pop(
        "sevispass_masked_phone",
        None
    )

    # --------------------------------------------------------
    # PROCESS SEVISPASS ID
    # --------------------------------------------------------

    if request.method == "POST":

        form = SevisPassVerificationForm(
            request.POST
        )

        if form.is_valid():

            sevispass_id = (
                form.cleaned_data[
                    "sevispass_id"
                ].strip()
            )

            # ------------------------------------------------
            # FIND ACTIVE USER
            # ------------------------------------------------

            user = verify_sevispass(
                sevispass_id
            )

            if user:

                # ------------------------------------------------
                # REQUIRE REGISTERED MOBILE NUMBER
                # ------------------------------------------------

                if not user.phone_number:

                    messages.error(
                        request,
                        (
                            "No registered mobile phone number "
                            "is available for this account. "
                            "Please contact the system administrator."
                        )
                    )

                    return render(
                        request,
                        "accounts/sevispass_verify.html",
                        {
                            "form": form
                        }
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
                # MASK MOBILE NUMBER
                # ------------------------------------------------

                phone = str(
                    user.phone_number
                    or ""
                ).strip()

                if len(phone) >= 4:

                    masked_phone = (
                        "••••"
                        + phone[-4:]
                    )

                else:

                    masked_phone = (
                        "Registered mobile number"
                    )

                request.session[
                    "sevispass_masked_phone"
                ] = masked_phone

                # ------------------------------------------------
                # FIREBASE WILL SEND THE SMS
                # ------------------------------------------------
                #
                # The actual SMS is now sent by Firebase
                # from the OTP page.
                #
                # We no longer generate or store a Django OTP.
                # ------------------------------------------------

                messages.success(
                    request,
                    (
                        "SevisPass ID verified. "
                        "A verification code will be sent "
                        "to your registered mobile number."
                    )
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
                )
            )

    else:

        form = SevisPassVerificationForm()

    return render(
        request,
        "accounts/sevispass_verify.html",
        {
            "form": form
        }
    )
# ============================================================
# SEVISPASS OTP VERIFICATION USING FIREBASE
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
            )
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
                "division"
            )
            .get(
                id=pending_user_id,
                is_active=True
            )
        )

    except User.DoesNotExist:

        request.session.flush()

        messages.error(
            request,
            (
                "The BlueShield account could not be found. "
                "Please contact the system administrator."
            )
        )

        return redirect(
            "accounts:sevispass_verify"
        )

    # --------------------------------------------------------
    # GET REGISTERED PHONE NUMBER
    # --------------------------------------------------------

    phone = str(
        user.phone_number
        or ""
    ).strip()

    if not phone:

        request.session.flush()

        messages.error(
            request,
            (
                "No registered mobile phone number is "
                "available for this account."
            )
        )

        return redirect(
            "accounts:sevispass_verify"
        )

    # --------------------------------------------------------
    # MASK PHONE NUMBER
    # --------------------------------------------------------

    masked_phone = request.session.get(
        "sevispass_masked_phone",
        "Registered mobile number"
    )

    # --------------------------------------------------------
    # FIREBASE TOKEN VERIFICATION
    # --------------------------------------------------------

    if (
        request.method == "POST"
        and request.POST.get("action") == "verify_firebase"
    ):

        firebase_token = (
            request.POST.get(
                "firebase_token",
                ""
            ).strip()
        )

        if not firebase_token:

            return render(
                request,
                "accounts/sevispass_otp.html",
                {
                    "form": SevisPassOTPForm(),
                    "masked_phone": masked_phone,
                    "firebase_phone_number": phone,
                    "firebase_error": (
                        "Firebase verification token was not "
                        "received. Please try again."
                    ),
                }
            )

        # ----------------------------------------------------
        # VERIFY FIREBASE ID TOKEN
        # ----------------------------------------------------

        try:

            decoded_token = (
                auth.verify_id_token(
                    firebase_token
                )
            )

        except Exception:

            return render(
                request,
                "accounts/sevispass_otp.html",
                {
                    "form": SevisPassOTPForm(),
                    "masked_phone": masked_phone,
                    "firebase_phone_number": phone,
                    "firebase_error": (
                        "Firebase verification failed. "
                        "Please enter the correct SMS code "
                        "and try again."
                    ),
                }
            )

        # ----------------------------------------------------
        # GET VERIFIED FIREBASE PHONE NUMBER
        # ----------------------------------------------------

        firebase_phone = (
            decoded_token.get(
                "phone_number"
            )
        )

        if not firebase_phone:

            return render(
                request,
                "accounts/sevispass_otp.html",
                {
                    "form": SevisPassOTPForm(),
                    "masked_phone": masked_phone,
                    "firebase_phone_number": phone,
                    "firebase_error": (
                        "Firebase did not return a verified "
                        "phone number."
                    ),
                }
            )

        # ----------------------------------------------------
        # NORMALIZE PHONE NUMBERS
        # ----------------------------------------------------

        normalized_database_phone = (
            phone.replace(
                " ",
                ""
            )
            .replace(
                "-",
                ""
            )
            .replace(
                "(",
                ""
            )
            .replace(
                ")",
                ""
            )
        )

        normalized_firebase_phone = (
            str(firebase_phone)
            .replace(
                " ",
                ""
            )
            .replace(
                "-",
                ""
            )
            .replace(
                "(",
                ""
            )
            .replace(
                ")",
                ""
            )
        )

        # ----------------------------------------------------
        # CONFIRM PHONE BELONGS TO SEVISPASS USER
        # ----------------------------------------------------

        if (
            normalized_database_phone
            != normalized_firebase_phone
        ):

            messages.error(
                request,
                (
                    "The verified mobile number does not "
                    "match the mobile number registered "
                    "with this SevisPass account."
                )
            )

            request.session.flush()

            return redirect(
                "accounts:sevispass_verify"
            )

        # ----------------------------------------------------
        # FIREBASE + SEVISPASS VERIFICATION SUCCESSFUL
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # STORE FIREBASE USER ID FOR THIS SESSION
        # ----------------------------------------------------

        firebase_uid = (
            decoded_token.get(
                "uid"
            )
        )

        if firebase_uid:

            request.session[
                "firebase_uid"
            ] = firebase_uid

        # ----------------------------------------------------
        # REMOVE TEMPORARY DATA
        # ----------------------------------------------------

        request.session.pop(
            "sevispass_pending_user_id",
            None
        )

        request.session.pop(
            "sevispass_pending_sevispass_id",
            None
        )

        request.session.pop(
            "sevispass_otp_expires_at",
            None
        )

        request.session.pop(
            "simulated_sevispass_otp",
            None
        )

        request.session.pop(
            "sevispass_masked_phone",
            None
        )

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        messages.success(
            request,
            (
                "SevisPass identity successfully "
                "verified. Please continue with "
                "your BlueShield login."
            )
        )

        return redirect(
            "accounts:login"
        )

    # --------------------------------------------------------
    # NORMAL PAGE LOAD
    # --------------------------------------------------------

    form = SevisPassOTPForm()

    return render(
        request,
        "accounts/sevispass_otp.html",
        {
            "form": form,
            "masked_phone": masked_phone,
            "firebase_phone_number": phone,
        }
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

    try:

        sevispass_user = (
            User.objects
            .select_related(
                "district",
                "station",
                "division"
            )
            .get(
                id=sevispass_user_id,
                is_active=True
            )
        )

    except User.DoesNotExist:

        request.session.flush()

        messages.error(
            request,
            (
                "Your SevisPass verification session "
                "has expired. Please verify again."
            )
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
                    )
                )

                return render(
                    request,
                    "accounts/login.html",
                    {
                        "form": form,
                        "sevispass_user": sevispass_user,
                    }
                )

            # ------------------------------------------------
            # CHECK ACTIVE ACCOUNT
            # ------------------------------------------------

            if not user.is_active:

                messages.error(
                    request,
                    "Your BlueShield account is inactive."
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
                    )
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
                user
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
                    f"Station: "
                    f"{user.station.name if user.station else 'N/A'}. "
                    f"District: "
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
                )
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
        }
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
        "You have been securely logged out of BlueShield."
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
            "division"
        )
        .order_by(
            "username"
        )
    )

    return render(
        request,
        "dashboards/police_officers.html",
        {
            "officers": officers
        }
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
            "name"
        )
    )

    return render(
        request,
        "dashboards/police_stations.html",
        {
            "stations": stations,
        }
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
                status=Case.Status.UNDER_INVESTIGATION
            ).count()

            cases_for_review = Case.objects.filter(
                station=station,
                status=Case.Status.CASE_FILE_PREPARED
            ).count()

            closed_cases = Case.objects.filter(
                station=station,
                status=Case.Status.CLOSED
            ).count()

            monthly_arrests = ArrestRecord.objects.filter(
                station=station,
                arrest_datetime__date__gte=current_month_start,
                arrest_datetime__date__lte=today,
            ).count()

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

            total_complaints = 0
            total_cases = 0
            total_arrests = 0
            total_suspects = 0
            active_investigations = 0
            cases_for_review = 0
            closed_cases = 0
            monthly_arrests = 0
            recent_arrests = []

        dashboard_data.update({

            "total_complaints": total_complaints,
            "total_cases": total_cases,
            "total_arrests": total_arrests,
            "total_suspects": total_suspects,
            "active_investigations": active_investigations,
            "cases_for_review": cases_for_review,
            "closed_cases": closed_cases,
            "monthly_arrests": monthly_arrests,
            "recent_arrests": recent_arrests,

        })

        return render(
            request,
            "dashboards/officer_dashboard.html",
            dashboard_data
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
                is_active=True
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
                status=Case.Status.UNDER_INVESTIGATION
            ).count()

            cases_for_review = Case.objects.filter(
                station=station,
                status=Case.Status.CASE_FILE_PREPARED
            ).count()

            solved_cases = Case.objects.filter(
                station=station,
                status=Case.Status.CLOSED
            ).count()

            monthly_arrests = ArrestRecord.objects.filter(
                station=station,
                arrest_datetime__date__gte=current_month_start,
                arrest_datetime__date__lte=today,
            ).count()

            # -----------------------------------------------
            # OFFICER ACTIVITY
            # -----------------------------------------------

            officer_activity = (
                User.objects
                .filter(
                    station=station,
                    role="OFFICER",
                    is_active=True
                )
                .annotate(

                    complaint_count=Count(
                        "complaints_created",
                        distinct=True
                    ),

                    case_count=Count(
                        "investigated_cases",
                        distinct=True
                    ),

                    arrest_count=Count(
                        "arrests_made",
                        distinct=True
                    ),

                )
                .order_by(
                    "-case_count",
                    "-arrest_count"
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

        dashboard_data.update({

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

        })

        return render(
            request,
            "dashboards/station_commander_dashboard.html",
            dashboard_data
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
                is_active=True
            ).count()

        else:

            officers = 0

        if district:

            commanders = User.objects.filter(
                district=district,
                role="STATION_COMMANDER",
                is_active=True
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
                status=Case.Status.UNDER_INVESTIGATION
            ).count()

            cases_for_review = Case.objects.filter(
                station__district=district,
                status=Case.Status.CASE_FILE_PREPARED
            ).count()

            solved_cases = Case.objects.filter(
                station__district=district,
                status=Case.Status.CLOSED
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
                ]
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

        dashboard_data.update({

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

        })

        return render(
            request,
            "dashboards/division_admin_dashboard.html",
            dashboard_data
        )

    # ========================================================
    # PPC / SYSTEM ADMINISTRATOR DASHBOARD
    # ========================================================

    elif user.role == "ADMIN":

        # ====================================================
        # PROVINCIAL TOTALS
        # ====================================================

        total_complaints = Complaint.objects.count()

        total_officers = User.objects.filter(
            role="OFFICER",
            is_active=True
        ).count()

        total_commanders = User.objects.filter(
            role="STATION_COMMANDER",
            is_active=True
        ).count()

        total_stations = PoliceStation.objects.count()

        total_cases = Case.objects.count()

        total_arrests = ArrestRecord.objects.count()

        total_suspects = Suspect.objects.count()

        total_offences = CriminalOffence.objects.count()

        # ====================================================
        # CASE STATUS INTELLIGENCE
        # ====================================================

        active_investigations = Case.objects.filter(
            status=Case.Status.UNDER_INVESTIGATION
        ).count()

        cases_for_review = Case.objects.filter(
            status=Case.Status.CASE_FILE_PREPARED
        ).count()

        solved_cases = Case.objects.filter(
            status=Case.Status.CLOSED
        ).count()

        # ====================================================
        # MONTHLY ARRESTS
        # ====================================================

        current_month_arrests = ArrestRecord.objects.filter(
            arrest_datetime__date__gte=current_month_start,
            arrest_datetime__date__lte=today,
        ).count()

        previous_month_arrests = ArrestRecord.objects.filter(
            arrest_datetime__date__gte=previous_month_start,
            arrest_datetime__date__lte=previous_month_end,
        ).count()

        # ====================================================
        # MONTHLY SUSPECTS
        # ====================================================

        current_month_suspects = Suspect.objects.filter(
            created_at__date__gte=current_month_start,
            created_at__date__lte=today,
        ).count()

        previous_month_suspects = Suspect.objects.filter(
            created_at__date__gte=previous_month_start,
            created_at__date__lte=previous_month_end,
        ).count()

        # ====================================================
        # MONTHLY CASES
        # ====================================================

        current_month_cases = Case.objects.filter(
            created_at__date__gte=current_month_start,
            created_at__date__lte=today,
        ).count()

        previous_month_cases = Case.objects.filter(
            created_at__date__gte=previous_month_start,
            created_at__date__lte=previous_month_end,
        ).count()

        # ====================================================
        # ACTIVE WARRANTS
        # ====================================================

        active_warrants = Warrant.objects.filter(
            status__in=[
                Warrant.Status.PENDING,
                Warrant.Status.APPROVED,
            ]
        ).count()

        # ====================================================
        # STATION COMMANDERS
        # ====================================================

        station_commanders = (
            User.objects
            .filter(
                role="STATION_COMMANDER",
                is_active=True
            )
            .select_related(
                "station",
                "district"
            )
            .order_by(
                "district__name",
                "station__name"
            )
        )

        # ====================================================
        # DISTRICT SUMMARY
        # ====================================================

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
                is_active=True
            ).count()

            district_commanders = User.objects.filter(
                district=district,
                role="STATION_COMMANDER",
                is_active=True
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
                station__district=district
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
                status=Case.Status.CLOSED
            ).count()

            district_stats.append({

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

            })

        # ====================================================
        # MOST COMMON OFFENCES
        # ====================================================

        common_offence_objects = (
            CriminalOffence.objects
            .annotate(
                case_count=Count(
                    "cases",
                    distinct=True
                )
            )
            .filter(
                case_count__gt=0
            )
            .order_by(
                "-case_count",
                "title"
            )[:10]
        )

        common_offences = []

        for offence in common_offence_objects:

            common_offences.append({

                "name": offence.title,

                "code": offence.code,

                "count": offence.case_count,

            })

        # ====================================================
        # HIGHEST CRIME LOCATIONS / HOTSPOTS
        # ====================================================

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
                "station__district__name"
            )
            .annotate(
                crime_count=Count(
                    "id",
                    distinct=True
                )
            )
            .order_by(
                "-crime_count",
                "location"
            )[:10]
        )

        for hotspot in hotspot_data:

            district_name = (
                hotspot[
                    "station__district__name"
                ]
                or "Unknown District"
            )

            crime_hotspots.append({

                "location":
                    hotspot["location"],

                "district":
                    district_name,

                "crime_count":
                    hotspot["crime_count"],

            })

        # ====================================================
        # CRIME SUMMARY
        # ====================================================

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

            crime_summary.append({

                "offence":
                    offence.title,

                "code":
                    offence.code,

                "cases":
                    offence_case_count,

                "arrests":
                    offence_arrests,

                "suspects":
                    offence_suspects,

                "warrants":
                    offence_warrants,

            })

        # ====================================================
        # RECENT ARRESTS
        # ====================================================

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

        # ====================================================
        # RECENT SYSTEM ACTIVITY
        # ====================================================

        recent_complaints = (
            Complaint.objects
            .select_related(
                "reported_by",
                "station"
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
                "suspect"
            )
            .order_by(
                "-created_at"
            )[:5]
        )

        # ====================================================
        # CRIME SUMMARY TOTALS
        # ====================================================

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

        # ====================================================
        # DASHBOARD DATA
        # ====================================================

        dashboard_data.update({

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

        })

        return render(
            request,
            "dashboards/admin_dashboard.html",
            dashboard_data
        )

    # ========================================================
    # UNKNOWN / UNSUPPORTED ROLE
    # ========================================================

    messages.error(
        request,
        (
            "Your BlueShield account has an unsupported role. "
            "Please contact the system administrator."
        )
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

    # --------------------------------------------------------
    # Arrests by district
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Arrests by station
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Arrests by offence
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Base querysets
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Date filtering
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Main totals
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Case status statistics
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Offence statistics
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # District statistics
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Monthly cases
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Monthly arrests
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Monthly complaints
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Context
    # --------------------------------------------------------

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