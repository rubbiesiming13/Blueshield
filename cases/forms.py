from django import forms

from .models import Case
from complaints.models import Complaint
from suspects.models import Suspect


class CaseRegistrationForm(forms.ModelForm):

    class Meta:

        model = Case

        fields = [
            "complaint",
            "title",
            "description",
            "offence",
            "incident_date",
            "location",
            "suspect",
        ]

        widgets = {

            # ====================================================
            # COMPLAINT
            # ====================================================

            "complaint": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            # ====================================================
            # CASE TITLE
            # ====================================================

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter case title"
                }
            ),

            # ====================================================
            # CASE DESCRIPTION
            # ====================================================

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Provide a clear summary of the case..."
                    )
                }
            ),

            # ====================================================
            # OFFENCE
            # ====================================================

            "offence": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            # ====================================================
            # INCIDENT DATE
            # ====================================================

            "incident_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local"
                }
            ),

            # ====================================================
            # INCIDENT LOCATION
            # ====================================================

            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter incident location"
                }
            ),

            # ====================================================
            # SUSPECT
            # ====================================================

            "suspect": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),
        }

    # ============================================================
    # INITIALIZE FORM
    # ============================================================

    def __init__(self, *args, **kwargs):

        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        # ========================================================
        # SAFETY
        # ========================================================
        # If no user is supplied, show no complaints or suspects.
        # ========================================================

        if user is None:

            self.fields["complaint"].queryset = (
                Complaint.objects.none()
            )

            self.fields["suspect"].queryset = (
                Suspect.objects.none()
            )

            return

        # ========================================================
        # POLICE OFFICER
        # ========================================================
        #
        # Officers can only work with records that belong to them.
        #
        # This prevents:
        #
        # Officer John
        #      ↓
        # selecting Timothy's complaint
        #
        # or
        #
        # Officer John
        #      ↓
        # selecting Timothy's suspect
        #
        # ========================================================

        if user.role == "OFFICER":

            # ====================================================
            # OFFICER'S COMPLAINTS
            # ====================================================

            if user.station:

                self.fields["complaint"].queryset = (
                    Complaint.objects
                    .filter(
                        reported_by=user,
                        station=user.station,
                    )
                    .select_related(
                        "station",
                        "station__district",
                    )
                    .order_by("-created_at")
                )

            else:

                self.fields["complaint"].queryset = (
                    Complaint.objects.none()
                )

            # ====================================================
            # OFFICER'S SUSPECTS
            # ====================================================
            #
            # Only suspects:
            # - registered by the logged-in officer
            # - belong to the officer's station
            # - are not already attached to another case
            #
            # ====================================================

            if user.station:

                self.fields["suspect"].queryset = (
                    Suspect.objects
                    .filter(
                        registered_by=user,
                        station=user.station,
                        case__isnull=True,
                    )
                    .select_related(
                        "station",
                    )
                    .order_by(
                        "first_name",
                        "last_name",
                    )
                )

            else:

                self.fields["suspect"].queryset = (
                    Suspect.objects.none()
                )

        # ========================================================
        # OTHER ROLES
        # ========================================================
        #
        # Case registration is currently restricted to Police
        # Officers.
        #
        # Division Admin
        # Station Commander
        # PPC / System Admin
        #
        # do not register cases through this form.
        #
        # ========================================================

        else:

            self.fields["complaint"].queryset = (
                Complaint.objects.none()
            )

            self.fields["suspect"].queryset = (
                Suspect.objects.none()
            )

    # ============================================================
    # FORM VALIDATION
    # ============================================================

    def clean(self):

        cleaned_data = super().clean()

        complaint = cleaned_data.get("complaint")
        suspect = cleaned_data.get("suspect")

        # --------------------------------------------------------
        # The detailed ownership checks are handled by the
        # queryset above and by the register_case view.
        # --------------------------------------------------------

        return cleaned_data