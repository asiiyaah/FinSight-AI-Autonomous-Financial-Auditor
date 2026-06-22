const BASE_URL = "http://127.0.0.1:8000/api/v1";

const accessToken = localStorage.getItem("access_token");

if (!accessToken) {
    window.location.href = "index.html";
}

const logoutBtn = document.getElementById("logout-btn");

const welcomeText = document.getElementById("welcome-text");
const newUserWelcome = document.getElementById("new-user-welcome");

const newUserSection = document.getElementById("new-user-section");
const existingUserSection = document.getElementById("existing-user-section");

async function loadUser() {
    try {
        const response = await fetch(`${BASE_URL}/accounts/me/`, {
            headers: {
                Authorization: `Bearer ${accessToken}`
            }
        });

        if (!response.ok) {
            localStorage.clear();
            window.location.href = "index.html";
            return;
        }

        const data = await response.json();

        const firstName = data.first_name;
        const isNewUser = localStorage.getItem("is_new_user");

        if (isNewUser === "true") {
            newUserWelcome.textContent = `Welcome to FinSight, ${firstName}!`;
            newUserSection.classList.remove("d-none");
        } else {
            welcomeText.textContent = `Welcome back, ${firstName}!`;
            existingUserSection.classList.remove("d-none");
        }

    } catch (error) {
        console.error(error);
    }
}

loadUser();

logoutBtn.addEventListener("click", () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("is_new_user");

    window.location.href = "index.html";
});


const uploadBtn = document.getElementById("upload-btn");
const statementsBtn = document.querySelector("#statements-card button");

uploadBtn.addEventListener("click", () => {
    console.log("UPLOAD CLICKED");
    window.location.href = "upload.html";
});

statementsBtn.addEventListener("click", () => {
    console.log("STATEMENTS CLICKED");
    window.location.href = "statements.html";
});
