from django import forms

from .models import Suspect
from stations.models import Province
from cases.models import Case


class SuspectForm(forms.ModelForm):

    class Meta:

        model = Suspect

        fields = [
            "id_type",
            "national_id_or_voter_no",

            "first_name",
            "middle_name",
            "last_name",
            "alias",
            "gender",
            "date_of_birth",
            "nationality",
            "occupation",

            "phone_number",
            "residential_address",
            "village",
            "province",

            "mugshot",
            "identifying_marks",

            "case",
            "suspect_role",
            "notes",
        ]

        widgets = {

            "id_type": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "national_id_or_voter_no": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter identification number",
                    "autocomplete": "off"
                }
            ),

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter first name",
                    "autocomplete": "given-name"
                }
            ),

            "middle_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter middle name",
                    "autocomplete": "additional-name"
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter last name",
                    "autocomplete": "family-name"
                }
            ),

            "alias": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Known nickname or alias"
                }
            ),

            "gender": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "date_of_birth": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "nationality": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter nationality",
                    "value": "Papua New Guinean"
                }
            ),

            "occupation": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter occupation"
                }
            ),

            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter phone number"
                }
            ),

            "residential_address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter current residential address"
                }
            ),

            "village": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter village"
                }
            ),

            "province": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "mugshot": forms.ClearableFileInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "identifying_marks": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": (
                        "Scars, tattoos, birthmarks or "
                        "other identifying features"
                    )
                }
            ),

            "case": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_case"
                }
            ),

            "suspect_role": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter any additional information"
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        # ============================================================
        # HOME PROVINCE
        # ============================================================

        self.fields["province"].queryset = (
            Province.objects
            .filter(is_active=True)
            .order_by("name")
        )

        self.fields["province"].required = True

        self.fields["province"].empty_label = "Select Home Province"

        # ============================================================
        # CASES
        # ============================================================

        case_queryset = (
            Case.objects
            .select_related(
                "offence",
                "investigating_officer",
                "station",
            )
            .order_by("-created_at")
        )

        # Officers should only see cases belonging to
        # their own police station.
        if user and getattr(user, "station", None):
            case_queryset = case_queryset.filter(
                station=user.station
            )

        self.fields["case"].queryset = case_queryset

        self.fields["case"].empty_label = "Select Case"

        # ============================================================
        # DEFAULT VALUES
        # ============================================================

        if not self.instance.pk:

            self.fields["nationality"].initial = (
                "Papua New Guinean"
            )

            self.fields["suspect_role"].initial = "MAIN"

        # ============================================================
        # CASE DATA FOR AUTO-FILL
        # ============================================================

        self.case_details = {}

        for case in case_queryset:

            investigating_officer = (
                case.investigating_officer.get_full_name()
                or case.investigating_officer.username
            )

            offence_name = str(case.offence)

            station_name = str(case.station)

            incident_date = ""

            if case.incident_date:
                incident_date = case.incident_date.strftime(
                    "%d %B %Y %H:%M"
                )

            self.case_details[str(case.pk)] = {
                "case_number": case.case_number,
                "title": case.title,
                "offence": offence_name,
                "status": case.get_status_display(),
                "priority": case.get_priority_display(),
                "incident_date": incident_date,
                "location": case.location,
                "investigating_officer": investigating_officer,
                "station": station_name,
            }

        # ============================================================
        # REQUIRED FIELDS
        # ============================================================

        self.fields["province"].required = True