
from django import forms

from .models import CustodyRecord


class CustodyRecordForm(forms.ModelForm):

    class Meta:
        model = CustodyRecord

        fields = [
            "arrest",
            "status",
            "cell_number",
            "detention_start",
            "detention_end",
            "bail_amount_pgk",
            "bail_receipt_number",
            "transfer_destination",
            "release_reason",
            "notes",
        ]

        widgets = {
            "arrest": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "cell_number": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "detention_start": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local"
                }
            ),

            "detention_end": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local"
                }
            ),

            "bail_amount_pgk": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01"
                }
            ),

            "bail_receipt_number": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "transfer_destination": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "release_reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4
                }
            ),
        }

