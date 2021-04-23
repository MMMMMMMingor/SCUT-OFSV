import "./index.css";
import axios from "axios";

const usernameInput = document.getElementById("username_input");
const enrollmentBtn = document.getElementById("enrollment_btn");
const verificationBtn = document.getElementById("verification_btn");

const params = new URLSearchParams(window.location.search);
const username = params.get("username");
usernameInput.value = username;

enrollmentBtn.addEventListener("click", async () => {
    let name = usernameInput.value.trim();
    if (name === "") {
        alert("input can not be empty");
        return;
    }

    enrollmentBtn.disabled = true;

    let res = await axios.get(`/api/user/${encodeURIComponent(name)}`);
    if (res.data.exist === 'true') {
        alert(`用户名: ${name} 已存在`);
        usernameInput.value = '';
        enrollmentBtn.disabled = false;
        return;
    }

    let redirect_url = '/enroll.html?username=' + encodeURIComponent(name);
    window.location = redirect_url;
});

verificationBtn.addEventListener("click", async () => {
    let name = usernameInput.value.trim();
    if (name === "") {
        alert("input can not be empty");
        return;
    }

    verificationBtn.disabled = true;

    let res = await axios.get(`/api/user/${encodeURIComponent(name)}`);
    if (res.data.exist === 'false') {
        alert(`用户名: ${name} 不存在, 请先注册`);
        verificationBtn.disabled = false;
        return;
    }

    let redirect_url = '/verify.html?username=' + encodeURIComponent(name);
    window.location = redirect_url;
});
