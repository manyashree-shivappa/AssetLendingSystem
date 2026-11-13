/* ============================================
   ASSETFLOW - MAIN JAVASCRIPT
   Interactive website functions
============================================ */

document.addEventListener("DOMContentLoaded", function () {

    // 1. Automatically hide notification messages
    const messages = document.querySelectorAll(
        ".message, .alert"
    );

    messages.forEach(function (message) {
        setTimeout(function () {
            message.style.transition = "opacity 0.5s ease";
            message.style.opacity = "0";

            setTimeout(function () {
                message.remove();
            }, 500);
        }, 5000);
    });


    // 2. Validate asset request dates
    const startDate = document.querySelector(
        'input[name="start_date"]'
    );

    const endDate = document.querySelector(
        'input[name="end_date"]'
    );

    if (startDate) {
        const today = new Date();

        const localToday = new Date(
            today.getTime() -
            today.getTimezoneOffset() * 60000
        ).toISOString().split("T")[0];

        startDate.min = localToday;

        startDate.addEventListener("change", function () {

            if (endDate) {
                endDate.min = startDate.value;

                if (
                    endDate.value &&
                    endDate.value < startDate.value
                ) {
                    endDate.value = "";
                }
            }

        });
    }


    // 3. Validate branch transfer selection
    const fromBranch = document.querySelector(
        'select[name="from_branch"]'
    );

    const toBranch = document.querySelector(
        'select[name="to_branch"]'
    );

    function validateBranches() {

        if (!fromBranch || !toBranch) {
            return;
        }

        if (
            fromBranch.value &&
            fromBranch.value === toBranch.value
        ) {
            toBranch.setCustomValidity(
                "Please select a different destination branch."
            );
        } else {
            toBranch.setCustomValidity("");
        }

    }

    if (fromBranch && toBranch) {
        fromBranch.addEventListener(
            "change",
            validateBranches
        );

        toBranch.addEventListener(
            "change",
            validateBranches
        );
    }


    // 4. Confirm important actions
    const confirmElements = document.querySelectorAll(
        "[data-confirm]"
    );

    confirmElements.forEach(function (element) {

        element.addEventListener("click", function (event) {

            const confirmation =
                element.dataset.confirm || "Are you sure?";

            if (!window.confirm(confirmation)) {
                event.preventDefault();
            }

        });

    });


    // 5. Toggle password visibility
    const passwordToggle = document.querySelector(
        "[data-password-toggle]"
    );

    if (passwordToggle) {

        passwordToggle.addEventListener("click", function () {

            const targetId =
                passwordToggle.dataset.passwordToggle;

            const passwordInput =
                document.getElementById(targetId);

            if (passwordInput) {

                passwordInput.type =
                    passwordInput.type === "password"
                        ? "text"
                        : "password";

            }

        });

    }


    // 6. Prevent accidental double submission
    document.querySelectorAll("form").forEach(function (form) {

        form.addEventListener("submit", function () {

            const submitButton = form.querySelector(
                'button[type="submit"], input[type="submit"]'
            );

            if (submitButton && form.checkValidity()) {
                submitButton.disabled = true;
                submitButton.textContent = "Please wait...";
            }

        });

    });

});
