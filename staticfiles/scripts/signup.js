document.addEventListener("DOMContentLoaded", function () {
    const usernameInput = document.querySelector('input[name="username"]');
    const roleSelect = document.querySelector('select[name="role"]');

    usernameInput.addEventListener("input", function () {
        const username = usernameInput.value.trim().toLowerCase();
        if (username.endsWith("admin")) {
            roleSelect.value = "Admin";
        } else if (roleSelect.value === "Admin") {
            roleSelect.value = "";
        }
    });
});


function validateRecaptcha(event) {
const response = grecaptcha.getResponse();
if (!response) {
    event.preventDefault();
    alert("Please complete the reCAPTCHA to proceed.");
}
}

document.addEventListener("DOMContentLoaded", function () {
const form = document.querySelector("form");
if (form) {
    form.addEventListener("submit", validateRecaptcha);
}
});
