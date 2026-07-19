console.log("statements.js loaded");

const BASE_URL = "http://127.0.0.1:8000/api/v1";

// Auth guard
const accessToken = localStorage.getItem("access_token");
if (!accessToken) {
    window.location.href = "index.html";
}

// Simple Toast Notification System
function showToast(message) {
    const toast = document.createElement("div");
    toast.textContent = message;
    toast.style.position = "fixed";
    toast.style.bottom = "20px";
    toast.style.left = "50%";
    toast.style.transform = "translateX(-50%)";
    toast.style.backgroundColor = "#333";
    toast.style.color = "#fff";
    toast.style.padding = "10px 20px";
    toast.style.borderRadius = "5px";
    toast.style.zIndex = "9999";
    toast.style.boxShadow = "0 2px 10px rgba(0,0,0,0.2)";
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Elements
const loadingState = document.getElementById("loading-state");
const emptyState = document.getElementById("empty-state");
const statementsContainer = document.getElementById("statements-container");
const statementsGrid = document.getElementById("statements-grid");
const paginationControls = document.getElementById("pagination-controls");
const prevBtn = document.getElementById("prev-btn");
const nextBtn = document.getElementById("next-btn");
const pageInfo = document.getElementById("page-info");
const logoutBtn = document.getElementById("logout-btn");
const deleteFileNameEl = document.getElementById("delete-file-name");
const confirmDeleteBtn = document.getElementById("confirm-delete-btn");

// State
let currentPage = 1;
let totalPages = 1;
let statementToDeleteId = null;
let statementToDeleteName = null;
const deleteModal = new bootstrap.Modal(document.getElementById("deleteModal"));

// Logout
logoutBtn.addEventListener("click", () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("is_new_user");
    window.location.href = "index.html";
});

// Format date
function formatDate(dateString) {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-IN", {
        year: "numeric",
        month: "short",
        day: "numeric"
    });
}

// Get status badge HTML
function getStatusBadge(status) {
    const statusMap = {
        uploaded: { label: "Uploaded", icon: "bi-cloud-check" },
        analytics_ready: { label: "Analysis Ready", icon: "bi-bar-chart-fill" },
        completed: { label: "Audited", icon: "bi-shield-check-fill" },
        failed: { label: "Failed", icon: "bi-x-circle-fill" }
    };
    const s = statusMap[status] || statusMap.uploaded;
    return `<span class="status-badge ${status}"><i class="bi ${s.icon}"></i>${s.label}</span>`;
}

// Render statement cards
function renderStatements(statements) {
    statementsGrid.innerHTML = "";

    statements.forEach(stmt => {
        const col = document.createElement("div");
        col.className = "col-md-6 col-lg-4";

        const txCount = stmt.transaction_count ?? "—";
        const auditStatusLabel = stmt.audit_status === "completed"
            ? '<span class="text-success"><i class="bi bi-cpu-fill me-1"></i>AI Audited</span>'
            : stmt.audit_status === "analytics_ready"
            ? '<span class="text-primary"><i class="bi bi-bar-chart me-1"></i>Analytics Ready</span>'
            : '<span class="text-muted-custom">Not Audited</span>';

        col.innerHTML = `
            <div class="statement-card">
                <div class="card-top">
                    <div class="file-icon-wrapper">
                        <i class="bi bi-file-earmark-pdf-fill"></i>
                    </div>
                    <div class="card-title-block">
                        <p class="card-file-name" title="${stmt.file_name}">${stmt.file_name}</p>
                        <p class="card-upload-date"><i class="bi bi-calendar3 me-1"></i>${formatDate(stmt.uploaded_at)}</p>
                    </div>
                    ${getStatusBadge(stmt.audit_status)}
                </div>

                <div class="card-stats">
                    <div class="card-stat">
                        <div class="card-stat-label">Transactions</div>
                        <div class="card-stat-value">${txCount}</div>
                    </div>
                    <div class="card-stat">
                        <div class="card-stat-label">AI Audit</div>
                        <div class="card-stat-value">${auditStatusLabel}</div>
                    </div>
                </div>

                <div class="card-actions">
                    <a href="statement_details.html?id=${stmt.id}" class="view-btn" id="view-btn-${stmt.id}">
                        <i class="bi bi-eye"></i> View Details
                    </a>
                    <button class="delete-btn" id="delete-btn-${stmt.id}" data-id="${stmt.id}" data-name="${stmt.file_name}">
                        <i class="bi bi-trash3"></i>
                    </button>
                </div>
            </div>
        `;

        statementsGrid.appendChild(col);
    });

    // Bind delete buttons
    document.querySelectorAll(".delete-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            statementToDeleteId = btn.dataset.id;
            statementToDeleteName = btn.dataset.name;
            deleteFileNameEl.textContent = statementToDeleteName;
            deleteModal.show();
        });
    });
}

