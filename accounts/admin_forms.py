from django import forms
from django.contrib.auth import get_user_model

from stations.models import District, PoliceStation
from .models import Division


User = get_user_model()


# ============================================================
# CREATE USER FORM
# ============================================================

class AdminUserCreateForm(forms.ModelForm):

    class Meta:

        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "badge_number",
            "rank",
            "role",
            "division",
            "district",
            "station",
            "is_active",
        ]

        widgets = {

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "First name",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Last name",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Registered email address",
                    "autocomplete": "email",
                }
            ),

            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 7XXXXXXXX",
                    "inputmode": "tel",
                }
            ),

            "badge_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Police badge number",
                }
            ),

            "rank": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Police rank",
                }
            ),

            "role": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "division": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "district": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "station": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # ----------------------------------------------------
        # Email is required for SevisPass OTP verification.
        # ----------------------------------------------------

        self.fields["email"].required = True

        # ----------------------------------------------------
        # Phone number is optional.
        # It is kept as a contact field but is NOT used
        # for SevisPass OTP verification.
        # ----------------------------------------------------

        self.fields["phone_number"].required = False

        # ----------------------------------------------------
        # Active divisions only
        # ----------------------------------------------------

        self.fields["division"].queryset = (
            Division.objects
            .filter(is_active=True)
            .order_by("name")
        )

        # ----------------------------------------------------
        # All districts
        # ----------------------------------------------------

        self.fields["district"].queryset = (
            District.objects
            .order_by("name")
        )

        # ----------------------------------------------------
        # All police stations
        # ----------------------------------------------------

        self.fields["station"].queryset = (
            PoliceStation.objects
            .select_related("district")
            .order_by(
                "district__name",
                "name",
            )
        )

        # ----------------------------------------------------
        # Optional location fields.
        # Role validation is handled in clean().
        # ----------------------------------------------------

        self.fields["division"].required = False
        self.fields["district"].required = False
        self.fields["station"].required = False

    def clean_email(self):

        email = self.cleaned_data.get("email")

        if not email:
            raise forms.ValidationError(
                "A registered email address is required for "
                "SevisPass OTP verification."
            )

        return email.strip().lower()

    def clean(self):

        cleaned_data = super().clean()

        role = cleaned_data.get("role")
        division = cleaned_data.get("division")
        district = cleaned_data.get("district")
        station = cleaned_data.get("station")

        # ----------------------------------------------------
        # Role assignment rules
        # ----------------------------------------------------

        if role == "OFFICER":

            if not district:
                self.add_error(
                    "district",
                    "Police Officer must be assigned to a district.",
                )

            if not station:
                self.add_error(
                    "station",
                    "Police Officer must be assigned to a police station.",
                )

        elif role == "STATION_COMMANDER":

            if not district:
                self.add_error(
                    "district",
                    "Station Commander must be assigned to a district.",
                )

            if not station:
                self.add_error(
                    "station",
                    "Station Commander must be assigned to a police station.",
                )

        elif role == "DIVISION_ADMIN":

            if not division:
                self.add_error(
                    "division",
                    "Division Admin must be assigned to a division.",
                )

            if not district:
                self.add_error(
                    "district",
                    "Division Admin must be assigned to a district.",
                )

            if not station:
                self.add_error(
                    "station",
                    "Division Admin must be assigned to a police station.",
                )

        elif role == "ADMIN":

            # PPC / System Admin does not require
            # district, station or division.
            pass

        # ----------------------------------------------------
        # Station must belong to selected district
        # ----------------------------------------------------

        if station and district:

            if station.district_id != district.id:

                self.add_error(
                    "station",
                    (
                        f"{station.name} does not belong to "
                        f"{district.name} District."
                    ),
                )

        return cleaned_data

    def save(self, commit=True):

        user = super().save(
            commit=False
        )

        # ----------------------------------------------------
        # New users are NOT SevisPass verified.
        # Verification happens only after successful OTP
        # verification.
        # ----------------------------------------------------

        user.sevispass_verified = False
        user.sevispass_verified_at = None

        if commit:
            user.save()

        return user


# ============================================================
# UPDATE USER FORM
# ============================================================

class AdminUserUpdateForm(forms.ModelForm):

    class Meta:

        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "badge_number",
            "rank",
            "role",
            "division",
            "district",
            "station",
            "is_active",
        ]

        widgets = {

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "First name",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Last name",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Registered email address",
                    "autocomplete": "email",
                }
            ),

            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 7XXXXXXXX",
                    "inputmode": "tel",
                }
            ),

            "badge_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Police badge number",
                }
            ),

            "rank": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Police rank",
                }
            ),

            "role": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "division": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "district": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "station": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # ----------------------------------------------------
        # Email is required for SevisPass OTP verification.
        # ----------------------------------------------------

        self.fields["email"].required = True

        # ----------------------------------------------------
        # Phone number is optional.
        # It is NOT used for SevisPass OTP verification.
        # ----------------------------------------------------

        self.fields["phone_number"].required = False

        # ----------------------------------------------------
        # Active divisions only
        # ----------------------------------------------------

        self.fields["division"].queryset = (
            Division.objects
            .filter(is_active=True)
            .order_by("name")
        )

        # ----------------------------------------------------
        # All districts
        # ----------------------------------------------------

        self.fields["district"].queryset = (
            District.objects
            .order_by("name")
        )

        # ----------------------------------------------------
        # All police stations
        # ----------------------------------------------------

        self.fields["station"].queryset = (
            PoliceStation.objects
            .select_related("district")
            .order_by(
                "district__name",
                "name",
            )
        )

        # ----------------------------------------------------
        # Optional location fields.
        # Role validation is handled in clean().
        # ----------------------------------------------------

        self.fields["division"].required = False
        self.fields["district"].required = False
        self.fields["station"].required = False

    def clean_email(self):

        email = self.cleaned_data.get("email")

        if not email:
            raise forms.ValidationError(
                "A registered email address is required for "
                "SevisPass OTP verification."
            )

        return email.strip().lower()

    def clean(self):

        cleaned_data = super().clean()

        role = cleaned_data.get("role")
        division = cleaned_data.get("division")
        district = cleaned_data.get("district")
        station = cleaned_data.get("station")

        # ----------------------------------------------------
        # Role assignment rules
        # ----------------------------------------------------

        if role == "OFFICER":

            if not district:
                self.add_error(
                    "district",
                    "Police Officer must be assigned to a district.",
                )

            if not station:
                self.add_error(
                    "station",
                    "Police Officer must be assigned to a police station.",
                )

        elif role == "STATION_COMMANDER":

            if not district:
                self.add_error(
                    "district",
                    "Station Commander must be assigned to a district.",
                )

            if not station:
                self.add_error(
                    "station",
                    "Station Commander must be assigned to a police station.",
                )

        elif role == "DIVISION_ADMIN":

            if not division:
                self.add_error(
                    "division",
                    "Division Admin must be assigned to a division.",
                )

            if not district:
                self.add_error(
                    "district",
                    "Division Admin must be assigned to a district.",
                )

            if not station:
                self.add_error(
                    "station",
                    "Division Admin must be assigned to a police station.",
                )

        elif role == "ADMIN":

            # PPC / System Admin does not require
            # district, station or division.
            pass

        # ----------------------------------------------------
        # Station must belong to selected district
        # ----------------------------------------------------

        if station and district:

            if station.district_id != district.id:

                self.add_error(
                    "station",
                    (
                        f"{station.name} does not belong to "
                        f"{district.name} District."
                    ),
                )

        return cleaned_data