from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.utils import timezone

from .forms import CaseRegistrationForm
from .models import Case


# ============================================================
# GENERATE CASE NUMBER
# ============================================================

def generate_case_number():

    year = timezone.now().year

    last_case = (
        Case.objects
        .filter(
            case_number__startswith=f"CASE-{year}-"
        )
        .order_by("-id")
        .first()
    )

    if last_case:

        try:
            last_number = int(
                last_case.case_number.rsplit("-", 1)[1]
            )

            next_number = last_number + 1

        except (ValueError, IndexError):

            next_number = 1

    else:

        next_number = 1

    return f"CASE-{year}-{next_number:04d}"


# ============================================================
# REGISTER CASE
# ============================================================

@login_required(login_url="accounts:login")
def register_case(request):

    # --------------------------------------------------------
    # ONLY POLICE OFFICERS CAN REGISTER CASES
    # --------------------------------------------------------

    if request.user.role != "OFFICER":

        messages.error(
            request,
            "You do not have permission to register cases."
        )

        return redirect("accounts:dashboard")

    # --------------------------------------------------------
    # OFFICER MUST HAVE A STATION
    # --------------------------------------------------------

    if not request.user.station:

        messages.error(
            request,
            "Your account is not assigned to a police station. "
            "Please contact the system administrator."
        )

        return redirect("accounts:dashboard")

    # --------------------------------------------------------
    # POST - REGISTER CASE
    # --------------------------------------------------------

    if request.method == "POST":

        form = CaseRegistrationForm(
            request.POST,
            user=request.user
        )

        if form.is_valid():

            case = form.save(commit=False)

            # ------------------------------------------------
            # AUTOMATIC BLUE SHIELD INFORMATION
            # ------------------------------------------------

            # Generate unique case number
            case.case_number = generate_case_number()

            # The logged-in officer becomes the
            # investigating officer.
            case.investigating_officer = request.user

            # The case automatically belongs to the
            # officer's assigned station.
            case.station = request.user.station

            # New cases start as OPEN.
            case.status = Case.Status.OPEN

            # Save the case
            case.save()

            # ------------------------------------------------
            # SUCCESS MESSAGE
            # ------------------------------------------------

            messages.success(
                request,
                f"Case {case.case_number} "
                "has been registered successfully."
            )

            return redirect("cases:list")

    # --------------------------------------------------------
    # GET - DISPLAY EMPTY FORM
    # --------------------------------------------------------

    else:

        form = CaseRegistrationForm(
            user=request.user
        )

    # --------------------------------------------------------
    # DISPLAY REGISTER CASE PAGE
    # --------------------------------------------------------

    return render(
        request,
        "cases/register_case.html",
        {
            "form": form,
            "officer": request.user,
            "station": request.user.station,
            "district": request.user.district,
        }
    )


# ============================================================
# CASE LIST / MY CASES
# ============================================================

@login_required(login_url="accounts:login")
def case_list(request):

    user = request.user

    # --------------------------------------------------------
    # START WITH NO CASES
    # --------------------------------------------------------
    # This is safer than starting with Case.objects.all().
    # Access is then granted according to the user's role.
    # --------------------------------------------------------

    cases = Case.objects.none()

    # ========================================================
    # POLICE OFFICER
    # ========================================================
    # An officer sees ONLY their own cases.
    #
    # Example:
    #
    # John -> John's cases
    # Timothy -> Timothy's cases
    #
    # ========================================================

    if user.role == "OFFICER":

        if user.station and user.district:

            cases = Case.objects.filter(
                investigating_officer=user,
                station=user.station,
                station__district=user.district,
            )

    # ========================================================
    # DIVISION ADMIN / PROSECUTION
    # ========================================================
    # Can see cases belonging to officers in the same:
    #
    # - Division
    # - District
    # - Station
    #
    # ========================================================

    elif user.role == "DIVISION_ADMIN":

        if user.division and user.station and user.district:

            cases = Case.objects.filter(
                investigating_officer__division=user.division,
                station=user.station,
                station__district=user.district,
            )

    # ========================================================
    # STATION COMMANDER
    # ========================================================
    # Can supervise all cases belonging to their station.
    #
    # ========================================================

    elif user.role == "STATION_COMMANDER":

        if user.station and user.district:

            cases = Case.objects.filter(
                station=user.station,
                station__district=user.district,
            )

    # ========================================================
    # PPC / SYSTEM ADMIN
    # ========================================================
    # Province-wide access.
    #
    # ========================================================

    elif user.role == "ADMIN":

        cases = Case.objects.all()

    # ========================================================
    # COMMON QUERY OPTIMIZATION
    # ========================================================

    cases = (
        cases
        .select_related(
            "complaint",
            "station",
            "station__district",
            "suspect",
            "offence",
            "investigating_officer",
        )
        .order_by("-created_at")
    )

    # ========================================================
    # DISPLAY CASE LIST
    # ========================================================

    return render(
        request,
        "cases/case_list.html",
        {
            "cases": cases,
            "officer": user,
            "station": user.station,
            "district": user.district,
        }
    )


# ============================================================
# CASE DETAIL / ROLE-BASED ACCESS
# ============================================================

@login_required(login_url="accounts:login")
def case_detail(request, case_id):

    user = request.user

    # --------------------------------------------------------
    # BASE CASE QUERY
    # --------------------------------------------------------

    case_queryset = Case.objects.select_related(
        "complaint",
        "station",
        "station__district",
        "suspect",
        "offence",
        "investigating_officer",
    )

    # ========================================================
    # POLICE OFFICER
    # ========================================================
    # Officer can only open their own case.
    # ========================================================

    if user.role == "OFFICER":

        case = get_object_or_404(
            case_queryset,
            id=case_id,
            investigating_officer=user,
            station=user.station,
            station__district=user.district,
        )

    # ========================================================
    # DIVISION ADMIN / PROSECUTION
    # ========================================================
    # Can open cases belonging to officers in their
    # assigned division, district and station.
    # ========================================================

    elif user.role == "DIVISION_ADMIN":

        if not user.division or not user.station or not user.district:

            messages.error(
                request,
                "Your account is not fully assigned to a "
                "division, district and station."
            )

            return redirect("accounts:dashboard")

        case = get_object_or_404(
            case_queryset,
            id=case_id,
            investigating_officer__division=user.division,
            station=user.station,
            station__district=user.district,
        )

    # ========================================================
    # STATION COMMANDER
    # ========================================================
    # Can open any case belonging to their station.
    # ========================================================

    elif user.role == "STATION_COMMANDER":

        if not user.station or not user.district:

            messages.error(
                request,
                "Your account is not assigned to a "
                "district and police station."
            )

            return redirect("accounts:dashboard")

        case = get_object_or_404(
            case_queryset,
            id=case_id,
            station=user.station,
            station__district=user.district,
        )

    # ========================================================
    # PPC / SYSTEM ADMIN
    # ========================================================
    # Can view all cases across Madang Province.
    # ========================================================

    elif user.role == "ADMIN":

        case = get_object_or_404(
            case_queryset,
            id=case_id,
        )

    # ========================================================
    # UNKNOWN ROLE
    # ========================================================

    else:

        messages.error(
            request,
            "You do not have permission to view this case."
        )

        return redirect("accounts:dashboard")

    # ========================================================
    # DISPLAY CASE DETAIL
    # ========================================================

    return render(
        request,
        "cases/case_detail.html",
        {
            "case": case,
        }
    )