// Fetch statements from API
async function fetchStatements(page = 1) {
    loadingState.classList.remove("d-none");
    emptyState.classList.add("d-none");
    statementsContainer.classList.add("d-none");

    try {
        const response = await fetch(`${BASE_URL}/statements/?page=${page}`, {
            headers: { Authorization: `Bearer ${accessToken}` }
        });

        if (!response.ok) {
            if (response.status === 401) {
                localStorage.clear();
                window.location.href = "index.html";
                return;
            }
            throw new Error("Failed to load statements");
        }

        const data = await response.json();
        const results = data.results || [];
        const count = data.count || 0;
        const pageSize = 5; // matches backend PAGE_SIZE

        loadingState.classList.add("d-none");

        if (results.length === 0 && page === 1) {
            emptyState.classList.remove("d-none");
            return;
        }

        totalPages = Math.ceil(count / pageSize);
        currentPage = page;

        renderStatements(results);
        statementsContainer.classList.remove("d-none");

        // Update pagination
        if (totalPages > 1) {
            paginationControls.classList.remove("d-none");
            pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
            prevBtn.disabled = currentPage <= 1;
            nextBtn.disabled = currentPage >= totalPages;
        } else {
            paginationControls.classList.add("d-none");
        }

    } catch (error) {
        console.error(error);
        loadingState.classList.add("d-none");
        statementsGrid.innerHTML = `
            <div class="col-12 text-center py-5">
                <p class="text-muted-custom">Failed to load statements. Please refresh the page.</p>
            </div>`;
        statementsContainer.classList.remove("d-none");
    }
}

// Pagination events
prevBtn.addEventListener("click", () => {
    if (currentPage > 1) fetchStatements(currentPage - 1);
});

nextBtn.addEventListener("click", () => {
    if (currentPage < totalPages) fetchStatements(currentPage + 1);
});

// Delete confirmation
confirmDeleteBtn.addEventListener("click", async () => {
    if (!statementToDeleteId) return;

    confirmDeleteBtn.disabled = true;
    confirmDeleteBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>Deleting...`;

    try {
        const response = await fetch(`${BASE_URL}/statements/${statementToDeleteId}/`, {
            method: "DELETE",
            headers: { Authorization: `Bearer ${accessToken}` }
        });

        if (response.ok || response.status === 204 || response.status === 404) {
            deleteModal.hide();
            // Reload current page (or go back if this was last item on page)
            fetchStatements(currentPage);
            if (response.status === 404) {
                showToast("Statement no longer exists. Cleaned up.");
            }
        } else {
            const errData = await response.json().catch(() => ({}));
            showToast(errData.error || "Delete failed. Please try again.");
        }
    } catch (error) {
        console.error(error);
        showToast("Network error. Could not delete statement.");
    } finally {
        confirmDeleteBtn.disabled = false;
        confirmDeleteBtn.innerHTML = `<i class="bi bi-trash3 me-1"></i>Delete`;
        statementToDeleteId = null;
        statementToDeleteName = null;
    }
});

// Initialize
fetchStatements(1);
