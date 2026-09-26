document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("case-form");

    if (!form) {
        return;
    }


    /* ================================
       SUBMIT BUTTON
    ================================= */

    const submitButton =
        document.getElementById("submit-button");

    const buttonText =
        submitButton.querySelector(".button-text");

    const buttonLoading =
        submitButton.querySelector(".button-loading");


    form.addEventListener("submit", function (event) {

        if (!form.checkValidity()) {

            event.preventDefault();

            form.reportValidity();

            return;
        }


        if (buttonText) {
            buttonText.hidden = true;
        }


        if (buttonLoading) {
            buttonLoading.hidden = false;
        }


        submitButton.disabled = true;

    });


    /* ================================
       CLOSE SUCCESS MESSAGE
    ================================= */

    document
        .querySelectorAll(".alert-close")
        .forEach(function (button) {

            button.addEventListener(
                "click",
                function () {

                    const alert =
                        button.closest(".alert");

                    if (alert) {

                        alert.style.opacity = "0";

                        alert.style.transition =
                            "opacity 0.2s ease";

                        setTimeout(function () {

                            alert.remove();

                        }, 200);

                    }

                }
            );

        });


    /* ================================
       CLEAR VALIDATION STATE
    ================================= */

    form
        .querySelectorAll(
            "input, select, textarea"
        )
        .forEach(function (field) {

            field.addEventListener(
                "input",
                function () {

                    field.setCustomValidity("");

                }
            );

            field.addEventListener(
                "change",
                function () {

                    field.setCustomValidity("");

                }
            );

        });

});