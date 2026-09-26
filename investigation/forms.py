from django import forms

from cases.models import Case
from evidence.models import Evidence

from .models import InvestigationRecord, Statement


# ============================================================
# INVESTIGATION RECORD FORM
# ============================================================

class InvestigationRecordForm(forms.ModelForm):

    class Meta:
        model = InvestigationRecord

        fields = [
            "case",
            "investigation_date",
            "activity",
            "location",
            "findings",
            "action_taken",
            "investigation_notes",
        ]

        widgets = {
            "case": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "investigation_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "activity": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Brief description of investigation activity",
                }
            ),

            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter investigation location",
                }
            ),

            "findings": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Record investigation findings",
                }
            ),

            "action_taken": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Record action taken",
                }
            ),

            "investigation_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter additional investigation notes",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        # Case is required because InvestigationRecord.case
        # cannot be NULL in the database.
        self.fields["case"].required = True

        # Only show cases belonging to the logged-in officer.
        if user is not None:
            self.fields["case"].queryset = (
                Case.objects
                .filter(
                    investigating_officer=user
                )
                .select_related(
                    "offence",
                    "station",
                )
                .order_by("-created_at")
            )

        # Helpful label
        self.fields["case"].label = "Case"


# ============================================================
# STATEMENT FORM
# ============================================================

class StatementForm(forms.ModelForm):

    class Meta:
        model = Statement

        fields = [
            "case",
            "person",
            "statement_type",
            "statement_date",
            "statement_time",
            "location",
            "statement",
            "attachment",
        ]

        widgets = {
            "case": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "person": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Name of person giving statement",
                }
            ),

            "statement_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "statement_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "statement_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),

            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Where was the statement recorded?",
                }
            ),

            "statement": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Enter the full statement...",
                }
            ),

            "attachment": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        self.fields["case"].required = False

        if user is not None:
            self.fields["case"].queryset = (
                Case.objects
                .filter(
                    investigating_officer=user
                )
                .order_by("-created_at")
            )


# ============================================================
# EVIDENCE FORM
# ============================================================

class EvidenceForm(forms.ModelForm):

    class Meta:
        model = Evidence

        fields = [
            "case",
            "arrest",
            "evidence_type",
            "description",
            "location_found",
            "date_collected",
            "storage_location",
            "status",
            "notes",
        ]

        widgets = {
            "case": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "arrest": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "evidence_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe the evidence",
                }
            ),

            "location_found": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Where was the evidence found?",
                }
            ),

            "date_collected": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),

            "storage_location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Evidence storage location",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Additional evidence notes",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        self.fields["case"].required = False
        self.fields["arrest"].required = False

        if user is not None:
            self.fields["case"].queryset = (
                Case.objects
                .filter(
                    investigating_officer=user
                )
                .order_by("-created_at")
            )