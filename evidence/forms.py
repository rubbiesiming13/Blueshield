from django import forms

from .models import Evidence


class EvidenceForm(forms.ModelForm):

    class Meta:
        model = Evidence

        fields = [
            "evidence_number",
            "case",
            "arrest",
            "evidence_type",
            "description",
            "location_found",
            "collected_by",
            "date_collected",
            "storage_location",
            "status",
            "notes",
        ]

        widgets = {
            "evidence_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "EVD-2026-0001",
                }
            ),

            "case": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "arrest": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "evidence_type": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe the evidence..."
                }
            ),

            "location_found": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Where was the evidence found?"
                }
            ),

            "collected_by": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "date_collected": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local"
                }
            ),

            "storage_location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Evidence storage location"
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4
                }
            ),
        }