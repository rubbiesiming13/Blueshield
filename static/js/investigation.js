document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById(
        "investigationWorkspaceForm"
    );

    const saveButton = document.getElementById(
        "saveWorkspaceBtn"
    );

    const statementField = document.getElementById(
        "id_statement"
    );

    const statementCount = document.getElementById(
        "statementCount"
    );


    /* =====================================================
       STATEMENT CHARACTER COUNT
    ====================================================== */

    if (statementField && statementCount) {

        function updateCharacterCount() {

            statementCount.textContent =
                statementField.value.length;

        }

        statementField.addEventListener(
            "input",
            updateCharacterCount
        );

        updateCharacterCount();
    }


    /* =====================================================
       PREVENT DOUBLE SUBMISSION
    ====================================================== */

    if (form && saveButton) {

        form.addEventListener("submit", function () {

            saveButton.disabled = true;

            saveButton.innerHTML =
                '<span class="spinner-border spinner-border-sm me-2"></span>' +
                'Saving Record...';

        });

    }

});