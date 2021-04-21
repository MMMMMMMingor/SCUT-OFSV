import "./index.css";

const usernameInput = document.getElementById("username_input");
const enrollmentBtn = document.getElementById("enrollment_btn");
const verificationBtn = document.getElementById("verification_btn");

enrollmentBtn.addEventListener("click", () => {
    if (usernameInput.value.trim() === "") {
        alert("input can not be empty");
        return;
    }

    let redirect_url = '/enroll.html?username=' + encodeURIComponent(usernameInput.value.trim());
    window.location = redirect_url;
});

verificationBtn.addEventListener("click", () => {
    if (usernameInput.value.trim() === "") {
        alert("input can not be empty");
        return;
    }

    let redirect_url = '/enroll.html?username=' + encodeURIComponent(usernameInput.value.trim());
    window.location = redirect_url;
});
