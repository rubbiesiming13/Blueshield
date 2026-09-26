from django import forms

from .models import Prosecution


# ============================================================
# PROSECUTION REVIEW FORM
# ============================================================

class ProsecutionReviewForm(forms.ModelForm):

    class Meta:
        model = Prosecution

        fields = [
            "case_file_complete",
            "investigation_reviewed",
            "evidence_reviewed",
            "arrest_reviewed",
            "warrant_reviewed",
            "custody_reviewed",
            "review_comments",
        ]

        widgets = {

            "case_file_complete": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "investigation_reviewed": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "evidence_reviewed": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "arrest_reviewed": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "warrant_reviewed": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "custody_reviewed": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "review_comments": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Enter prosecution review comments..."
                    ),
                }
            ),
        }


# ============================================================
# RETURN CASE FORM
# ============================================================

class ReturnCaseForm(forms.ModelForm):

    class Meta:
        model = Prosecution

        fields = [
            "return_reason",
        ]

        widgets = {

            "return_reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Explain what information or correction "
                        "is required from the Police Officer..."
                    ),
                }
            ),
        }

    def clean_return_reason(self):

        reason = self.cleaned_data.get(
            "return_reason"
        )

        if not reason or not reason.strip():

            raise forms.ValidationError(
                "A return reason is required."
            )

        return reason.strip()


# ============================================================
# PROSECUTION PROCESS FORM
# ============================================================

class ProsecutionProcessForm(forms.ModelForm):

    class Meta:
        model = Prosecution

        fields = [
            "decision",

            "committal_status",
            "committal_date",
            "committal_notes",

            "summary_trial_status",
            "summary_trial_date",
            "summary_trial_notes",

            "forwarded_to_court",
            "forwarded_date",
        ]

        widgets = {

            "decision": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Enter the prosecution decision..."
                    ),
                }
            ),

            "committal_status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "committal_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "committal_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Enter committal proceedings notes..."
                    ),
                }
            ),

            "summary_trial_status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "summary_trial_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "summary_trial_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Enter summary trial notes..."
                    ),
                }
            ),

            "forwarded_to_court": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "forwarded_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
        }

    # ========================================================
    # VALIDATION
    # ========================================================

    def clean(self):

        cleaned_data = super().clean()

        decision = cleaned_data.get(
            "decision"
        )

        committal_status = cleaned_data.get(
            "committal_status"
        )

        committal_date = cleaned_data.get(
            "committal_date"
        )

        summary_trial_status = cleaned_data.get(
            "summary_trial_status"
        )

        summary_trial_date = cleaned_data.get(
            "summary_trial_date"
        )

        forwarded_to_court = cleaned_data.get(
            "forwarded_to_court"
        )

        forwarded_date = cleaned_data.get(
            "forwarded_date"
        )

        not_started = (
            Prosecution.ProceedingStatus.NOT_STARTED
        )

        in_progress = (
            Prosecution.ProceedingStatus.IN_PROGRESS
        )

        completed = (
            Prosecution.ProceedingStatus.COMPLETED
        )

        # ----------------------------------------------------
        # DECISION
        # ----------------------------------------------------

        if not decision or not decision.strip():

            self.add_error(
                "decision",
                "A prosecution decision is required.",
            )

        # ----------------------------------------------------
        # ONLY ONE PROCEEDING CAN BE ACTIVE
        # ----------------------------------------------------

        if (
            committal_status == in_progress
            and summary_trial_status == in_progress
        ):

            raise forms.ValidationError(
                "Committal and Summary Trial cannot both "
                "be in progress at the same time."
            )

        # ----------------------------------------------------
        # PREVENT BOTH FROM BEING COMPLETED
        # ----------------------------------------------------

        if (
            committal_status == completed
            and summary_trial_status == completed
        ):

            raise forms.ValidationError(
                "Committal and Summary Trial cannot both "
                "be completed as the active proceeding."
            )

        # ----------------------------------------------------
        # COMMITTAL DATE
        # ----------------------------------------------------

        if (
            committal_status in [in_progress, completed]
            and not committal_date
        ):

            self.add_error(
                "committal_date",
                (
                    "A committal date is required when "
                    "Committal proceedings are started "
                    "or completed."
                ),
            )

        if (
            committal_status == not_started
            and committal_date
        ):

            self.add_error(
                "committal_date",
                (
                    "Remove the committal date while "
                    "Committal is marked Not Started."
                ),
            )

        # ----------------------------------------------------
        # SUMMARY TRIAL DATE
        # ----------------------------------------------------

        if (
            summary_trial_status in [in_progress, completed]
            and not summary_trial_date
        ):

            self.add_error(
                "summary_trial_date",
                (
                    "A summary-trial date is required when "
                    "Summary Trial is started or completed."
                ),
            )

        if (
            summary_trial_status == not_started
            and summary_trial_date
        ):

            self.add_error(
                "summary_trial_date",
                (
                    "Remove the summary-trial date while "
                    "Summary Trial is marked Not Started."
                ),
            )

        # ----------------------------------------------------
        # COURT FORWARDING
        # ----------------------------------------------------

        if forwarded_to_court and not forwarded_date:

            self.add_error(
                "forwarded_date",
                (
                    "A forwarded date is required when "
                    "the case is marked as forwarded to court."
                ),
            )

        if not forwarded_to_court and forwarded_date:

            self.add_error(
                "forwarded_date",
                (
                    "Remove the forwarded date or mark "
                    "the case as forwarded to court."
                ),
            )

        return cleaned_data