console.log("upload.js loaded");

const accessToken = localStorage.getItem("access_token");
if (!accessToken) {
    window.location.href = "index.html";
}

const fileInput = document.getElementById("file-input");
const dropZone = document.getElementById("drop-zone");
const fileName = document.getElementById("file-name");
const uploadBtn = document.getElementById("upload-btn");
const statusBox = document.getElementById("status-box");
const logoutBtn = document.getElementById("logout-btn");

const BASE_URL = "http://127.0.0.1:8000/api/v1";
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

// file selected via file picker
fileInput.addEventListener("change", (event) => {
    const file = event.target.files[0];

    if (!file) return;

    selectedFile = file;
    fileName.textContent = file.name;
    statusBox.textContent = "";
});

// Drag and drop event prevention & styling
["dragenter", "dragover"].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add("drag-over");
    }, false);
});

["dragleave", "drop"].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove("drag-over");
    }, false);
});

// File dropped handler
dropZone.addEventListener("drop", (e) => {
    const dt = e.dataTransfer;
    const file = dt.files[0];

    if (file) {
        if (file.name.endsWith(".pdf")) {
            selectedFile = file;
            fileName.textContent = file.name;
            statusBox.textContent = "";
        } else {
            statusBox.textContent = "Only PDF statement files are supported.";
            statusBox.className = "status-box text-danger";
        }
    }
});

// upload handler
uploadBtn.addEventListener("click", async (event) => {
    event.preventDefault();

    console.log("Upload button clicked");
    if (!selectedFile) {
        statusBox.textContent = "Please select a PDF file first.";
        statusBox.className = "status-box text-danger";
        return;
    }

    const token = localStorage.getItem("access_token");
    const formData = new FormData();
    formData.append("file", selectedFile);

    // visual loading state
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
        Uploading...
    `;
    statusBox.textContent = "Uploading statement & parsing transactions...";
    statusBox.className = "status-box text-warning";

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
            statusBox.className = "status-box text-danger";
            uploadBtn.disabled = false;
            uploadBtn.textContent = "Upload Statement";
            return;
        }

        statusBox.textContent = `Upload successful! Parsed ${data.transactions_parsed} transactions. Open the statement view and click Run AI Audit when you want AI insights.`;
        statusBox.className = "status-box text-success";

        // Redirect to Statement Details page
        setTimeout(() => {
            window.location.href = `statement_details.html?id=${data.statement_id}`;
        }, 1200);

    } catch (error) {
        console.error(error);
        statusBox.textContent = "Network error. Please try again.";
        statusBox.className = "status-box text-danger";
        uploadBtn.disabled = false;
        uploadBtn.textContent = "Upload Statement";
    }
});