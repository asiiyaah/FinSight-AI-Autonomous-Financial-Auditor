console.log("statement_details.js loaded");

// Token Check
const accessToken = localStorage.getItem("access_token");
if (!accessToken) {
    window.location.href = "index.html";
}

const BASE_URL = "http://127.0.0.1:8000/api/v1";

// Get statement ID from URL query parameters
const urlParams = new URLSearchParams(window.location.search);
const statementId = urlParams.get("id");

if (!statementId) {
    alert("No statement ID provided.");
    window.location.href = "dashboard.html";
}

// Elements
const logoutBtn = document.getElementById("logout-btn");
const docTitle = document.getElementById("doc-title");
const docStatusBadge = document.getElementById("doc-status-badge");
const infoUploadedAt = document.getElementById("info-uploaded-at");
const infoParsingStatus = document.getElementById("info-parsing-status");
const infoTxCount = document.getElementById("info-tx-count");
const infoAuditStatus = document.getElementById("info-audit-status");
const runAuditBtn = document.getElementById("run-audit-btn");
const auditProgress = document.getElementById("audit-progress");
const auditHelperText = document.getElementById("audit-helper-text");
const loadingState = document.getElementById("loading-state");
const detailsContent = document.getElementById("details-content");

// Logout
logoutBtn.addEventListener("click", () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("is_new_user");
    window.location.href = "index.html";
});

// Load statement details
async function fetchStatementDetails() {
    try {
        const response = await fetch(`${BASE_URL}/statements/${statementId}/`, {
            headers: {
                Authorization: `Bearer ${accessToken}`
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                localStorage.clear();
                window.location.href = "index.html";
                return;
            }
            alert("Error loading statement details.");
            window.location.href = "dashboard.html";
            return;
        }

        const data = await response.json();
        renderPage(data);

    } catch (error) {
        console.error(error);
        alert("Failed to connect to the server.");
        window.location.href = "dashboard.html";
    }
}

// Format Date
function formatDate(dateString) {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-IN", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
    });
}

// Render Page Content
function renderPage(data) {
    loadingState.classList.add("d-none");
    detailsContent.classList.remove("d-none");

    const stmt = data.statement;
    const analytics = data.analytics;
    const aiAudit = data.ai_audit;

    // Sidebar text mapping
    docTitle.textContent = stmt.file_name;
    
    // Status badges
    let statusClass = "bg-secondary";
    let statusLabel = "Uploaded";
    if (stmt.audit_status === "completed") {
        statusClass = "bg-success";
        statusLabel = "Audited";
    } else if (stmt.audit_status === "analytics_ready") {
        statusClass = "bg-primary";
        statusLabel = "Analysis Ready";
    } else if (stmt.audit_status === "failed") {
        statusClass = "bg-danger";
        statusLabel = "Failed";
    }
    
    docStatusBadge.textContent = statusLabel;
    docStatusBadge.className = `badge ${statusClass} mt-2`;

    infoUploadedAt.textContent = formatDate(stmt.uploaded_at);
    infoParsingStatus.innerHTML = stmt.transaction_count > 0 
        ? '<span class="text-success"><i class="bi bi-patch-check-fill me-1"></i> Parsed</span>' 
        : '<span class="text-warning"><i class="bi bi-clock-history me-1"></i> Unparsed</span>';
    
    infoTxCount.textContent = stmt.transaction_count || "0";
    
    // Audit status details
    let auditText = "Not Audited";
    if (stmt.audit_status === "completed") {
        auditText = "Completed";
    } else if (stmt.audit_status === "failed") {
        auditText = "Failed";
    }
    infoAuditStatus.textContent = auditText;

    // Trigger AI Audit button configuration
    if (stmt.audit_status === "completed") {
        runAuditBtn.innerHTML = '<i class="bi bi-arrow-repeat me-2"></i> Re-run AI Audit';
        auditHelperText.textContent = "Audit completed. You can re-run it anytime.";
    } else {
        runAuditBtn.innerHTML = '<i class="bi bi-cpu me-2"></i> Run AI Audit';
        auditHelperText.textContent = "Upload is complete. Click Run AI Audit to generate AI findings for this statement.";
    }

    // Render Analytics
    renderAnalytics(analytics);

    // Render AI Audit details
    renderAIAudit(aiAudit);
}

