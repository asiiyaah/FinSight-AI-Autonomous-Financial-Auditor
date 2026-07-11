console.log("upload.js loaded");

const accessToken = localStorage.getItem("access_token");
if (!accessToken) {
    window.location.href = "index.html";
}

const fileInput = document.getElementById("file-input");
const dropZone = document.getElementById("drop-zone");
const fileNameEl = document.getElementById("file-name");
const uploadBtn = document.getElementById("upload-btn");
const statusBox = document.getElementById("status-box");
const logoutBtn = document.getElementById("logout-btn");
const progressStepper = document.getElementById("progress-stepper");
const progressFill = document.getElementById("progress-fill");
const progressLabel = document.getElementById("progress-step-label");
const progressCounter = document.getElementById("progress-step-counter");
const progressSub = document.getElementById("progress-sub-label");

const BASE_URL = "http://127.0.0.1:8000/api/v1";
let selectedFile = null;

// ── Progress bar helpers ──────────────────────────────
const STEPS = [
    { pct: 20,  label: "Uploading PDF...",           sub: "Sending your file securely",                counter: "1 / 5" },
    { pct: 40,  label: "Parsing PDF with AI...",     sub: "Reading statement structure",               counter: "2 / 5" },
    { pct: 60,  label: "Extracting transactions...", sub: "Identifying dates, vendors & amounts",      counter: "3 / 5" },
    { pct: 80,  label: "Preparing analytics...",     sub: "Computing cashflow & risk insights",        counter: "4 / 5" },
    { pct: 100, label: "Complete!",                  sub: "Redirecting to your statement...",          counter: "5 / 5" },
];

function setProgress(stepIndex, state = "normal") {
    const step = STEPS[stepIndex];
    if (!step) return;

    progressFill.style.width = `${step.pct}%`;
    progressLabel.textContent = step.label;
    progressCounter.textContent = step.counter;
    progressSub.textContent = step.sub;

    progressFill.className = "progress-fill";
    if (state === "complete") progressFill.classList.add("complete");
    if (state === "error") progressFill.classList.add("error");
}

function setProgressError(message) {
    progressFill.className = "progress-fill error";
    progressLabel.textContent = "Upload failed";
    progressCounter.textContent = "";
    progressSub.textContent = message;
}

function resetProgress() {
    progressFill.style.width = "0%";
    progressFill.className = "progress-fill";
    progressLabel.textContent = "Starting...";
    progressCounter.textContent = "0 / 5";
    progressSub.textContent = "";
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ── Logout ───────────────────────────────────────────
logoutBtn.addEventListener("click", () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("is_new_user");
    window.location.href = "index.html";
});

// ── Drop zone ────────────────────────────────────────
dropZone.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (!file) return;
    selectedFile = file;
    fileNameEl.textContent = file.name;
    statusBox.textContent = "";
});

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

dropZone.addEventListener("drop", (e) => {
    const file = e.dataTransfer.files[0];
    if (file) {
        if (file.name.toLowerCase().endsWith(".pdf")) {
            selectedFile = file;
            fileNameEl.textContent = file.name;
            statusBox.textContent = "";
        } else {
            statusBox.textContent = "Only PDF files are supported.";
            statusBox.className = "status-box text-danger";
        }
    }
});

// ── Upload handler ───────────────────────────────────
uploadBtn.addEventListener("click", async (event) => {
    event.preventDefault();

    if (!selectedFile) {
        statusBox.textContent = "Please select a PDF file first.";
        statusBox.className = "status-box text-danger";
        return;
    }

    const token = localStorage.getItem("access_token");
    const formData = new FormData();
    formData.append("file", selectedFile);

    // Lock UI & show progress bar
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing...`;
    statusBox.textContent = "";
    statusBox.className = "status-box";

    progressStepper.classList.remove("d-none");
    resetProgress();

    // Step 1 — Uploading (20%)
    setProgress(0);

    try {
        const response = await fetch(`${BASE_URL}/statements/upload/`, {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            setProgressError(data.error || data.message || "Upload failed.");
            statusBox.textContent = data.error || data.message || "Upload failed.";
            statusBox.className = "status-box text-danger";
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = `<i class="bi bi-cloud-upload me-2"></i>Upload Statement`;
            return;
        }

        // Step 2 — Parsing (40%)
        setProgress(1);
        await delay(500);

        // Step 3 — Extracting (60%)
        setProgress(2);
        await delay(450);

        // Step 4 — Analytics (80%)
        setProgress(3);
        await delay(400);

        // Step 5 — Done (100%)
        setProgress(4, "complete");
        progressLabel.textContent = `Done — ${data.transactions_parsed} transactions extracted`;

        localStorage.setItem("refresh_dashboard", "1");
        await delay(900);
        window.location.href = `statement_details.html?id=${data.statement_id}`;

    } catch (error) {
        console.error(error);
        setProgressError("Network error. Please check your connection.");
        statusBox.textContent = "Network error. Please try again.";
        statusBox.className = "status-box text-danger";
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = `<i class="bi bi-cloud-upload me-2"></i>Upload Statement`;
    }
});