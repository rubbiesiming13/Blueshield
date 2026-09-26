from django import forms

from .models import ArrestRecord


class ArrestRecordForm(forms.ModelForm):

    class Meta:
        model = ArrestRecord

        fields = [
            "occurrence_book_no",
            "suspect",
            "case",
            "arrest_datetime",
            "arrest_location",
            "reason_for_arrest",
            "offences",
            "property_seized",
            "physical_condition_at_intake",
            "custody_status",
            "cell_number",
            "bail_amount_pgk",
            "bail_receipt_no",
        ]

        widgets = {
            "occurrence_book_no": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter OB number",
                }
            ),

            "suspect": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "case": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "arrest_datetime": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),

            "arrest_location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Kalibobo, Modilon Road, Meiro Market",
                }
            ),

            "reason_for_arrest": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "State the reason for the arrest...",
                }
            ),

            "offences": forms.SelectMultiple(
                attrs={
                    "class": "form-select",
                    "size": "6",
                }
            ),

            "property_seized": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "List any property or items seized...",
                }
            ),

            "physical_condition_at_intake": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Record visible injuries or medical observations...",
                }
            ),

            "custody_status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "cell_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Cell 04",
                }
            ),

            "bail_amount_pgk": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0.00",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "bail_receipt_no": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter bail receipt number",
                }
            ),
        }

        labels = {
            "occurrence_book_no": "Occurrence Book Number",
            "suspect": "Suspect",
            "case": "Case",
            "arrest_datetime": "Arrest Date & Time",
            "arrest_location": "Arrest Location",
            "reason_for_arrest": "Reason for Arrest",
            "offences": "Offence(s)",
            "property_seized": "Property / Evidence Seized",
            "physical_condition_at_intake": "Physical Condition at Intake",
            "custody_status": "Custody Status",
            "cell_number": "Cell Number",
            "bail_amount_pgk": "Bail Amount (PGK)",
            "bail_receipt_no": "Bail Receipt Number",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add a blank option to the Case field
        self.fields["case"].required = False

        self.fields["case"].empty_label = "Select Case (Optional)"

        self.fields["suspect"].empty_label = "Select Suspect"

        # Improve offence field
        self.fields["offences"].required = True

        # Help text
        self.fields["offences"].help_text = (
            "Hold Ctrl and select all applicable offences."
        )

        self.fields["bail_amount_pgk"].required = False
        self.fields["bail_receipt_no"].required = False
        self.fields["cell_number"].required = False
        self.fields["property_seized"].required = False
        self.fields["physical_condition_at_intake"].required = False