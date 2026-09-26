from django import forms
from django.forms import inlineformset_factory

from .models import Complaint, ComplaintWitness


# ============================================================
# COMPLAINT FORM
# ============================================================

class ComplaintForm(forms.ModelForm):

    witness_count = forms.IntegerField(
        min_value=0,
        max_value=20,
        initial=0,
        required=True,
        label="Number of Additional Witnesses",
        help_text="Enter the number of additional witnesses for this complaint.",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": "0",
                "max": "20",
                "placeholder": "0",
            }
        ),
    )

    class Meta:
        model = Complaint

        fields = [
            "complainant_name",
            "complainant_phone",
            "complainant_address",
            "complainant_role",
            "complaint_type",
            "incident_date",
            "incident_location",
            "description",
            "complainant_statement",
        ]

        widgets = {

            "complainant_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter full name",
                }
            ),

            "complainant_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter phone number",
                }
            ),

            "complainant_address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter residential or contact address",
                }
            ),

            "complainant_role": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "complaint_type": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: Theft, Assault, Missing Person",
                }
            ),

            "incident_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "incident_location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Where did the incident occur?",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Provide a clear description of what happened."
                    ),
                }
            ),

            "complainant_statement": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Record what the reporting person personally "
                        "saw, heard, experienced, or knows about the incident."
                    ),
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        complainant_role = cleaned_data.get("complainant_role")
        complainant_statement = cleaned_data.get(
            "complainant_statement"
        )

        # A statement is required for every reporting person.
        if not complainant_statement:

            self.add_error(
                "complainant_statement",
                "Please record the statement of the reporting person.",
            )

        return cleaned_data


# ============================================================
# WITNESS FORM
# ============================================================

class ComplaintWitnessForm(forms.ModelForm):

    class Meta:
        model = ComplaintWitness

        fields = [
            "full_name",
            "phone",
            "address",
            "statement",
        ]

        widgets = {

            "full_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Witness full name",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Witness phone number",
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Witness residential or contact address",
                }
            ),

            "statement": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Record exactly what the witness personally "
                        "saw or heard."
                    ),
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        full_name = cleaned_data.get("full_name")
        phone = cleaned_data.get("phone")
        address = cleaned_data.get("address")
        statement = cleaned_data.get("statement")

        # ----------------------------------------------------
        # Allow a completely empty form.
        #
        # This is important when editing because the formset
        # can contain an empty extra witness form.
        # ----------------------------------------------------

        if not full_name and not phone and not address and not statement:
            return cleaned_data

        # ----------------------------------------------------
        # If the witness form has information, name and
        # statement are required.
        # ----------------------------------------------------

        if not full_name:

            self.add_error(
                "full_name",
                "Witness full name is required.",
            )

        if not statement:

            self.add_error(
                "statement",
                "Witness statement is required.",
            )

        return cleaned_data


# ============================================================
# WITNESS FORMSET
# ============================================================

ComplaintWitnessFormSet = inlineformset_factory(
    Complaint,
    ComplaintWitness,
    form=ComplaintWitnessForm,
    extra=1,
    can_delete=True,
    max_num=20,
)