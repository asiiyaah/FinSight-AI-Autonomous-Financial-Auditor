# FinSight - AI-Powered Financial Statement Auditing Platform

FinSight is a secure, AI-powered financial statement analysis and auditing platform. It leverages **Django REST Framework** (backend), **Vanilla HTML/CSS/JS** (frontend), and **Google Gemini AI** to extract transactions, perform deterministic audit checks, and generate professional, structured financial audit reports.

---

## 🌟 Key Features (Implemented)

### 1. Secure Authentication & Onboarding
- **JWT Token Authentication:** Secure register, login, and token-refresh cycle (Access & Refresh tokens) using `Django REST Framework SimpleJWT`.
- **Dynamic Onboarding:** Smart frontend dashboard detects whether the signed-in user is new or returning. New users see a visual onboarding prompt to upload their first statement, while returning users see their analysis statistics.

### 2. Secure Bank Statement Upload
- **Premium Drag & Drop Zone:** Interactive upload container with smooth transitions and glow outlines when dragging a PDF.
- **Visual Upload Feedback:** Progress loaders disable upload buttons and display spinners during file parsing to block double submissions.

### 3. PII Sensitive Data Redaction (Privacy First)
- **Local Sanitizer:** Extracted raw PDF text is sanitized **locally** on the server before transmitting it to external APIs.
- **PII Filters:** Uses regex logic to redact:
  - Account/Card Numbers (9-18 digits) ➔ `[ACCOUNT_REDACTED]`
  - Indian Aadhaar & PAN Cards ➔ `[AADHAAR_REDACTED]`, `[PAN_REDACTED]`
  - Customer/Holder Names in document headers ➔ `[NAME_REDACTED]`
  - Email addresses & Phone numbers ➔ `[EMAIL_REDACTED]`, `[PHONE_REDACTED]`
  - Bank branch codes (IFSC) ➔ `[IFSC_REDACTED]`

### 4. Interactive Statement Details Dashboard
- **Layer A: Deterministic Financial Analytics (Local & Free):**
  - **Cashflow Summaries:** Automatically aggregates total credit (income), total debit (spending), net savings, and savings rates formatted in Indian Rupees (`₹`).
  - **Category Breakdown:** Groups spending by category and paints dynamic percentage progress bars.
  - **Heuristic Risk Detectors:** Automatically flags statistical spending anomalies (threshold-based), duplicate charges, monthly subscription bills, and recurring loan EMIs.
- **Layer B: AI Audit Analysis (Gemini API):**
  - Structured audit summaries generated on-demand by **Gemini** (using `gemini-2.5-flash` with a strict JSON Pydantic schema).
  - Categorizes insights into risk levels (**LOW**, **MODERATE**, or **HIGH**) with matching glow badges, strengths, critical concerns, suspicious transactions, and actionable financial advice.

### 5. Local Developer Mock Bypasses
- Integrates `MOCK_PARSER` and `MOCK_AUDIT` environment options. If enabled (or if no API key is set), the backend generates rich synthetic transaction sets and structured audits instantly. This saves Gemini API token usage during local frontend/layout testing.

---

## 🛠️ Technology Stack
- **Backend:** Django, Django REST Framework, SimpleJWT, PDFPlumber, Pandas, Google GenAI SDK.
- **Frontend:** Vanilla HTML5, Vanilla CSS3 (custom variables, glassmorphism dark-theme), JavaScript ES6 (Fetch API), Bootstrap 5.
- **Database:** SQLite (Development).

---

## 🚀 Running Locally

### 1. Run the Backend API
Navigate to the root directory, activate your virtual environment, and run the Django dev server:
```bash
cd FinSight
source venv/bin/activate
python manage.py runserver
```
*(Runs on **http://127.0.0.1:8000**)*

### 2. Run the Static Frontend
In a second terminal window, navigate to the folder, activate your environment, and serve the frontend:
```bash
cd FinSight
source venv/bin/activate
python3 -m http.server 8080 --directory frontend
```
*(Runs on **http://localhost:8080**)*

Open **[http://localhost:8080/index.html](http://localhost:8080/index.html)** in your browser to log in and upload a PDF!

---

## 📅 Roadmap (Upcoming Features)

- **💬 Conversational RAG Chatbot:** Ask questions directly to your bank statement (e.g., *"How much did I spend on Swiggy in March?"*, *"Why was my risk rating Moderate?"*) using vector search databases and RAG (Retrieval-Augmented Generation) templates.
- **📊 Comparative Analysis:** Upload multiple months of statements and view comparative trend graphs of cashflow histories over quarters.
- **📄 Exportable PDF Compliance Reports:** Download signed financial audit reports for tax validation and personal accounting.