// Format Currency
function formatCurrency(value) {
    if (value === undefined || value === null) return "₹0.00";
    return "₹" + parseFloat(value).toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Render Layer A Analytics details
function renderAnalytics(analytics) {
    if (!analytics) return;

    // Cashflow Cards
    const cashflow = analytics.cashflow;
    if (cashflow) {
        document.getElementById("stat-total-credit").textContent = formatCurrency(cashflow.total_credit);
        document.getElementById("stat-total-debit").textContent = formatCurrency(cashflow.total_debit);
        
        const netSavings = cashflow.net_savings;
        const netSavingsEl = document.getElementById("stat-net-savings");
        netSavingsEl.textContent = formatCurrency(netSavings);
        if (netSavings >= 0) {
            netSavingsEl.className = "text-success m-0 fw-bold";
        } else {
            netSavingsEl.className = "text-danger m-0 fw-bold";
        }
        
        document.getElementById("stat-savings-rate").textContent = `${cashflow.savings_rate}%`;
    }

    // Category Breakdown
    const spending = analytics.spending;
    const catList = document.getElementById("category-breakdown-list");
    catList.innerHTML = "";

    if (spending && spending.category_breakdown) {
        const breakdown = spending.category_breakdown;
        let totalSpend = 0;
        Object.values(breakdown).forEach(val => totalSpend += val);

        const sortedCategories = Object.entries(breakdown).sort((a, b) => b[1] - a[1]);

        if (sortedCategories.length > 0) {
            sortedCategories.forEach(([cat, amount]) => {
                const pct = totalSpend > 0 ? ((amount / totalSpend) * 100).toFixed(1) : 0;
                
                const catItem = document.createElement("div");
                catItem.className = "category-item";
                catItem.innerHTML = `
                    <div class="category-item-meta">
                        <span class="fw-semibold">${cat}</span>
                        <span class="text-muted-custom">${formatCurrency(amount)} (${pct}%)</span>
                    </div>
                    <div class="progress-custom">
                        <div class="progress-bar-custom" style="width: ${pct}%"></div>
                    </div>
                `;
                catList.appendChild(catItem);
            });
        } else {
            catList.innerHTML = '<p class="text-muted-custom m-0">No spending transactions recorded.</p>';
        }
    } else {
        catList.innerHTML = '<p class="text-muted-custom m-0">No spending breakdown available.</p>';
    }

    // Deterministic Risks
    const risks = analytics.risks;
    if (risks) {
        // 1. Anomalies
        const anomaliesList = document.getElementById("anomalies-list");
        anomaliesList.innerHTML = "";
        if (risks.anomalies && risks.anomalies.length > 0) {
            risks.anomalies.forEach(anom => {
                const item = document.createElement("div");
                item.className = "risk-info-item mb-2";
                item.innerHTML = `
                    <div class="risk-info-item-header">
                        <span class="fw-bold text-white">${anom.vendor}</span>
                        <span class="text-danger fw-bold">${formatCurrency(anom.amount)}</span>
                    </div>
                    <div class="d-flex justify-content-between text-muted-custom mt-1" style="font-size: 0.82rem;">
                        <span>Date: ${anom.date}</span>
                        <span>Threshold: ${formatCurrency(anom.threshold)}</span>
                    </div>
                `;
                anomaliesList.appendChild(item);
            });
        } else {
            anomaliesList.innerHTML = '<p class="text-muted-custom p-3 m-0">No unusual spending anomalies detected.</p>';
        }

        // 2. Duplicates
        const duplicatesList = document.getElementById("duplicates-list");
        duplicatesList.innerHTML = "";
        if (risks.duplicates && risks.duplicates.length > 0) {
            risks.duplicates.forEach(group => {
                if (group.length > 0) {
                    const first = group[0];
                    const item = document.createElement("div");
                    item.className = "risk-info-item mb-2";
                    item.innerHTML = `
                        <div class="risk-info-item-header">
                            <span class="fw-bold text-warning">${first.vendor}</span>
                            <span class="text-warning fw-bold">${group.length}x ${formatCurrency(first.amount)}</span>
                        </div>
                        <div class="text-muted-custom mt-1" style="font-size: 0.82rem;">
                            <span>Detected duplicates on date: ${first.date}</span>
                            <p class="mb-0 mt-1 small font-monospace">Raw: ${first.raw_description || 'N/A'}</p>
                        </div>
                    `;
                    duplicatesList.appendChild(item);
                }
            });
        } else {
            duplicatesList.innerHTML = '<p class="text-muted-custom p-3 m-0">No duplicate charges detected.</p>';
        }

        // 3. Subscriptions
        const subscriptionsList = document.getElementById("subscriptions-list");
        subscriptionsList.innerHTML = "";
        if (risks.subscriptions && risks.subscriptions.length > 0) {
            risks.subscriptions.forEach(sub => {
                const item = document.createElement("div");
                item.className = "risk-info-item mb-2";
                item.innerHTML = `
                    <div class="risk-info-item-header">
                        <span class="fw-bold text-white">${sub.vendor}</span>
                        <span class="text-primary fw-bold">${formatCurrency(sub.amount)}/mo</span>
                    </div>
                    <div class="d-flex justify-content-between text-muted-custom mt-1" style="font-size: 0.82rem;">
                        <span>Category: ${sub.category}</span>
                        <span>Detected in ${sub.months_detected} months (${sub.occurrences} charges)</span>
                    </div>
                `;
                subscriptionsList.appendChild(item);
            });
        } else {
            subscriptionsList.innerHTML = '<p class="text-muted-custom p-3 m-0">No recurring active subscriptions identified.</p>';
        }

        // 4. EMIs
        const emiList = document.getElementById("emi-list");
        emiList.innerHTML = "";
        if (risks.emi && risks.emi.detected && risks.emi.loans && risks.emi.loans.length > 0) {
            risks.emi.loans.forEach(loan => {
                const item = document.createElement("div");
                item.className = "risk-info-item mb-2";
                item.innerHTML = `
                    <div class="risk-info-item-header">
                        <span class="fw-bold text-info">${loan.vendor}</span>
                        <span class="text-info fw-bold">${formatCurrency(loan.amount)}/mo</span>
                    </div>
                    <div class="text-muted-custom mt-1" style="font-size: 0.82rem;">
                        <span>Active monthly EMI obligation detected. (Months detected: ${loan.months_detected})</span>
                    </div>
                `;
                emiList.appendChild(item);
            });
        } else {
            emiList.innerHTML = '<p class="text-muted-custom p-3 m-0">No active monthly loan EMI obligations detected.</p>';
        }
    }
}

// Render Layer B AI Audit findings
function renderAIAudit(aiAudit) {
    const aiAuditSection = document.getElementById("ai-audit-section");
    if (!aiAudit || !aiAudit.risk_level) {
        aiAuditSection.classList.add("d-none");
        return;
    }

    aiAuditSection.classList.remove("d-none");

    // Risk level styling
    const riskBadge = document.getElementById("ai-risk-badge");
    riskBadge.textContent = `${aiAudit.risk_level} RISK`;
    riskBadge.className = `risk-badge ${aiAudit.risk_level}`;

    // Summary text
    document.getElementById("ai-summary").textContent = aiAudit.overall_summary || "N/A";

    // Strengths list
    const strengthsList = document.getElementById("ai-strengths");
    strengthsList.innerHTML = "";
    if (aiAudit.strengths && aiAudit.strengths.length > 0) {
        aiAudit.strengths.forEach(str => {
            const li = document.createElement("li");
            li.textContent = str;
            strengthsList.appendChild(li);
        });
    } else {
        strengthsList.innerHTML = "<li>No specific strengths highlighted.</li>";
    }

    // Concerns list
    const concernsList = document.getElementById("ai-concerns");
    concernsList.innerHTML = "";
    if (aiAudit.concerns && aiAudit.concerns.length > 0) {
        aiAudit.concerns.forEach(con => {
            const li = document.createElement("li");
            li.textContent = con;
            concernsList.appendChild(li);
        });
    } else {
        concernsList.innerHTML = "<li>No specific concerns flagged.</li>";
    }

    // Suspicious Activity list
    const suspiciousList = document.getElementById("ai-suspicious");
    suspiciousList.innerHTML = "";
    if (aiAudit.suspicious_activity && aiAudit.suspicious_activity.length > 0) {
        aiAudit.suspicious_activity.forEach(act => {
            const li = document.createElement("li");
            li.textContent = act;
            suspiciousList.appendChild(li);
        });
    } else {
        suspiciousList.innerHTML = "<li>No suspicious activity detected.</li>";
    }

    // Actionable Recommendations list
    const recsList = document.getElementById("ai-recommendations");
    recsList.innerHTML = "";
    if (aiAudit.recommendations && aiAudit.recommendations.length > 0) {
        aiAudit.recommendations.forEach(rec => {
            const li = document.createElement("li");
            li.textContent = rec;
            recsList.appendChild(li);
        });
    } else {
        recsList.innerHTML = "<li>No recommendations generated.</li>";
    }

    // Final Verdict
    document.getElementById("ai-verdict").textContent = aiAudit.final_verdict || "N/A";
}

// Trigger AI Audit on button click
runAuditBtn.addEventListener("click", async () => {
    runAuditBtn.disabled = true;
    runAuditBtn.classList.add("d-none");
    auditProgress.classList.remove("d-none");

    try {
        const response = await fetch(`${BASE_URL}/statements/${statementId}/audit/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${accessToken}`
            }
        });

        if (!response.ok) {
            const errData = await response.json();
            alert(`AI Audit run failed: ${errData.error || response.statusText}`);
            runAuditBtn.disabled = false;
            runAuditBtn.classList.remove("d-none");
            auditProgress.classList.add("d-none");
            return;
        }

        // Successfully completed audit, fetch details again to reload layout
        await fetchStatementDetails();
        
        // Hide loader & restore button
        runAuditBtn.disabled = false;
        runAuditBtn.classList.remove("d-none");
        auditProgress.classList.add("d-none");

        // Scroll to the audit section for immediate visual feedback
        document.getElementById("ai-audit-section").scrollIntoView({ behavior: "smooth" });

    } catch (error) {
        console.error(error);
        alert("Server error occurred while executing AI Audit.");
        runAuditBtn.disabled = false;
        runAuditBtn.classList.remove("d-none");
        auditProgress.classList.add("d-none");
    }
});

// Initialization
fetchStatementDetails();
