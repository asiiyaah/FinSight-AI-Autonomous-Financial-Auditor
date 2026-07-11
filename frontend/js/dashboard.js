console.log("dashboard.js loaded");

const BASE_URL = "http://127.0.0.1:8000/api/v1";
const accessToken = localStorage.getItem("access_token");

if (!accessToken) {
    window.location.href = "index.html";
}

// Elements
const logoutBtn = document.getElementById("logout-btn");
const welcomeText = document.getElementById("welcome-text");
const newUserWelcome = document.getElementById("new-user-welcome");
const newUserSection = document.getElementById("new-user-section");
const existingUserSection = document.getElementById("existing-user-section");
const uploadBtn = document.getElementById("upload-btn");
const statementsBtn = document.getElementById("statements-btn");

// Logout
logoutBtn.addEventListener("click", () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("is_new_user");
    window.location.href = "index.html";
});

// Navigation
uploadBtn.addEventListener("click", () => { window.location.href = "upload.html"; });
statementsBtn.addEventListener("click", () => { window.location.href = "statements.html"; });

// Format date (short)
function formatDate(dateString) {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleDateString("en-IN", {
        year: "numeric", month: "short", day: "numeric"
    });
}

// Load user profile
async function loadUser() {
    try {
        // Reset layout state before rendering fresh data
        newUserSection.classList.add("d-none");
        existingUserSection.classList.add("d-none");
        document.getElementById("recent-loading").classList.remove("d-none");
        document.getElementById("recent-empty").classList.add("d-none");
        document.getElementById("recent-list").classList.add("d-none");

        const response = await fetch(`${BASE_URL}/accounts/me/`, {
            headers: { Authorization: `Bearer ${accessToken}` }
        });

        if (!response.ok) {
            localStorage.clear();
            window.location.href = "index.html";
            return;
        }

        const data = await response.json();
        const firstName = data.first_name || data.username;

        // Check actual statement count instead of relying on a flag
        // This ensures the dashboard is always accurate regardless of how user got here
        const stmtResponse = await fetch(`${BASE_URL}/statements/?page=1`, {
            headers: { Authorization: `Bearer ${accessToken}` }
        });

        if (!stmtResponse.ok) {
            localStorage.clear();
            window.location.href = "index.html";
            return;
        }

        const stmtData = await stmtResponse.json();
        const totalStatements = stmtData.count || 0;

        if (totalStatements === 0) {
            // New user OR user who deleted everything — show welcome card
            newUserWelcome.textContent = `Welcome to FinSight, ${firstName}!`;
            newUserSection.classList.remove("d-none");
            existingUserSection.classList.add("d-none");
        } else {
            // Has statements — show full dashboard
            welcomeText.textContent = `Welcome back, ${firstName}!`;
            existingUserSection.classList.remove("d-none");
            newUserSection.classList.add("d-none");
            renderDashboardData(stmtData); // pass data we already fetched
        }

    } catch (error) {
        console.error("loadUser error:", error);
    }
}

function checkRefreshFlag() {
    const requiresRefresh = sessionStorage.getItem("refresh_dashboard") === "1";
    if (requiresRefresh) {
        sessionStorage.removeItem("refresh_dashboard");
        loadUser();
        return true;
    }
    return false;
}

document.addEventListener("DOMContentLoaded", () => {
    checkRefreshFlag();
    loadUser();
});

window.addEventListener("load", () => {
    checkRefreshFlag();
    loadUser();
});

window.addEventListener("pageshow", () => {
    checkRefreshFlag();
    loadUser();
});

window.addEventListener("popstate", () => {
    checkRefreshFlag();
    loadUser();
});

window.addEventListener("focus", () => {
    checkRefreshFlag();
    loadUser();
});

window.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") {
        checkRefreshFlag();
        loadUser();
    }
});

window.addEventListener("storage", (event) => {
    if (event.key === "refresh_dashboard") {
        checkRefreshFlag();
        loadUser();
    }
});

// Render statements for stats + recent list
function renderDashboardData(data) {
    try {
        const results = data.results || [];
        const totalCount = data.count || 0;

        // --- If no statements exist, show simplified state ---
        if (totalCount === 0) {
            document.getElementById("stat-total").textContent = "0";
            document.getElementById("stat-audited").textContent = "0";
            document.getElementById("stat-pending").textContent = "0";
            document.getElementById("stat-last-upload").textContent = "None yet";
            document.getElementById("recent-loading").classList.add("d-none");
            document.getElementById("recent-empty").classList.remove("d-none");
            return;
        }

        // --- Compute Stats ---
        // Fetch all pages to count across all statements
        // (page 1 gives us first 5 results; count comes from API)
        // We compute from page 1 results since it's enough for recent view;
        // for accurate counts we do a second targeted call if needed
        let auditedCount = 0;
        let pendingCount = 0;

        results.forEach(stmt => {
            if (stmt.audit_status === "completed") auditedCount++;
            else pendingCount++;
        });

        // If there are more pages, we can't count exactly without fetching all —
        // so we show proportional estimate from count
        if (totalCount > results.length) {
            const auditedRatio = results.filter(s => s.audit_status === "completed").length / results.length;
            auditedCount = Math.round(auditedRatio * totalCount);
            pendingCount = totalCount - auditedCount;
        }

        document.getElementById("stat-total").textContent = totalCount;
        document.getElementById("stat-audited").textContent = auditedCount;
        document.getElementById("stat-pending").textContent = pendingCount;
        document.getElementById("stat-last-upload").textContent = formatDate(results[0]?.uploaded_at);

        // --- Render Recent Statements (up to 5) ---
        const recentList = document.getElementById("recent-list");
        recentList.innerHTML = "";

        results.slice(0, 5).forEach(stmt => {
            const badgeClass = stmt.audit_status;
            const badgeLabel = {
                completed: "Audited",
                analytics_ready: "Ready",
                uploaded: "Uploaded",
                failed: "Failed"
            }[stmt.audit_status] || "Uploaded";

            const row = document.createElement("a");
            row.href = `statement_details.html?id=${stmt.id}`;
            row.className = "recent-row";
            row.innerHTML = `
                <div class="d-flex align-items-center gap-2 flex-grow-1 min-width-0">
                    <i class="bi bi-file-earmark-pdf-fill" style="color:var(--primary);font-size:1.1rem;flex-shrink:0"></i>
                    <span class="recent-file-name">${stmt.file_name}</span>
                </div>
                <span class="recent-date">${formatDate(stmt.uploaded_at)}</span>
                <span class="recent-badge ${badgeClass}">${badgeLabel}</span>
            `;
            recentList.appendChild(row);
        });

        document.getElementById("recent-loading").classList.add("d-none");
        recentList.classList.remove("d-none");

    } catch (error) {
        console.error("loadDashboardData error:", error);
        document.getElementById("recent-loading").classList.add("d-none");
    }
}

// Init
loadUser();
