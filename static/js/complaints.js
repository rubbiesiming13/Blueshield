
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("complaint-form");

    if (!form) {
        return;
    }

    /* =====================================================
       SUBMIT BUTTON
    ===================================================== */

    const submitButton = document.getElementById("submit-button");

    const buttonText = submitButton
        ? submitButton.querySelector(".button-text")
        : null;

    const buttonLoading = submitButton
        ? submitButton.querySelector(".button-loading")
        : null;

    /* =====================================================
       FORM SUBMISSION
    ===================================================== */

    form.addEventListener("submit", function (event) {
        if (!form.checkValidity()) {
            event.preventDefault();
            form.reportValidity();
            return;
        }

        /* Show loading state */

        if (buttonText) {
            buttonText.hidden = true;
        }

        if (buttonLoading) {
            buttonLoading.hidden = false;
        }

        if (submitButton) {
            submitButton.disabled = true;
        }
    });

    /* =====================================================
       CANCEL BUTTON
    ===================================================== */

    const cancelButton = document.getElementById("cancel-button");

    if (cancelButton) {
        cancelButton.addEventListener("click", function () {
            const confirmed = window.confirm(
                "Are you sure you want to cancel? Any information entered will be lost."
            );

            if (confirmed) {
                window.history.back();
            }
        });
    }

    /* =====================================================
       CLOSE ALERT
    ===================================================== */

    document.querySelectorAll(".alert-close").forEach(function (button) {
        button.addEventListener("click", function () {
            const alert = button.closest(".alert");

            if (alert) {
                alert.style.opacity = "0";
                alert.style.transition = "opacity 0.2s ease";

                setTimeout(function () {
                    alert.remove();
                }, 200);
            }
        });
    });

    /* =====================================================
       CLEAR VALIDATION MESSAGE
    ===================================================== */

    form.querySelectorAll("input, select, textarea").forEach(function (field) {
        field.addEventListener("input", function () {
            field.setCustomValidity("");
        });
    });
});
