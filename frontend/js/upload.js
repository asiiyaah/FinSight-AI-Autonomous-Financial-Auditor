const fileInput = document.getElementById("file-input");
const dropZone = document.getElementById("drop-zone");
const fileName = document.getElementById("file-name");
const uploadBtn = document.getElementById("upload-btn");
const statusBox = document.getElementById("status-box");
const logoutBtn = document.getElementById("logout-btn");

const BASE_URL = "http://127.0.0.1:8000";
let selectedFile = null;

// logout
logoutBtn.addEventListener("click", () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("is_new_user");
    window.location.href = "index.html";
});

// click dropzone opens file picker
dropZone.addEventListener("click", () => {
    fileInput.click();
});

// file selected
fileInput.addEventListener("change", (event) => {
    const file = event.target.files[0];

    if (!file) return;

    selectedFile = file;
    fileName.textContent = file.name;
});

// upload
uploadBtn.addEventListener("click", async () => {
    if (!selectedFile) {
        statusBox.textContent = "Please select a PDF file first.";
        return;
    }

    const token = localStorage.getItem("access_token");

    const formData = new FormData();
    formData.append("file", selectedFile);

    statusBox.textContent = "Uploading and parsing...";

    try {
        const response = await fetch(`${BASE_URL}/statements/upload/`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${token}`
            },
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            statusBox.textContent = data.error || data.message || "Upload failed";
            return;
        }

        statusBox.textContent =
            `Upload successful! Parsed ${data.transactions_parsed} transactions`;

        console.log(data);

    } catch (error) {
        console.error(error);
        statusBox.textContent = "Server error. Try again.";
    }
});