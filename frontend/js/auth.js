const BASE_URL = "http://127.0.0.1:8000/api/v1";


const loginTab = document.getElementById("login-tab");
const registerTab = document.getElementById("register-tab");

const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");

const registerPassword = document.getElementById("register-password");
const registerConfirmPassword = document.getElementById("register-confirm-password");
const policyContainer = document.getElementById("password-policy-container");
const mismatchError = document.getElementById("password-mismatch-error");
const registerErrorMsg = document.getElementById("register-error-message");

loginTab.addEventListener("click", () => {
    loginTab.classList.add("active");
    registerTab.classList.remove("active");

    loginForm.classList.remove("d-none");
    registerForm.classList.add("d-none");
});

registerTab.addEventListener("click", () => {
    registerTab.classList.add("active");
    loginTab.classList.remove("active");

    registerForm.classList.remove("d-none");
    loginForm.classList.add("d-none");
});

// Password Visibility Toggle
document.querySelectorAll('.toggle-password').forEach(button => {
    button.addEventListener('click', function() {
        const targetId = this.getAttribute('data-target');
        const input = document.getElementById(targetId);
        const icon = this.querySelector('i');
        
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('bi-eye');
            icon.classList.add('bi-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.remove('bi-eye-slash');
            icon.classList.add('bi-eye');
        }
    });
});

// Real-time password policy validation
const updatePolicyCheck = (id, isValid) => {
    const el = document.getElementById(id);
    const icon = el.querySelector('i');
    if (isValid) {
        el.classList.remove('text-muted-custom');
        el.classList.add('text-success');
        icon.classList.remove('bi-circle');
        icon.classList.add('bi-check-circle-fill');
    } else {
        el.classList.remove('text-success');
        el.classList.add('text-muted-custom');
        icon.classList.remove('bi-check-circle-fill');
        icon.classList.add('bi-circle');
    }
};

const validatePasswordPolicy = (pwd) => {
    const isLengthValid = pwd.length >= 8;
    const isUpperValid = /[A-Z]/.test(pwd);
    const isLowerValid = /[a-z]/.test(pwd);
    const isNumberValid = /[0-9]/.test(pwd);
    const isSpecialValid = /[^a-zA-Z0-9]/.test(pwd);

    updatePolicyCheck('req-length', isLengthValid);
    updatePolicyCheck('req-upper', isUpperValid);
    updatePolicyCheck('req-lower', isLowerValid);
    updatePolicyCheck('req-number', isNumberValid);
    updatePolicyCheck('req-special', isSpecialValid);

    return isLengthValid && isUpperValid && isLowerValid && isNumberValid && isSpecialValid;
};

registerPassword.addEventListener("input", (e) => {
    policyContainer.style.display = "block";
    validatePasswordPolicy(e.target.value);
    checkMismatch();
});

registerConfirmPassword.addEventListener("input", () => {
    checkMismatch();
});

const checkMismatch = () => {
    const pwd = registerPassword.value;
    const confirmPwd = registerConfirmPassword.value;
    
    if (confirmPwd && pwd !== confirmPwd) {
        mismatchError.style.display = "block";
    } else {
        mismatchError.style.display = "none";
    }
};

registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    registerErrorMsg.style.display = "none";

    const username = document.getElementById("register-username").value;
    const firstName = document.getElementById("register-firstname").value;
    const lastName = document.getElementById("register-lastname").value;
    const email = document.getElementById("register-email").value;
    const password = registerPassword.value;
    const confirmPassword = registerConfirmPassword.value;

    if (!validatePasswordPolicy(password)) {
        registerErrorMsg.textContent = "Please ensure your password meets all requirements.";
        registerErrorMsg.style.display = "block";
        return;
    }

    if (password !== confirmPassword) {
        registerErrorMsg.textContent = "Passwords do not match!";
        registerErrorMsg.style.display = "block";
        return;
    }

    try {
        const response = await fetch(`${BASE_URL}/accounts/register/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                first_name: firstName,
                last_name: lastName,
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("access_token", data.access);
            localStorage.setItem("refresh_token", data.refresh);
            localStorage.setItem("is_new_user", "true");
            window.location.href = "dashboard.html";
        } else {

            const firstField = Object.keys(data)[0];
            let errorMessage = "Registration failed.";
            if (Array.isArray(data[firstField])) {
                errorMessage = data[firstField][0];
            } else if (typeof data[firstField] === 'string') {
                errorMessage = data[firstField];
            }
            registerErrorMsg.textContent = errorMessage;
            registerErrorMsg.style.display = "block";
        }

    } catch (error) {
        console.error(error);
        registerErrorMsg.textContent = "Something went wrong! Could not connect to the server.";
        registerErrorMsg.style.display = "block";
    }
});

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    try {
        const response = await fetch(`${BASE_URL}/accounts/login/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("access_token", data.access);
            localStorage.setItem("refresh_token", data.refresh);
            localStorage.setItem("is_new_user", "false");
            window.location.href = "dashboard.html";
        } else {

            alert("Login failed! " + (data.detail || "Invalid credentials"));
        }

    } catch (error) {
        console.error(error);
        alert("Something went wrong! Could not connect to the server.");
    }
});