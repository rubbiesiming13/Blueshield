from django import forms

from .models import MonthlyReport


class MonthlyReportForm(forms.ModelForm):
    class Meta:
        model = MonthlyReport

        fields = [
            "year",
            "month",
            "summary",
            "operational_notes",
            "challenges",
            "recommendations",
        ]

        widgets = {
            "year": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 2020,
                    "max": 2100,
                }
            ),

            "month": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "summary": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Provide a summary of the station's "
                        "activities during this reporting month."
                    ),
                }
            ),

            "operational_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Describe important operational activities, "
                        "events and observations."
                    ),
                }
            ),

            "challenges": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Describe challenges faced by the station "
                        "during this reporting period."
                    ),
                }
            ),

            "recommendations": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Provide recommendations from the "
                        "Station Commander."
                    ),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["year"].label = "Reporting Year"
        self.fields["month"].label = "Reporting Month"

        self.fields["summary"].label = "Monthly Summary"
        self.fields["operational_notes"].label = "Operational Notes"
        self.fields["challenges"].label = "Challenges"
        self.fields["recommendations"].label = "Recommendations"

        self.fields["summary"].required = False
        self.fields["operational_notes"].required = False
        self.fields["challenges"].required = False
        self.fields["recommendations"].required = False