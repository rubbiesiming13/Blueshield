from django import forms


# ============================================================
# SEVISPASS VERIFICATION FORM
# ============================================================

class SevisPassVerificationForm(forms.Form):

    sevispass_id = forms.CharField(
        max_length=100,
        label="SevisPass ID",
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Enter your SevisPass ID",
                "autocomplete": "off",
                "autofocus": True,
            }
        )
    )


# ============================================================
# SEVISPASS OTP FORM
# ============================================================

class SevisPassOTPForm(forms.Form):

    otp = forms.CharField(
        max_length=6,
        min_length=6,
        label="6-Digit OTP",
        widget=forms.TextInput(
            attrs={
                "class": "form-control otp-input",
                "placeholder": "Enter 6-digit OTP",
                "inputmode": "numeric",
                "autocomplete": "one-time-code",
                "maxlength": "6",
                "pattern": "[0-9]{6}",
                "autofocus": True,
            }
        )
    )

    def clean_otp(self):

        otp = self.cleaned_data["otp"].strip()

        if not otp.isdigit() or len(otp) != 6:

            raise forms.ValidationError(
                "Enter the 6-digit OTP."
            )

        return otp

# ============================================================
# BLUESHIELD LOGIN FORM
# ============================================================

class LoginForm(forms.Form):

    username = forms.CharField(
        max_length=150,
        label="BlueShield Username",
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Enter your BlueShield username",
                "autocomplete": "username",
                "autofocus": True,
            }
        )
    )

    password = forms.CharField(
        label="BlueShield Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Enter your BlueShield password",
                "autocomplete": "current-password",
            }
        )
    )

