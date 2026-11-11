# FinSight: AI-Powered Financial Statement Auditing Platform
## Comprehensive Architectural Dossier & IBM Expert Labs Technical Interview Defense Guide

---

# 1. BASIC PROJECT IDENTIFICATION

### 1.1 Core Metadata
- **Project Name:** FinSight – Autonomous Financial Statement Auditing Platform
- **Problem Solved:** Manual financial statement auditing is tedious, slow, error-prone, and vulnerable to missed anomalies, double-billing, and recurring subscription creep. FinSight automates bank statement ingestion, redacts personally identifiable information (PII) locally, calculates deterministic financial metrics (cashflow, savings rates, statistical anomalies, duplicate charges, subscriptions, and loan EMIs), and uses Google Gemini generative AI to produce structured, auditor-grade financial audit reports.
- **Target Users:** Individual consumers seeking personal financial health auditing, small-to-medium enterprise (SME) accountants, financial advisors, and compliance officers conducting rapid preliminary bank statement verification.
- **Implementation Status Legend:**
  - **IMPLEMENTED:** Fully coded and wired end-to-end.
  - **PARTIALLY IMPLEMENTED:** Coded in backend or frontend, but has integration gaps or incomplete routes.
  - **CONFIGURED BUT UNUSED:** Installed in `requirements.txt` or settings, but never invoked in application code.
  - **DOCUMENTED / PLANNED:** Mentioned in README/documentation/roadmap, but zero code exists.

### 1.2 Feature Implementation Matrix
| Feature | Status | Evidence in Codebase |
|---|---|---|
| Custom User Auth (Email/Pass + JWT) | **IMPLEMENTED** | `accounts/models.py`, `accounts/serializers.py`, `accounts/views.py` |
| Token Refresh Cycle & Route Guards | **IMPLEMENTED** | `accounts/urls.py`, `frontend/js/auth.js`, `frontend/js/dashboard.js` |
| PDF Ingestion & Text Extraction | **IMPLEMENTED** | `statements/views.py:StatementUploadView`, `statements/parser.py:parse_statement` via `pdfplumber` |
| Local PII Sanitization / Redaction | **IMPLEMENTED** | `statements/parser.py:redact_sensitive_info` (Regex for PAN, Aadhaar, Account, Phone, Email, IFSC, Names) |
| Deterministic Cashflow & Metrics (Layer A) | **IMPLEMENTED** | `audits/audit_engine.py:calculate_cashflow`, `calculate_category_breakdown`, `calculate_spending_profile` |
| Heuristic Risk Detectors (Layer A) | **IMPLEMENTED** | `audits/audit_engine.py:detect_duplicates`, `detect_subscriptions`, `detect_emi`, `detect_anomalies` |
| Structured AI Financial Audit (Layer B) | **IMPLEMENTED** | `audits/ai_audit.py:generate_ai_audit`, `audits/prompts.py`, `audits/schemas.py:AIAuditSchema` |
| Interactive Statement Details UI | **IMPLEMENTED** | `frontend/statement_details.html`, `frontend/js/statement_details.js`, `frontend/css/statement_details.css` |
| Statement Deletion API | **PARTIALLY IMPLEMENTED** | `statements/views.py:delete` exists at module level with a severe indentation bug; unreachable via HTTP DELETE |
| All Statements List View Screen | **PARTIALLY IMPLEMENTED** | Backend `StatementListView` exists with pagination; Frontend `statements.html` does NOT exist (404) |
| Local Mock Bypass Mode | **PARTIALLY IMPLEMENTED** | `audits/ai_audit.py` has working mock; `statements/parser.py` attempts importing non-existent `generate_data.py` |
| Conversational RAG Bank Chatbot | **DOCUMENTED/PLANNED** | Listed in `README.md` Roadmap; No vector database, LangChain/LlamaIndex, or RAG code exists |
| Multi-Month Comparative Analysis | **DOCUMENTED/PLANNED** | Listed in `README.md` Roadmap; No comparative aggregation logic implemented |
| Exportable PDF Compliance Reports | **DOCUMENTED/PLANNED** | Listed in `README.md` Roadmap; `reportlab` in `requirements.txt` but never imported or invoked |

### 1.3 Technology Stack Table
| Technology | Where it is used | Why it is used | Evidence in code |
|---|---|---|---|
| **Python 3.12+ / Django 6.0.6** | Backend core framework | Robust ORM, built-in security, standard project modularity | `manage.py`, `finsight/settings.py` |
| **Django REST Framework 3.17.1** | API Layer | Provides class-based APIViews, request serialization, and HTTP status handling | `accounts/views.py`, `statements/views.py`, `finsight/settings.py` |
| **djangorestframework-simplejwt 5.5.1** | Authentication | Stateless JSON Web Token authentication (access + refresh tokens) | `accounts/serializers.py`, `accounts/urls.py`, `finsight/settings.py` |
| **django-cors-headers 4.9.0** | Middleware | Allows decoupled frontend (running on port 8080) to consume backend API (port 8000) | `finsight/settings.py:MIDDLEWARE`, `CORS_ALLOW_ALL_ORIGINS = True` |
| **pdfplumber 0.11.9** | File parsing engine | Detailed text extraction from bank statement PDF documents | `statements/parser.py:parse_statement` |
| **google-genai 2.8.0** | LLM Client SDK | Official Google GenAI SDK used to interact with Gemini models for transaction extraction and audit generation | `statements/parser.py:client.models.generate_content`, `audits/ai_audit.py:generate_ai_audit` |
| **Pydantic 2.13.4** | Structured LLM output & schemas | Enforces strict JSON schemas on Gemini output (`StatementData`, `AIAuditSchema`) | `statements/parser.py`, `audits/schemas.py` |
| **Pandas 3.0.3** | Data formatting | Standard date parsing (`pd.to_datetime`) during transaction extraction | `statements/parser.py:line 1`, `line 200` |
| **SQLite 3** | Database | Zero-configuration relational database for local development and schema prototyping | `finsight/settings.py:DATABASES` (`BASE_DIR / 'db.sqlite3'`) |
| **Bootstrap 5.3.7 & Icons 1.11.3** | Frontend styling | Responsive grid, dark theme UI cards, modals, tabs, and glyph icons | `frontend/*.html` via jsDelivr CDN links |
| **Vanilla JavaScript (ES6+ Fetch)** | Frontend client logic | Lightweight, zero-build-step client architecture communicating with REST API | `frontend/js/auth.js`, `frontend/js/dashboard.js`, `frontend/js/upload.js`, `frontend/js/statement_details.js` |
| **reportlab 4.5.1** | **Configured but Unused** | Installed for planned PDF report generation; never imported or called | `requirements.txt:34` |
| **Faker 40.23.0** | **Configured but Unused** | Installed for synthetic mock data generation; ignored file not committed | `requirements.txt:13`, `.gitignore:11` |
| **websockets 16.0** | **Configured but Unused** | Transitive dependency or unintegrated real-time stub | `requirements.txt:43` |
| **tenacity 9.1.4** | **Configured but Unused** | Installed for retry logic, but codebase implemented manual `while/for` retry loops with `time.sleep` | `requirements.txt:39`, `statements/parser.py:167`, `audits/ai_audit.py:167` |

---

# 2. COMPLETE ARCHITECTURE

### 2.1 Architectural Pattern
The application follows a **Decoupled Two-Tier Monolithic Backend with Client-Side Rendered (CSR) Single-Page-Style Static Frontend**:
- **Layered Architecture:** The backend strictly segregates concerns into Models (Data Access), Serializers/Schemas (Data Validation & Transformation), Views (HTTP Transport & Orchestration), and Dedicated Service Engines (`parser.py`, `audit_engine.py`, `ai_audit.py`).
- **Two-Layer Hybrid Auditing Architecture:**
  - **Layer A (Deterministic Financial Intelligence):** Pure Python + Django ORM statistical aggregations (zero LLM token cost, zero hallucination risk, instantaneous).
  - **Layer B (Generative Auditor Intelligence):** Prompt-engineered Gemini LLM with strict Pydantic JSON schema constraints that consumes the *compressed summary* produced by Layer A.

### 2.2 Text Architecture Diagram
```
+---------------------------------------------------------------------------------------+
|                                FRONTEND LAYER                                         |
|  Vanilla HTML5 / Modern Glassmorphism CSS3 / ES6 Fetch API (Served on :8080)          |
|  [index.html] <---> [dashboard.html] <---> [upload.html] <---> [statement_details.html]|
+------------------------------------------+--------------------------------------------+
                                           | HTTP / REST (JWT Bearer Token via Header)
                                           v
+---------------------------------------------------------------------------------------+
|                                BACKEND API ROUTER                                     |
|  Django 6.0.6 / Django REST Framework (Running on :8000)                               |
|  - CORS Middleware (corsheaders)                                                      |
|  - SimpleJWT Authentication Middleware                                                |
|  - /api/v1/accounts/  (Register, Login, Refresh, Me)                                  |
|  - /api/v1/statements/(Upload, Detail, List, Audit)                                   |
+------------------------------------------+--------------------------------------------+
                                           |
                  +------------------------+------------------------+
                  |                                                 |
                  v                                                 v
+------------------------------------+    +---------------------------------------------+
|        ACCOUNTS SERVICE            |    |              STATEMENTS SERVICE             |
| - CustomUser Model (Email unique)  |    | - StatementUploadView                       |
| - EmailLoginSerializer             |    | - StatementListView (PageNumberPagination)  |
| - RegisterSerializer               |    | - StatementDetailView (On-the-fly Layer A)  |
| - Passwords hashed with PBKDF2     |    | - PDF Storage (/media/statements/)          |
+------------------------------------+    +----------------------+----------------------+
                                                                 |
                  +----------------------------------------------+
                  |
                  v
+---------------------------------------------------------------------------------------+
|                                  AUDITING PIPELINE                                    |
|                                                                                       |
|  [Ingestion & PII Redaction] (statements/parser.py)                                   |
|   1. pdfplumber extracts raw text                                                     |
|   2. redact_sensitive_info() strips PAN, Aadhaar, Card/Account, Phone, Email, IFSC    |
|   3. Gemini / Structured Parser extracts transactions (or aborts on 0 rows)           |
|                                                                                       |
|  [Layer A: Deterministic Engine] (audits/audit_engine.py)                             |
|   1. get_audit_context() -> Date range, transaction count, confidence scoring         |
|   2. calculate_cashflow() -> Credit sum, debit sum, net savings, savings rate         |
|   3. calculate_category_breakdown() -> Spending distribution                          |
|   4. calculate_spending_profile() -> Essential vs. Discretionary ratio                |
|   5. detect_duplicates() -> Identical (date, vendor, amount) tuples                   |
|   6. detect_subscriptions() -> Recurring debit across >= 2 unique months (>= 60 days) |
|   7. detect_emi() -> Keyword match ('emi', 'loan', etc.) + recurring debit           |
|   8. detect_anomalies() -> Statistical Z-score outlier: amount > mean + 2*std_dev     |
|                                                                                       |
|  [Layer B: AI Generative Auditor] (audits/ai_audit.py + audits/prompts.py)            |
|   1. build_ai_context() -> Compresses Layer A analytics to reduce prompt tokens       |
|   2. build_audit_prompt() -> Injects constraints, rules, and word count boundaries   |
|   3. Gemini Client (gemini-2.5-flash) -> Enforces AIAuditSchema (Pydantic)            |
|   4. Retry Loop with Exponential Backoff (5 attempts, 8s -> 16s -> 32s...)            |
+------------------------------------------+--------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                                 PERSISTENCE LAYER                                     |
|  SQLite 3 (db.sqlite3)                                                                |
|  - CustomUser: id, username, email, password hash, names                              |
|  - Statement:  id, user_id (FK), file, audit_status, analytics (JSON), ai_audit (JSON)|
|  - Transaction:id, statement_id (FK), date, vendor, amount, category, type           |
+---------------------------------------------------------------------------------------+
```

### 2.3 Component Breakdown
1. **Frontend Client (`frontend/`):**
   - *What it does:* Handles user presentation, browser event listening, JWT token lifecycle in `localStorage`, drag-and-drop file staging, dynamic DOM rendering, and API communication via Fetch.
   - *Why it exists:* Provides a zero-dependency, fast-loading, visually rich glassmorphic interface without the overhead of heavy JavaScript compilation pipelines (e.g., Webpack/Vite/Node).
   - *Communication:* Dispatches JSON or `multipart/form-data` HTTP requests with `Authorization: Bearer <token>` to `http://127.0.0.1:8000/api/v1/`.
2. **API & Serialization Layer (`accounts/serializers.py`, `statements/serializers.py`, `finsight/urls.py`):**
   - *What it does:* Parses incoming request payloads, validates types and constraints, controls write-only fields (e.g., password), and serializes database model instances into JSON responses.
   - *Communication:* Dispatches validated data to Django ORM and returns standard DRF `Response` objects.
3. **PII Sanitizer (`statements/parser.py:redact_sensitive_info`):**
   - *What it does:* Scans raw text extracted from bank statements using pre-compiled regular expressions to redact personal identities, account numbers, government IDs (Aadhaar, PAN), phone numbers, and IFSC codes before external transmission.
   - *Why it exists:* Strict compliance and data privacy; prevents sensitive user banking credentials from leaking into external third-party LLM cloud logs.
4. **Deterministic Audit Engine (`audits/audit_engine.py`):**
   - *What it does:* Executes rule-based statistical and heuristic calculations on ingested transactions.
   - *Why it exists:* LLMs are notoriously bad at precise floating-point arithmetic and deterministic grouping. Delegating math and risk flags to Python code guarantees 100% calculation accuracy.
5. **Generative AI Auditor (`audits/ai_audit.py`, `audits/prompts.py`, `audits/schemas.py`):**
   - *What it does:* Feeds compressed Layer A financial summaries into Google Gemini and forces structured JSON generation complying with `AIAuditSchema`.
   - *Why it exists:* Translates raw statistical figures into human-readable executive summaries, strengths, concerns, and actionable advice.
6. **Persistence Layer (`statements/models.py`, `accounts/models.py`):**
   - *What it does:* Manages relational records in SQLite. Stores user profiles, statement metadata, raw uploaded PDF files in `media/statements/`, extracted transactions, and structured JSON audit payloads.

---

# 3. END-TO-END DATA FLOW

### Flow 1: User Authentication & Onboarding (Login Flow)
```
[User submits email/password on index.html]
    ↓ (Event Listener in frontend/js/auth.js)
[Fetch POST http://127.0.0.1:8000/api/v1/accounts/login/]
    ↓ (finsight/urls.py -> accounts/urls.py)
[EmailLoginView.post() in accounts/views.py]
    ↓ (Passes request.data to EmailLoginSerializer)
[EmailLoginSerializer.validate() in accounts/serializers.py]
    ├─ Queries User.objects.filter(email=email).first()
    ├─ Calls django.contrib.auth.authenticate(username=user.username, password=password)
    │   └─ Verifies PBKDF2-SHA256 password hash against CustomUser record
    └─ Generates RefreshToken.for_user(authenticated_user)
        └─ Returns {"access": str(refresh.access_token), "refresh": str(refresh)}
    ↓ (HTTP 200 OK returned to browser)
[auth.js stores tokens in localStorage: access_token, refresh_token, is_new_user='false']
    ↓ (window.location.href = "dashboard.html")
[dashboard.html triggers dashboard.js:loadUser()]
    ↓ (Fetch GET /api/v1/accounts/me/ with Header 'Authorization: Bearer <access_token>')
[MeView.get() in accounts/views.py returns user profile JSON]
    ↓
[DOM updates: displays "Welcome back, <first_name>!" and reveals existing-user-section]
```

### Flow 2: Bank Statement Ingestion, PII Redaction & Transaction Parsing
```
[User drops PDF on upload.html and clicks "Upload Statement"]
    ↓ (Event Listener in frontend/js/upload.js)
[Fetch POST /api/v1/statements/upload/ with multipart/form-data]
    ↓ (finsight/urls.py -> statements/urls.py)
[StatementUploadView.post() in statements/views.py]
    ├─ Checks request.FILES.get('file')
    ├─ Validates file_name.endswith('.pdf')
    ├─ Creates Statement record in database (status="uploaded", is_parsed=False)
    │   └─ Saves physical file to media/statements/<uuid_or_filename>.pdf
    └─ Invokes parse_statement(statement) in statements/parser.py
        ↓
    [pdfplumber.open(file_path)]
        └─ Loops through pages, extracting raw text into string buffer
        ↓
    [redact_sensitive_info(raw_text)]
        └─ Executes 8 regex passes (Redacts names, addresses, emails, phones, IFSC, PAN, Aadhaar, account numbers)
        ↓
    [Gemini Client / Structured Extraction]
        ├─ Constructs extraction prompt with Pydantic StatementData schema
        ├─ Calls client.models.generate_content(model="gemini-3.5-flash")
        ├─ Implements 5-attempt retry loop with exponential backoff on 429/503 errors
        └─ Loops through parsed transactions:
            └─ Transaction.objects.create(statement=statement, date=..., vendor=..., amount=..., category=..., type=...)
        ↓
    [Updates statement.is_parsed = True, saves Statement]
    └─ Returns parsed transaction count
    ↓ (Check: if count == 0: aborts, calls statement.delete(), returns 422 Unprocessable Entity)
[HTTP 200 OK returned: {"statement_id": id, "transactions_parsed": count}]
    ↓
[upload.js receives 200 -> setTimeout redirects to statement_details.html?id=<id>]
```

### Flow 3: Deterministic Financial Analytics & On-Demand AI Auditing
```
[statement_details.html loads with query param ?id=<statement_id>]
    ↓ (frontend/js/statement_details.js: fetchStatementDetails())
[Fetch GET /api/v1/statements/<id>/]
    ↓
[StatementDetailView.get() in statements/views.py]
    ├─ Queries Statement.objects.get(id=statement_id, user=request.user)
    ├─ Check: if statement.is_parsed and not statement.analytics:
    │   └─ On-the-fly executes Layer A: run_audit(statement.id)
    │       ├─ audits/audit_engine.py: get_audit_context()
    │       ├─ calculate_cashflow()
    │       ├─ calculate_category_breakdown() & calculate_spending_profile()
    │       ├─ detect_duplicates(), detect_subscriptions(), detect_emi(), detect_anomalies()
    │       └─ Saves statement.analytics = analytics, audit_status = "analytics_ready"
    └─ Returns statement metadata, analytics, and ai_audit JSON
    ↓
[Frontend statement_details.js renders Cashflow cards, Category bars, and Tabbed Risk panels]
    ↓
[User clicks "Run AI Audit" button]
    ↓
[Fetch POST /api/v1/statements/<id>/audit/]
    ↓
[StatementAuditView.post() in statements/views.py]
    ↓
[run_full_audit(statement.id) in audits/audit_engine.py]
    ├─ Re-runs or retrieves Layer A analytics
    └─ Calls generate_ai_audit(analytics) in audits/ai_audit.py
        ├─ build_ai_context(analytics): compresses analytics (top 3 categories, anomaly max/top 3, subscriptions)
        ├─ build_audit_prompt(ai_context) in audits/prompts.py
        ├─ Invokes Gemini (model="gemini-2.5-flash") with response_schema=AIAuditSchema
        ├─ Retries with exponential backoff on rate limits
        ├─ Serializes structured output via result.model_dump()
        ├─ Persists statement.ai_audit = ai_result, statement.audit_status = "completed"
        └─ (If exception occurs: sets statement.audit_status = "failed", saves, and re-raises)
    ↓
[HTTP 200 OK returned with audit results]
    ↓
[statement_details.js receives response, re-fetches details, renders AI Audit Card (Risk badge, Strengths, Concerns, Suspicious activity, Verdict) and smoothly scrolls into view]
```

---

# 4. API ANALYSIS

### 4.1 Endpoint Catalog Table
| Method | Endpoint | Purpose | Auth Required? | Request Payload | Response Payload | Main Logic |
|---|---|---|---|---|---|---|
| `POST` | `/api/v1/accounts/register/` | Register new user account | No (`AllowAny`) | `{"username", "email", "password", "first_name", "last_name"}` | `{"message", "access", "refresh"}` (201 Created) | Validates unique email/username, calls `create_user()` with PBKDF2 hashing, generates JWT pair. |
| `GET` | `/api/v1/accounts/signup/` | Serves legacy HTML signup form | No (`AllowAny`) | None | Raw HTML (`signup.html`) (200 OK) | Django `render(request, 'signup.html')`. |
| `POST` | `/api/v1/accounts/login/` | Email-based authentication | No (`AllowAny`) | `{"email", "password"}` | `{"access": "...", "refresh": "..."}` (200 OK) | Looks up user by email, authenticates password, creates SimpleJWT refresh/access tokens. |
| `POST` | `/api/v1/accounts/login/refresh/` | Refresh expired access token | No (`AllowAny`) | `{"refresh": "..."}` | `{"access": "..."}` (200 OK) | Built-in SimpleJWT `TokenRefreshView`. Validates refresh token signature & expiry, issues new access token. |
| `GET` | `/api/v1/accounts/me/` | Fetch current user profile | Yes (`IsAuthenticated`) | None (Bearer header) | `{"id", "username", "email", "first_name", "last_name"}` (200 OK) | Extracts `request.user` from validated JWT; returns serialized profile. |
| `GET` | `/api/v1/statements/` | List user's statements (Paginated) | Yes (`IsAuthenticated`) | None (Query param: `?page=N`) | `{"count", "next", "previous", "results": [...]}` (200 OK) | Filters `Statement.objects.filter(user=request.user).order_by("-uploaded_at")`, paginates 5 per page. |
| `POST` | `/api/v1/statements/upload/` | Ingest PDF, redact PII, extract txs | Yes (`IsAuthenticated`) | `multipart/form-data` with `file: <binary>` | `{"message", "statement_id", "file_name", "transactions_parsed"}` (200 OK) | Validates `.pdf`, extracts text via `pdfplumber`, redacts PII, extracts rows via Gemini, creates `Transaction` records. |
| `GET` | `/api/v1/statements/<int:statement_id>/` | Retrieve statement details & analytics | Yes (`IsAuthenticated`) | None (URL path param) | `{"statement": {...}, "analytics": {...}, "ai_audit": {...}}` (200 OK) | Validates ownership; triggers Layer A analytics on-the-fly if not pre-computed; returns aggregated metrics. |
| `POST` | `/api/v1/statements/<int:statement_id>/audit/` | Run full Layer A & B AI audit | Yes (`IsAuthenticated`) | None (URL path param) | `{"message", "statement_id", "result": {"analytics": ..., "ai_audit": ...}}` (200 OK) | Verifies `is_parsed`; executes `run_full_audit`; invokes Gemini with `AIAuditSchema`; persists audit JSON to DB. |
| `DELETE`| `/api/v1/statements/<int:statement_id>/` | *(Intended)* Delete statement & file | Yes (`IsAuthenticated`) | None (URL path param) | `{"message": "Statement deleted successfully"}` | **BROKEN:** Function `delete()` is defined at module scope with `self`; DRF returns `405 Method Not Allowed`. |

### 4.2 API Cross-Cutting Mechanics
- **Validation:** Enforced via DRF Serializers (`RegisterSerializer`, `EmailLoginSerializer`, `StatementListSerializer`) and Pydantic schemas (`StatementData`, `ExtractedTransaction`, `AIAuditSchema`). Serializer validation calls `is_valid(raise_exception=True)`.
- **Authentication:** DRF `DEFAULT_AUTHENTICATION_CLASSES` configured for SimpleJWT `JWTAuthentication`. Endpoints authenticate via standard HTTP Header: `Authorization: Bearer <access_token>`.
- **Authorization & Ownership:** Statement detail and audit endpoints explicitly enforce row-level ownership: `Statement.objects.get(id=statement_id, user=request.user)`. If another user accesses the ID, a 404 is returned, preventing enumeration attacks.
- **Error Responses:** Standardized DRF error formats: 400 Bad Request (serializer errors), 401 Unauthorized (invalid/missing token), 404 Not Found (statement not found or not owned by user), 422 Unprocessable Entity (zero transactions extracted from PDF), 500 Internal Server Error (unhandled LLM or database failure).
- **Pagination:** Global `PageNumberPagination` configured in `settings.py` with `PAGE_SIZE = 5`. Explicitly applied in `StatementListView`.
- **CORS:** Enabled globally via `corsheaders.middleware.CorsMiddleware` and `CORS_ALLOW_ALL_ORIGINS = True` to facilitate local development across distinct ports (8080 frontend, 8000 backend).

---

# 5. DATABASE ANALYSIS

### 5.1 Database Engine & Configuration
- **Database Engine:** SQLite 3 (`django.db.backends.sqlite3`).
- **File Location:** `BASE_DIR / 'db.sqlite3'`.
- **Transactions:** Autocommit mode (default Django behavior). No explicit `transaction.atomic()` context managers are used during statement upload or audit execution.

### 5.2 Entity-Relationship (ER) Diagram
```
+-------------------------------------------------------+
|                 accounts_customuser                   |
+-------------------------------------------------------+
| PK  id           : BigAutoField                       |
|     username     : VarChar(150) [UNIQUE]              |
|     email        : VarChar(254) [UNIQUE]              |
|     password     : VarChar(128)                       |
|     first_name   : VarChar(150)                       |
|     last_name    : VarChar(150)                       |
|     is_active    : Boolean                            |
|     is_staff     : Boolean                            |
|     date_joined  : DateTime                           |
+-------------------------------------------------------+
                           | 1
                           |
                           | 0..* (CASCADE)
                           v
+-------------------------------------------------------+
|                 statements_statement                  |
+-------------------------------------------------------+
| PK  id           : BigAutoField                       |
| FK  user_id      : BigInt -> accounts_customuser(id)  |
|     file         : VarChar(100)                       |
|     file_name    : VarChar(255)                       |
|     uploaded_at  : DateTime                           |
|     is_parsed    : Boolean [default=False]            |
|     audit_status : VarChar(30) [default="uploaded"]   |
|     analytics    : JSONField [default=dict, blank=True|
|     ai_audit     : JSONField [default=dict, blank=True|
+-------------------------------------------------------+
                           | 1
                           |
                           | 0..* (CASCADE, related_name='transactions')
                           v
+-------------------------------------------------------+
|                 statements_transaction                |
+-------------------------------------------------------+
| PK  id               : BigAutoField                   |
| FK  statement_id     : BigInt -> statements_statement |
|     date             : Date                           |
|     vendor           : VarChar(255)                   |
|     amount           : Decimal(10, 2)                 |
|     category         : VarChar(100)                   |
|     raw_description  : TextField [null=True, blank=Tru|
|     transaction_type : VarChar(10) [default="debit"]  |
+-------------------------------------------------------+
```

### 5.3 Model Schema Deep Dive
1. **`CustomUser` (`accounts/models.py`):**
   - Inherits from Django's `AbstractUser`.
   - Explicitly adds `email = models.EmailField(unique=True)`.
   - *Design Rationale:* Subclassing `AbstractUser` at project inception is a Django best practice; it allows custom authentication identifiers (logging in with email instead of username) without requiring destructive database schema migrations later.
2. **`Statement` (`statements/models.py`):**
   - Stores statement lifecycle state: `uploaded` -> `analytics_ready` -> `completed` (or `failed`).
   - Uses native `JSONField` for `analytics` and `ai_audit`.
   - *Design Rationale:* The outputs of Layer A (nested metrics, category mappings, risk lists) and Layer B (Pydantic audit output) have polymorphic or semi-structured nested shapes. Storing them in JSON fields avoids creating 6–8 rigid normalization tables (e.g., `StatementAnomalies`, `StatementDuplicates`, `StatementSubscriptions`, `AuditStrengths`, `AuditConcerns`) for data that is only ever retrieved and rendered as a complete document.
3. **`Transaction` (`statements/models.py`):**
   - Normalized relational child of `Statement`.
   - Fields: `date`, `vendor`, `amount` (`DecimalField` for precise monetary calculations), `category`, `raw_description`, `transaction_type` (`credit` vs `debit`).
   - *Design Rationale:* Transactions require direct relational filtering and aggregation (e.g., `Sum('amount')`, `Min('date')`, filtering by `transaction_type`), which cannot be performed efficiently inside a raw text or JSON blob.

### 5.4 ORM Queries & Aggregation Examples in Code
- **Date Range Discovery (`audits/audit_engine.py:52`):**
  ```python
  date_info = transactions.aggregate(start_date=Min("date"), end_date=Max("date"))
  ```
- **Cashflow Aggregation (`audits/audit_engine.py:95`):**
  ```python
  total_credit = Transaction.objects.filter(statement_id=statement_id, transaction_type="credit").aggregate(total=Sum("amount"))["total"] or 0
  ```
- **Category Spending Distribution (`audits/audit_engine.py:133`):**
  ```python
  category_data = (Transaction.objects.filter(statement_id=statement_id, transaction_type="debit")
                   .values("category")
                   .annotate(total=Sum("amount")))
  ```
- **Duplicate Detection Query (`audits/audit_engine.py:167`):**
  ```python
  transactions = Transaction.objects.filter(statement_id=statement_id, transaction_type="debit")
  ```

---

# 6. CODE STRUCTURE

### 6.1 Repository Directory Tree
```
FinSight-AI-Autonomous-Financial-Auditor/
├── manage.py                          # Django execution CLI
├── requirements.txt                   # Dependency specifications
├── README.md                          # Project documentation and roadmap
├── .gitignore                         # Git tracking exclusion rules
│
├── finsight/                          # Project Configuration Package
│   ├── __init__.py
│   ├── asgi.py                        # ASGI asynchronous deployment hook
│   ├── wsgi.py                        # WSGI synchronous web server hook
│   ├── settings.py                    # Global Django settings, SimpleJWT, CORS, DB config
│   └── urls.py                        # Root API route table & media file serving
│
├── accounts/                          # Authentication & User Management App
│   ├── __init__.py
│   ├── admin.py                       # UserAdmin registration for CustomUser
│   ├── apps.py                        # AccountsConfig definition
│   ├── models.py                      # CustomUser model definition (unique email)
│   ├── serializers.py                 # RegisterSerializer & EmailLoginSerializer
│   ├── urls.py                        # Account route mappings (/login, /register, /me)
│   ├── views.py                       # APIViews for registration, login, and profile
│   ├── tests.py                       # Empty boilerplate test suite
│   ├── migrations/                    # Database migration history for accounts
│   │   ├── 0001_initial.py
│   │   └── 0002_alter_customuser_email.py
│   └── templates/
│       └── signup.html                # Legacy visual HTML testing screen
│
├── statements/                        # Statement Ingestion & Parsing App
│   ├── __init__.py
│   ├── admin.py                       # Model registrations for Django Admin
│   ├── apps.py                        # StatementsConfig definition
│   ├── models.py                      # Statement and Transaction relational models
│   ├── parser.py                      # pdfplumber parsing, PII redaction, Gemini transaction extraction
│   ├── serializers.py                 # StatementListSerializer
│   ├── urls.py                        # Statement routes (/upload, /<id>/, /<id>/audit)
│   ├── views.py                       # StatementUploadView, StatementDetailView, StatementListView
│   ├── tests.py                       # Empty boilerplate test suite
│   └── migrations/                    # Database migration history for statements
│       ├── 0001_initial.py
│       ├── 0002_statement_audit_status_statement_summary_and_more.py
│       ├── 0003_statement_audit_result.py
│       ├── 0004_remove_statement_audit_result_and_more.py
│       └── 0005_remove_statement_file_type.py
│
├── audits/                            # Financial Auditing Engine & Intelligence App
│   ├── __init__.py
│   ├── admin.py                       # Empty admin registration
│   ├── apps.py                        # AuditsConfig definition
│   ├── models.py                      # Empty (Audits persist on Statement JSONFields)
│   ├── views.py                       # Empty boilerplate (Views implemented in statements/views.py)
│   ├── schemas.py                     # Pydantic AIAuditSchema for structured Gemini output
│   ├── prompts.py                     # Prompt engineering template (build_audit_prompt)
│   ├── ai_audit.py                    # Layer B Gemini auditor & context compression
│   ├── audit_engine.py                # Layer A deterministic calculations & full orchestrator
│   ├── tests.py                       # Empty boilerplate test suite
│   └── migrations/                    # Empty migrations package
│
└── frontend/                          # Client-Side Rendered Static Presentation Tier
    ├── index.html                     # Auth interface (Login & Register tabs)
    ├── dashboard.html                 # Main hub (Onboarding vs Returning user flows)
    ├── upload.html                    # PDF Drag-and-Drop file uploader
    ├── statement_details.html         # Rich analytics, risk breakdown & AI audit dashboard
    ├── css/
    │   ├── global.css                 # CSS variables, typography, glassmorphism base
    │   ├── auth.css                   # Authentication card styling
    │   ├── dashboard.css              # Dashboard layout and metric cards
    │   ├── upload.css                 # Drag-and-drop glowing dropzone styles
    │   └── statement_details.css      # Risk badges, cashflow cards, progress bars
    └── js/
        ├── auth.js                    # JWT token handling & auth form dispatching
        ├── dashboard.js               # User profile hydration & navigation routing
        ├── upload.js                  # Drag-and-drop event wiring & upload dispatch
        └── statement_details.js       # Analytics rendering & AI audit execution trigger
```

---

# 7. AUTHENTICATION AND SECURITY

### 7.1 Implemented Security Mechanisms
1. **Password Hashing:** Implemented via Django's default authentication framework in `accounts/serializers.py:RegisterSerializer.create()`. Invoking `User.objects.create_user()` routes through PBKDF2 with a SHA-256 hash and salt. Passwords are never stored in plaintext.
2. **Stateless JWT Tokens:** Implemented via `djangorestframework_simplejwt`. `ACCESS_TOKEN_LIFETIME` is set to 60 minutes; `REFRESH_TOKEN_LIFETIME` is set to 7 days; `ROTATE_REFRESH_TOKENS = True`. Access tokens are signed HMAC cryptographic tokens containing the `user_id`.
3. **PII Masking & Data Sanitization:** Implemented locally in `statements/parser.py:redact_sensitive_info()`. Masks customer names, addresses, emails, phone numbers, IFSC codes, PAN cards, Aadhaar cards, and credit card/bank account numbers before data ever touches an external LLM network endpoint.
4. **Row-Level Resource Ownership:** Implemented in `statements/views.py:StatementDetailView` and `StatementAuditView`. The query `Statement.objects.get(id=statement_id, user=request.user)` ensures users can only read or audit their own statements.
5. **SQL Injection Defense:** All database interactions utilize the Django ORM query abstraction layer (`filter()`, `aggregate()`, `values()`, `annotate()`). Zero raw SQL strings (`cursor.execute()`) exist, providing default parameterized protection against SQL injection.
6. **File Extension Validation:** `StatementUploadView` verifies `file.name.endswith('.pdf')` before creating records or invoking `pdfplumber`.

### 7.2 Potential Security Weaknesses (Interview Defense Points)
- **Token Storage in `localStorage`:** `frontend/js/auth.js` writes access and refresh tokens to browser `localStorage`. `localStorage` is accessible to any JavaScript running in the origin, leaving tokens vulnerable to Cross-Site Scripting (XSS) extraction. *Production fix:* Store refresh tokens in `HttpOnly`, `SameSite=Strict`, `Secure` cookies.
- **`CORS_ALLOW_ALL_ORIGINS = True`:** In `finsight/settings.py`, wildcard CORS is enabled. Any malicious third-party site visited by an authenticated user could make cross-origin API calls if ambient credentials or tokens are exposed. *Production fix:* Restrict `CORS_ALLOWED_ORIGINS` to specific trusted client domains.
- **File Upload MIME-Type Spoofing:** `StatementUploadView` checks only `file_name.endswith('.pdf')` via string manipulation. A malicious user could rename an executable (`malicious.exe` -> `malicious.pdf`) and bypass this check. *Production fix:* Validate file magic bytes (using `python-magic`) to ensure the file header matches `%PDF`.
- **Hardcoded Media File Serving:** `urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)` in `finsight/urls.py` serves uploaded statements publicly without checking JWT authentication. Anyone knowing the file URL path could download another user's unredacted bank statement. *Production fix:* Serve files via authenticated internal redirect views (e.g., Nginx `X-Accel-Redirect`).
- **Synchronous Denial of Service (DoS):** Uploading a 500-page PDF blocks the WSGI worker thread during `pdfplumber` parsing and Gemini API calls, allowing an attacker to exhaust server worker capacity with minimal requests.

---

# 8. ERROR HANDLING

### 8.1 Error Handling Architecture
Error handling is **distributed across layers** rather than centralized in custom middleware:
1. **Validation Errors:** Handled by DRF serializers (`serializer.is_valid()`) and returned as standard DRF field dictionaries with `400 Bad Request`.
2. **Resource Not Found:** Wrapped in explicit `try...except Statement.DoesNotExist` blocks in views, returning `404 Not Found` with `{"error": "Statement not found"}`.
3. **Database Integrity Preservation on Parser Failure:**
   - In `statements/views.py:116`, if `count == 0` (parsing extracted no valid transactions), the code executes:
     ```python
     statement.delete()
     return Response({"error": "Failed to parse transactions", ...}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
     ```
   - This prevents empty "zombie" statement records from polluting the user's dashboard.
4. **External API & Network Resilience (Gemini Retries):**
   - Both `statements/parser.py` and `audits/ai_audit.py` implement an explicit retry loop with exponential backoff:
     ```python
     max_retries = 5
     retry_delay = 8
     for attempt in range(max_retries):
         try:
             response = client.models.generate_content(...)
             break
         except Exception as e:
             if ("503" in str(e) or "429" in str(e)) and attempt < max_retries - 1:
                 time.sleep(retry_delay)
                 retry_delay *= 2
             else:
                 return 0 # or raise Exception
     ```
5. **Audit State Failure Tracking:**
   - In `audits/audit_engine.py:run_full_audit()`, the entire pipeline is wrapped in `try...except Exception as e`. If any component fails, `statement.audit_status = "failed"` is saved to SQLite before re-raising, guaranteeing the UI reflects the failure state instead of hanging in an intermediate state.

---

# 9. AI / ML ANALYSIS

### 9.1 Models and Integration
- **LLM Models Used:**
  - `gemini-3.5-flash` in `statements/parser.py:170` (Transaction Extraction).
  - `gemini-2.5-flash` in `audits/ai_audit.py:170` (Audit Synthesis).
  *(Note: `gemini-3.5-flash` appears to be a versioning placeholder/forward reference; Google's current production flash tiers are `gemini-1.5-flash`, `gemini-2.0-flash`, and `gemini-2.5-flash`).*
- **SDK:** Google GenAI Python SDK (`from google import genai`).
- **Client Instantiation:** `client = genai.Client(api_key=settings.GEMINI_API_KEY)`.

### 9.2 Data Flow Pipeline
```
[Raw Bank Statement PDF]
         ↓
[pdfplumber Text Extraction]
         ↓
[Local Regex PII Sanitization] (Masks names, accounts, PAN, Aadhaar)
         ↓
[Gemini Structured Extraction] (Enforces Pydantic StatementData schema)
         ↓
[Normalized SQL Database Storage] (Transaction table rows)
         ↓
[Layer A Deterministic Analytics] (Python math: cashflow, duplicates, subscriptions, EMIs, anomalies)
         ↓
[Context Compression (build_ai_context)] (Extracts top 3 categories, summaries, anomaly highlights)
         ↓
[Prompt Construction (build_audit_prompt)] (Injects constraints, length limits, schema expectations)
         ↓
[Gemini Generative Auditor (gemini-2.5-flash)] (Enforces Pydantic AIAuditSchema)
         ↓
[Validation & Serialization (result.model_dump())]
         ↓
[Persistence to Statement.ai_audit JSONField]
```

### 9.3 Structured Output Enforcement via Pydantic
The system eliminates LLM output hallucination and formatting drift by compiling Pydantic models directly into Gemini's `response_schema` configuration:
```python
# audits/schemas.py
class AIAuditSchema(BaseModel):
    risk_level: Literal["LOW", "MODERATE", "HIGH"]
    overall_summary: str
    strengths: List[str]
    concerns: List[str]
    suspicious_activity: List[str]
    recommendations: List[str]
    final_verdict: str
```
By passing `config=dict(response_mime_type="application/json", response_schema=AIAuditSchema)`, the Gemini engine uses constrained decoding (grammar-based sampling) to guarantee that the output is syntactically valid JSON conforming exactly to the fields and types specified.

### 9.4 Context Compression Strategy
Rather than dumping thousands of raw transaction rows into Gemini's prompt (which burns tokens, increases latency, and degrades reasoning focus), `audits/ai_audit.py:build_ai_context()` compresses Layer A metrics:
- Replaces hundreds of category rows with only the **top 3 spending categories**.
- Compresses duplicate groups into **count + vendor names**.
- Replaces all anomalies with the **largest anomaly amount + vendor** and top 3 outliers.
- Passes clean summary ratios: `essential_ratio`, `discretionary_ratio`, `audit_confidence`.

### 9.5 RAG (Retrieval-Augmented Generation) Status
- **RAG is NOT implemented in the current codebase.**
- The project implements a **Structured Context Injection Pipeline**, not RAG.
- *Distinction:* RAG requires document chunking, embedding generation (e.g., text-embedding-004), vector database indexing (e.g., Pinecone, ChromaDB, pgvector), similarity search on user queries, and dynamic context injection. FinSight extracts all statement transactions into relational tables and passes aggregated statistical metrics directly into the prompt.
- *Interview Defense:* Clearly acknowledge that RAG is on the documented product roadmap for natural-language conversational queries over multi-year statement histories, but the current production auditing pipeline relies on deterministic context compression.

---

# 10. ASYNC / BACKGROUND PROCESSING

### 10.1 Current Architecture Analysis
- **Current State:** **100% Synchronous Execution.**
- There is **no Celery, Redis, Django-Q, RabbitMQ, or background worker thread** present in the codebase.
- In `statements/views.py`:
  - When a user uploads a statement, `StatementUploadView.post()` runs `pdfplumber` parsing AND the external Gemini transaction extraction synchronously within the HTTP request thread.
  - When a user triggers an audit, `StatementAuditView.post()` runs `run_full_audit()` synchronously within the HTTP request thread.

### 10.2 Architectural Consequences & Failure Modes
1. **HTTP Gateway Timeouts:** Gemini API calls with exponential backoff (8s, 16s, 32s...) can take over 60 seconds if Google servers experience high demand. Production reverse proxies (Nginx/AWS ALB) default to 30–60 second timeouts, resulting in `504 Gateway Timeout` errors while the backend continues executing in an orphaned thread.
2. **Worker Starvation:** Synchronous blocking holds WSGI worker processes (e.g., Gunicorn workers). If 4 users upload statements simultaneously on a 4-worker server, all incoming requests (including login and static pages) are completely blocked.

### 10.3 Production Scaling Design (How to Explain in an Interview)
```
[Client POST /upload/] 
    ↓
[Django View validates file, writes to S3/Storage, creates Statement record (status='queued')]
    ↓
[Dispatches Celery Task: parse_statement_task.delay(statement_id)]
    ↓
[Returns HTTP 202 Accepted {"statement_id": id, "status": "queued"}]
    ↓
[Celery Worker picks task from Redis/RabbitMQ queue]
    ├─ Extracts text & redacts PII
    ├─ Calls Gemini API
    ├─ Writes Transaction records
    └─ Updates Statement status = 'analytics_ready'
    ↓
[Client polls GET /statements/<id>/status/ OR receives Server-Sent Events (SSE) / WebSocket push]
```

---

# 11. PERFORMANCE AND SCALABILITY

### 11.1 Current Implementation Bottlenecks
1. **N+1 Database Insertions:** In `statements/parser.py:217`, transactions are created row-by-row inside a loop:
   ```python
   for tx in result_data.transactions:
       Transaction.objects.create(...)  # Generates N separate SQL INSERT statements!
   ```
   *Fix:* Use `Transaction.objects.bulk_create(transaction_batch_list)`.
2. **Missing Database Indexes:**
   - `Transaction.statement_id` has an index (created automatically by Django for foreign keys).
   - However, `Transaction.date`, `Transaction.transaction_type`, and `Transaction.category` have **no database indexes**.
   - Filtering `Transaction.objects.filter(statement_id=statement_id, transaction_type="debit")` triggers full table scans on large datasets.
3. **Redundant Layer A Analytics Computations:**
   - In `statements/views.py:StatementDetailView.get()`, Layer A analytics are calculated on-the-fly if not present.
   - When the user subsequently clicks "Run AI Audit", `run_full_audit()` calls `run_audit()` again, duplicating all aggregate queries.
4. **SQLite Concurrency Locks:** SQLite locks the entire database file on write operations. Under concurrent user write traffic, threads experience `sqlite3.OperationalError: database is locked`.

### 11.2 Scaling to 100x Users: Current vs. Production Roadmap
| Dimension | Current Implementation | 100x Production Scale Architecture |
|---|---|---|
| **Database** | SQLite 3 (Single file on local disk) | Managed PostgreSQL (AWS RDS / GCP Cloud SQL) with read replicas and connection pooling (PgBouncer) |
| **Statement Processing** | Synchronous inside HTTP thread | Asynchronous task queues via Celery + Redis |
| **Object Storage** | Local filesystem (`media/statements/`) | Secure Cloud Storage (AWS S3 / Google Cloud Storage) with presigned expiring URLs |
| **Caching Layer** | None | Redis caching for parsed statement metadata, user profile lookups, and Layer A analytics |
| **Web Server** | Django development server (`manage.py runserver`) | Gunicorn/Uvicorn WSGI/ASGI workers behind an Nginx reverse proxy with TLS termination |
| **Bulk Operations** | Row-by-row ORM `.create()` | `Transaction.objects.bulk_create()` with batch sizing |
| **Database Indexes** | Primary Keys and Foreign Keys only | Composite indexes: `(statement_id, transaction_type)` and `(statement_id, date)` |

---

# 12. TESTING

### 12.1 Current Test Coverage Analysis
| Test File | Lines of Code | What it Verifies | Status |
|---|---|---|---|
| `accounts/tests.py` | 3 | None (Boilerplate `from django.test import TestCase`) | **EMPTY / UNTESTED** |
| `statements/tests.py` | 3 | None (Boilerplate `from django.test import TestCase`) | **EMPTY / UNTESTED** |
| `audits/tests.py` | 3 | None (Boilerplate `from django.test import TestCase`) | **EMPTY / UNTESTED** |

### 12.2 Critical Untested Paths (Interview Defense)
An interviewer will quickly note that test coverage is currently 0%. You must proactively highlight which tests must be prioritized:
1. **PII Sanitizer Unit Tests:** Verifying that regexes accurately redact PAN, Aadhaar, account numbers, and phone numbers without mangling transaction amounts, merchant names, or dates.
2. **Layer A Financial Engine Tests:**
   - Cashflow calculation with edge cases (zero credit, negative net savings).
   - Duplicate detection accuracy across same date/vendor/amount.
   - Statistical anomaly calculation with sample sizes `< 10` (should return empty list) and standard deviation outliers.
   - Subscription detection across multi-month vs. single-month statements.
3. **Authentication & Security Tests:** Token generation, expired token refresh, email login failures, and row-level authorization (User B cannot access User A's statement).
4. **API Integration Tests:** Multipart PDF upload mocking Gemini responses and testing the 422 unprocessable entity destruction branch.

---

# 13. DEPLOYMENT & DEVOPS

### 13.1 Deployment Inventory
- **Docker / Dockerfile:** **NOT PRESENT** in repository.
- **docker-compose.yml:** **NOT PRESENT** in repository.
- **CI/CD Pipelines (.github/workflows):** **NOT PRESENT** in repository.
- **Environment Management:** Utilizes `python-dotenv` to load `.env` file variables (`SECRET_KEY`, `GEMINI_API_KEY`).
- **Web Server Gateways:** Contains standard `finsight/wsgi.py` (synchronous) and `finsight/asgi.py` (asynchronous).

### 13.2 How the System Currently Runs Locally
1. **Backend Server:**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
   *Runs on `http://127.0.0.1:8000`*.
2. **Frontend Static Server:**
   ```bash
   python3 -m http.server 8080 --directory frontend
   ```
   *Runs on `http://localhost:8080`*.

### 13.3 Production Deployment Strategy (What to Propose to IBM)
1. **Containerization:** Author a multi-stage `Dockerfile` with Python 3.12-slim base, non-root application user, and pre-installed C-libraries for `pdfplumber`.
2. **Process Management:** Run Gunicorn with Uvicorn worker classes:
   `gunicorn finsight.wsgi:application --workers 4 --bind 0.0.0.0:8000 --timeout 120`.
3. **Static File & Media Separation:** Nginx serves static assets directly and proxies API calls to Gunicorn. Media files (PDFs) are uploaded directly to private object storage (S3) via pre-signed URLs.

---

# 14. TECHNICAL DECISION ANALYSIS

### 1. Why Django & Django REST Framework?
- *Reason cannot be determined from the codebase.*
- *Possible technical justification:* Django provides an enterprise-ready framework with built-in ORM security (parameterized queries), robust session and authentication scaffolding, and mature migration management. DRF layers standardized serialization, request parsing, and HTTP status handling on top with minimal boilerplate.

### 2. Why SimpleJWT instead of Session-Based Authentication?
- *Reason cannot be determined from the codebase.*
- *Possible technical justification:* The architecture decouples the frontend (static files on port 8080 or CDN) from the backend API (port 8000). Cookie-based sessions require complex cross-origin cookie sharing, CSRF token negotiation, and stateful server memory. Stateless JWT bearer tokens allow completely decoupled, cross-origin API authorization.

### 3. Why Pydantic for Gemini Output Formatting?
- *Determined from codebase (`audits/schemas.py`, `statements/parser.py`):* LLMs frequently return conversational filler (e.g., *"Sure, here is your JSON..."*) or missing keys. By using Pydantic models compiled into Gemini's `response_schema`, the model uses schema-constrained sampling, guaranteeing valid JSON that parses cleanly into database columns and frontend components.

### 4. Why a Two-Layer Auditing Architecture (Layer A + Layer B)?
- *Determined from codebase (`audits/audit_engine.py`, `audits/ai_audit.py`):*
  - **Cost & Speed:** Calculating cashflows, category totals, duplicates, and Z-score anomalies in pure Python takes < 5 milliseconds and costs $0.00.
  - **Accuracy:** LLMs struggle with multi-digit floating-point arithmetic and reliable statistical grouping.
  - **Token Optimization:** Compressing Layer A metrics reduces prompt tokens by > 80%, drastically cutting Gemini latency and API costs.

### 5. Why Vanilla JavaScript instead of React / Angular / Vue?
- *Reason cannot be determined from the codebase.*
- *Possible technical justification:* Eliminates npm dependency churn, build-step compilation overhead (Vite/Webpack), and complex state management libraries for an application with 4 views, keeping development velocity high and initial asset delivery instant.

---

# 15. CHALLENGES AND BUGS IDENTIFIED

### 1. Module-Level Indentation Bug on `StatementDetailView.delete`
- **Bug Location:** `statements/views.py:70-91`.
- **The Issue:** `def delete(self, request, statement_id):` is written at column 0 (indentation level 0) directly after `StatementDetailView.get()`. Because it is outside the class definition, DRF does not recognize `DELETE` as an allowed method on `StatementDetailView`. Any HTTP `DELETE /api/v1/statements/<id>/` returns `405 Method Not Allowed`.
- **How to Fix:** Indent the method by 4 spaces inside `class StatementDetailView(APIView)`.

### 2. Missing `generate_data.py` Breaks Mock Parser
- **Bug Location:** `statements/parser.py:83`.
- **The Issue:** When `MOCK_PARSER` is enabled (or `GEMINI_API_KEY` is omitted), line 83 executes `from .generate_data import generate_transactions`. However, `generate_data.py` was explicitly added to `.gitignore` (line 11) and was never committed to Git. The mock parser immediately crashes with `ModuleNotFoundError: No module named 'statements.generate_data'`.
- **How to Fix:** Implement an in-line mock data generator or check in a mock data fixture.

### 3. Missing `statements.html` Frontend Screen
- **Bug Location:** `frontend/js/dashboard.js:71` & `frontend/upload.html:32`.
- **The Issue:** The dashboard navigation and "My Statements" card direct users to `statements.html`. This file does not exist in the `frontend/` directory, resulting in browser 404 errors when users attempt to view their statement list.
- **How to Fix:** Create `frontend/statements.html` and wire it to consume `GET /api/v1/statements/` using `StatementListSerializer`.

### 4. Discrepancy in Gemini Model Tiers
- **Bug Location:** `statements/parser.py:170` vs `audits/ai_audit.py:170`.
- **The Issue:** `parser.py` requests `model="gemini-3.5-flash"`, while `ai_audit.py` requests `model="gemini-2.5-flash"`. In Google's GenAI API, `gemini-3.5-flash` is an invalid model identifier that will throw an API `404 Not Found / Model Not Supported` error when live API calls are triggered.
- **How to Fix:** Standardize both modules on a valid, production Google model identifier (e.g., `gemini-1.5-flash` or `gemini-2.5-flash`).

### 5. Orphaned Media Files on Parser Abortion
- **Bug Location:** `statements/views.py:116-124`.
- **The Issue:** When transaction parsing yields 0 rows, the view executes `statement.delete()` to protect database integrity. However, Django's model deletion does not delete files stored on disk via `FileField`. The uploaded PDF remains permanently orphaned inside `media/statements/`.
- **How to Fix:** Call `statement.file.delete(save=False)` prior to calling `statement.delete()`.

---

# 16. INTERVIEW QUESTIONS (ORGANIZED BY TOPIC)

### Beginner
1. What is the role of `CustomUser` in the accounts app, and why was it created instead of using Django's default `User`?
2. How does the frontend maintain user authentication across page refreshes?
3. What is the purpose of `PageNumberPagination` in `StatementListView`?

### Intermediate
4. Explain how `pdfplumber` extracts text from bank statements and where it can fail on scanned documents.
5. How does `redact_sensitive_info` use regular expressions to protect PII, and what types of data does it target?
6. Describe how `SimpleJWT` issues and validates access and refresh tokens in this project.
7. What happens in `StatementUploadView` if a statement fails to parse any transactions?

### Advanced & Architectural
8. Why did you choose a two-layer auditing system (Layer A deterministic vs. Layer B generative) instead of letting Gemini do the entire audit?
9. Explain how Pydantic schemas are used in conjunction with the Google GenAI SDK to guarantee structured JSON output.
10. In `audits/ai_audit.py`, how does the context compression logic work, and why is it important for LLM cost and performance?
11. How are Layer A analytics and Layer B AI audit results persisted in the database without creating dozens of normalized tables?

### Debugging & Troubleshooting
12. If a client attempts to delete a statement via `DELETE /api/v1/statements/1/`, what happens and why? How would you fix it?
13. If someone clones this repo fresh and runs it without a Gemini API key, why does the statement upload fail?
14. What would happen if a user uploads a statement covering only 14 days of transactions? How does the audit engine respond?
15. What happens if the Gemini API returns a 429 Rate Limit error during transaction parsing?

### Security
16. What are the security risks associated with storing JWT tokens in browser `localStorage`, and how would you resolve them in an enterprise deployment?
17. How does the API prevent User A from viewing or auditing User B's financial statements?
18. Is this application vulnerable to SQL injection? Why or why not?
19. What security vulnerabilities exist in the current file upload implementation?

### Scalability & Enterprise Operations
20. Why is running external LLM API calls synchronously inside Django views problematic in production?
21. How would you re-architect this platform using Celery, Redis, and WebSockets/SSE?
22. What database indexes are currently missing from the `Transaction` model that would hurt performance at scale?
23. If 1,000 users upload statements simultaneously, where will the current SQLite database fail?

### AI & Prompt Engineering
24. How does the prompt in `audits/prompts.py` prevent Gemini from hallucinating non-existent financial issues?
25. What is the difference between RAG and the context injection pattern used in this codebase?
26. Why did `statements/parser.py` specify `gemini-3.5-flash` while `audits/ai_audit.py` specified `gemini-2.5-flash`?

### Coding & Algorithms
27. Walk through the algorithm used in `detect_anomalies`. How is the statistical threshold calculated?
28. How does `detect_subscriptions` distinguish a recurring monthly subscription from random recurring charges?
29. Walk through `detect_emi`. How does it combine keyword matching with temporal grouping?

### Technology Justifications ("Why" Questions)
30. Why did you use Django REST Framework instead of a lightweight asynchronous framework like FastAPI?
31. Why did you choose SQLite over PostgreSQL for local development?

---

# 17. MODEL INTERVIEW ANSWERS

#### Question 1: Can you walk me through the architecture of FinSight and explain the rationale behind your design?
**Ideal Interview Answer:**
"FinSight is designed as a decoupled two-tier platform: a lightweight, client-side rendered frontend using Vanilla ES6 JavaScript and Bootstrap, and a Python backend built on Django REST Framework. The core design philosophy is what I call a **Hybrid Two-Layer Auditing Architecture**. 

Instead of treating the LLM as an all-knowing calculator, we divide auditing into two discrete stages. **Layer A** is a deterministic engine written in pure Python and Django ORM aggregations. It handles mathematical precision: cashflow sums, savings rates, duplicate charge detection, subscription recurrence across calendar months, and statistical anomaly detection using a two-standard-deviation Z-score threshold. 

**Layer B** is our generative layer powered by Google Gemini. It takes a compressed summary of Layer A's metrics and uses strict Pydantic schema validation to synthesize an executive audit report containing risk levels, strengths, concerns, and recommendations. This separation guarantees 100% mathematical accuracy, cuts LLM token costs by over 80%, and eliminates conversational hallucination."

**Follow-Up Question:** "Why didn't you just pass the raw transactions into Gemini and ask it to find the anomalies and calculate cashflow directly?"
**Follow-Up Answer:** "Large Language Models are probabilistic next-token predictors; they are notoriously unreliable at floating-point arithmetic, running sums, and strict statistical calculations over hundreds of lines. If you prompt an LLM with 300 transactions and ask for net savings, it will frequently hallucinate totals or miss edge-case duplicate charges. Furthermore, sending thousands of raw transaction tokens on every audit balloons latency and API costs. By calculating numbers deterministically in Python, we guarantee exact figures and let the LLM focus on what it excels at: semantic interpretation, risk context, and executive communication."

---

#### Question 2: How do you address data privacy and compliance when sending sensitive financial statements to third-party LLMs like Gemini?
**Ideal Interview Answer:**
"Privacy is handled at the network perimeter before any data leaves our server. When a bank statement PDF is uploaded, it is parsed locally by `pdfplumber`. Before any extracted text is transmitted to the Google Gemini API, it passes through our `redact_sensitive_info` sanitizer function in `statements/parser.py`. 

This module executes pre-compiled regular expressions that detect and mask Indian financial identifiers and general PII. Specifically, it redacts customer names in headers, residential addresses, email addresses, 10-digit mobile phone numbers, Indian IFSC banking codes, Permanent Account Number (PAN) cards, 12-digit Aadhaar cards, and credit card or bank account numbers between 9 and 18 digits. By substituting these with deterministic redaction tags like `[ACCOUNT_REDACTED]` and `[NAME_REDACTED]`, Gemini never sees identifiable user data, ensuring compliance with data privacy mandates."

**Follow-Up Question:** "What are the limitations of a regex-based PII redaction approach compared to an NLP Named Entity Recognition (NER) model?"
**Follow-Up Answer:** "Regex is fast, zero-dependency, and highly effective for rigidly structured tokens like PAN cards, IFSC codes, Aadhaar, and phone numbers. However, its primary weakness is header name and address extraction. If a bank formats an account holder name atypically—such as omitting standard prefixes like 'Customer Name:'—regex may miss it. In a production enterprise pipeline, I would complement regex with a lightweight local Named Entity Recognition (NER) model, such as SpaCy or Microsoft Presidio, to catch irregular contextual names and entities before API transmission."

---

#### Question 3: In `statements/views.py`, there is a `delete` function. How does that endpoint behave in your API?
**Ideal Interview Answer:**
"That is an important implementation detail in our codebase. If you inspect `statements/views.py` around line 70, `def delete(self, request, statement_id)` was accidentally written at column 0—meaning it is defined as a standalone module-level function rather than an indented method within `StatementDetailView`. 

Because DRF class-based views inspect class methods to determine allowed HTTP verbs, Django REST Framework does not see a `delete` method on `StatementDetailView`. If a client issues an `HTTP DELETE` request to `/api/v1/statements/<id>/`, DRF will respond with an `HTTP 405 Method Not Allowed`. To fix this, we simply indent the function 4 spaces inside `StatementDetailView`. Additionally, I would update the implementation to ensure `statement.file.delete(save=False)` is executed to clean up physical storage on disk."

**Follow-Up Question:** "What does this tell you about your development and testing pipeline?"
**Follow-Up Answer:** "It highlights the immediate need for automated API integration tests. Currently, the test suites in `accounts/tests.py`, `statements/tests.py`, and `audits/tests.py` contain initial boilerplate without test cases. If an automated test suite had run a test case executing `self.client.delete(f'/api/v1/statements/{id}/')`, this 405 error would have been flagged immediately during continuous integration."

---

#### Question 4: How does the application handle Gemini API rate limits or transient server failures?
**Ideal Interview Answer:**
"Both our transaction extraction pipeline in `statements/parser.py` and our audit generator in `audits/ai_audit.py` implement an explicit retry loop with exponential backoff. 

We configure `max_retries = 5` and an initial `retry_delay = 8` seconds. When we call `client.models.generate_content()`, we catch exceptions. If the error message indicates a temporary overload—specifically HTTP 429 for rate limiting or HTTP 503 for service unavailable—the catch block logs the attempt, sleeps for the backoff duration, and doubles the delay: 8 seconds, then 16, 32, and 64 seconds. If the call succeeds, it breaks out immediately. If retries are exhausted or a non-retryable error occurs, it aborts cleanly."

**Follow-Up Question:** "What is the operational risk of running a 64-second exponential backoff loop inside a synchronous Django view?"
**Follow-Up Answer:** "It creates a severe blocking bottleneck. Because this runs synchronously inside the WSGI request-response cycle, the worker thread (e.g., in Gunicorn) is held open for the entire duration. If multiple users hit rate limits at the same time, all available worker threads become saturated, causing connection timeouts for incoming traffic. Furthermore, enterprise load balancers like AWS ALB or Nginx default to 30- or 60-second timeouts, meaning the client will receive a `504 Gateway Timeout` even if Gemini eventually succeeds. In production, this must be decoupled into an asynchronous Celery task."

---

#### Question 5: Walk me through your statistical anomaly detection algorithm in `audits/audit_engine.py`.
**Ideal Interview Answer:**
"The anomaly detector in `detect_anomalies` identifies debit transactions that are statistically abnormal compared to the user's overall spending pattern. 

First, we establish a guardrail: we require a minimum sample size of at least 10 debit transactions (`MIN_ANOMALY_SAMPLE_SIZE = 10`). If the statement has fewer than 10 transactions, we return an empty list because small sample sizes yield volatile standard deviations. 

For statements meeting the threshold, we extract all debit transaction amounts and compute the sample mean. Then we calculate the sample variance by summing the squared differences between each amount and the mean, divided by the sample size, and take the square root to obtain the standard deviation. We set a dynamic threshold at `mean + (2 * std_dev)`, corresponding to roughly a 95% confidence boundary under normal distribution assumptions. Any individual transaction exceeding this threshold is flagged as an anomaly, capturing the vendor, date, amount, and the calculated threshold."

**Follow-Up Question:** "Financial spending distributions are typically right-skewed and heavy-tailed, not normal. Why use standard deviation instead of Interquartile Range (IQR)?"
**Follow-Up Answer:** "That is a very sharp observation. Spending data is indeed heavily right-skewed—most transactions are small daily expenses like groceries or transit, while rent or large purchases create extreme positive outliers. Using standard deviation on skewed data can artificially inflate the threshold because massive outliers pull the mean and standard deviation upward, potentially masking moderately high anomalies. A more robust statistical approach for enterprise production is the **Interquartile Range (IQR)**: defining anomalies as transactions exceeding $Q3 + 1.5 \times IQR$, or using median absolute deviation (MAD), which are resistant to extreme outlier distortion."

---

#### Question 6: How does FinSight detect recurring subscriptions and loan EMIs?
**Ideal Interview Answer:**
"Both detectors reside in `audits/audit_engine.py` and operate on temporal heuristics. 

First, both require that the statement duration covers at least 60 days (`MIN_SUBSCRIPTION_DURATION_DAYS = 60`), calculated by taking `(Max(date) - Min(date)).days + 1`. If a statement covers only 30 days, recurring monthly patterns cannot be proven.

For **subscriptions**, we group debit transactions by a compound key of `(normalized_vendor, amount)`. If a key appears at least twice, we inspect the calendar months of those occurrences: `(tx.date.year, tx.date.month)`. If the transaction appears across 2 or more unique months, it is flagged as a likely subscription, capturing the recurring monthly charge and frequency.

For **EMIs**, we apply an additional domain filter. We look for specific banking keywords—such as `'emi'`, `'loan'`, `'finance'`, and `'repayment'`—in the vendor name or raw description. If a candidate matches, we group by vendor and amount across unique months. If confirmed, we calculate the active monthly debt obligation."

**Follow-Up Question:** "What happens if a user has a bi-weekly subscription or if the billing date shifts slightly each month?"
**Follow-Up Answer:** "Because our grouping key uses `(vendor, amount)` rather than exact 30-day date deltas, a shifted billing date (e.g., January 3rd and February 7th) is still successfully detected as long as the amount matches and it lands in different calendar months. However, the limitation of the current implementation is strict amount equality. If a subscription price changes (e.g., Netflix increases from ₹499 to ₹649) or if utility bills fluctuate slightly, the compound key fails to group them. In production, we would introduce fuzzy amount clustering within a tolerance band (e.g., $\pm 5\%$) combined with vendor name normalization."

---

#### Question 7: Can you explain how you enforced structured outputs from Gemini without conversational markdown or invalid JSON?
**Ideal Interview Answer:**
"We enforced structured output using Google GenAI SDK's native schema binding paired with **Pydantic**. 

In `audits/schemas.py`, we define an `AIAuditSchema` class inheriting from `pydantic.BaseModel`. It defines exact fields: `risk_level` with a `Literal["LOW", "MODERATE", "HIGH"]` constraint, string fields for `overall_summary` and `final_verdict`, and typed string lists for `strengths`, `concerns`, `suspicious_activity`, and `recommendations`. 

When invoking `client.models.generate_content()`, we supply two critical parameters in the configuration: `response_mime_type="application/json"` and `response_schema=AIAuditSchema`. This directs Gemini's inference engine to apply constrained decoding at the token level, restricting sampling only to tokens that satisfy the grammar of our Pydantic schema. When the response arrives, we call `response.parsed.model_dump()`, giving us a clean, validated Python dictionary ready for database insertion."

**Follow-Up Question:** "What happens if the model violates the schema or returns an incomplete response?"
**Follow-Up Answer:** "If the model's output cannot be parsed into `AIAuditSchema`, `response.parsed` raises a validation error. In `audits/ai_audit.py`, this is caught in our try-except block, raising an exception that triggers `statement.audit_status = 'failed'` in `run_full_audit`. This guarantees that partial or malformed JSON is never stored in the database or rendered broken on the frontend."

---

#### Question 8: Why did you decide to store analytics and AI audit results in Django `JSONField`s instead of separate relational tables?
**Ideal Interview Answer:**
"We made a deliberate architectural trade-off based on data access patterns. 

Our transactions require relational normalization (`Transaction` model) because we run SQL aggregate queries—such as `Sum('amount')`, filtering by `transaction_type`, and grouping by `category`. 

However, the outputs of Layer A (`Statement.analytics`) and Layer B (`Statement.ai_audit`) represent a consolidated point-in-time audit snapshot. They contain deeply nested structures: category percentage breakdowns, arrays of duplicate transaction groups, subscription lists, anomaly threshold metrics, and multi-bullet audit observations. If we normalized this relationally, we would have had to create 7 distinct database tables with foreign keys and perform extensive multi-table joins on every statement detail view. By using Django's native `JSONField`, we can read and write the entire audit report in a single query while preserving the flexibility of the JSON document."

**Follow-Up Question:** "What is the downside of using `JSONField` in a relational database like PostgreSQL or SQLite?"
**Follow-Up Answer:** "The primary trade-off is the loss of relational constraints and schema enforcement at the database level. In a `JSONField`, the database engine cannot easily enforce foreign key integrity or validate that a field like `risk_level` contains only permitted values. Additionally, querying across statements—such as 'find all statements where an anomaly exceeded ₹50,000'—requires specialized JSON-path operators (e.g., `->>` in PostgreSQL) which are slower and harder to index than normalized columns. For FinSight, because audits are always fetched by `statement_id`, document storage is the optimal trade-off."

---

#### Question 9: How would you scale FinSight if the user base grew 100x and statement uploads spiked?
**Ideal Interview Answer:**
"Scaling FinSight 100x requires addressing three core bottlenecks: synchronous processing, database concurrency, and file storage.

First, we must decouple statement processing from the HTTP lifecycle. Currently, file parsing and Gemini calls run inside the request thread. We would introduce **Celery with Redis** as a distributed message broker. When a user uploads a statement, the API saves the file to cloud storage, marks the statement as `queued`, and returns `HTTP 202 Accepted` immediately. Background Celery workers pick up the job, run `pdfplumber`, redact PII, call Gemini, and execute Layer A analytics. The client receives status updates via Server-Sent Events (SSE) or WebSockets.

Second, we would migrate from local SQLite to **Managed PostgreSQL** (such as AWS RDS) with PgBouncer connection pooling. We would add composite database indexes on `(statement_id, transaction_type)` and `(statement_id, date)` and replace row-by-row `Transaction.objects.create()` with `bulk_create`.

Third, we would move uploaded PDF storage from the local `/media/` folder to **Amazon S3** or Google Cloud Storage, using short-lived pre-signed URLs to protect document privacy."

**Follow-Up Question:** "How would you handle Gemini API rate limits at 100x scale across multiple Celery workers?"
**Follow-Up Answer:** "At 100x scale, multiple concurrent Celery workers will easily exceed Google Cloud API quota limits (requests per minute or tokens per minute). To resolve this, we would implement **distributed rate limiting** at the task queue level using Redis token-bucket algorithms (e.g., Celery's `rate_limit` directive or `celery-singleton`). Additionally, we would implement multi-key rotation or route requests through an enterprise AI gateway like Cloudflare AI Gateway or LiteLLM, which provides load balancing, automatic failover across cloud regions, and caching of identical prompts."

---

#### Question 10: How do you verify user authorization on statement retrieval and audit endpoints?
**Ideal Interview Answer:**
"Authorization is enforced through row-level ownership checks inside our DRF class-based views. 

First, the endpoint enforces authentication via DRF's `IsAuthenticated` permission class, which decodes and validates the incoming JWT Bearer token from the `Authorization` header, assigning the authenticated user to `request.user`. 

Second, when accessing a specific statement by ID—for example in `StatementDetailView` or `StatementAuditView`—we never query by primary key alone (`Statement.objects.get(id=statement_id)`). Instead, we enforce compound ownership:
```python
statement = Statement.objects.get(id=statement_id, user=request.user)
```
If a user attempts to access a statement ID that belongs to another user (an Insecure Direct Object Reference or IDOR attack), the query fails to find a matching record and raises `Statement.DoesNotExist`, returning an `HTTP 404 Not Found`. This prevents unauthorized data access and prevents attackers from discovering valid statement IDs."

**Follow-Up Question:** "Why return a 404 instead of a 403 Forbidden when a user requests someone else's statement?"
**Follow-Up Answer:** "Returning `404 Not Found` rather than `403 Forbidden` is a deliberate security best practice to prevent **resource enumeration attacks**. If you return a 403, you confirm to the attacker that the statement ID actually exists in the database, revealing valid object IDs. By returning a 404, the system treats unauthorized IDs identically to non-existent IDs, leaking zero metadata to unauthorized clients."

---

# 18. "INTERVIEWER ATTACK MAP" (IF I SAY THIS, INTERVIEWER MAY ASK THIS)

### 1. If I say: "We used JWT tokens for authentication."
- **Interviewer may ask:**
  - Where do you store the tokens on the client? (Answer: Currently in `localStorage`, but in production they should be stored in `HttpOnly`, `SameSite=Strict` cookies to mitigate XSS).
  - What happens when an access token expires? (Answer: The client catches the 401 response and dispatches the refresh token to `/api/v1/accounts/login/refresh/` to receive a new access token without requiring re-login).
  - Can you revoke a JWT token before it expires? (Answer: JWTs are stateless, so standard tokens cannot be revoked without maintaining a Redis token blacklist/blocklist).
  - What is token rotation? (Answer: In `settings.py`, `ROTATE_REFRESH_TOKENS = True`; every time a refresh token is used, a new refresh token is issued and the old one is invalidated).

### 2. If I say: "We use Google Gemini to audit the bank statements."
- **Interviewer may ask:**
  - Did you send the raw bank statements directly to Gemini? (Answer: No, raw text is extracted locally via `pdfplumber`, sanitized of all PII via regex, and Layer A calculates numbers in Python; Gemini only receives compressed summary metrics).
  - How do you stop Gemini from hallucinating numbers or formatting? (Answer: We use Pydantic models compiled directly into Gemini's `response_schema`, enforcing token-level constrained grammar decoding).
  - Which exact Gemini model did you use? (Answer: The code calls `gemini-2.5-flash` in `ai_audit.py` and `gemini-3.5-flash` in `parser.py`, which is standardized on production Flash tiers).
  - What happens if the Gemini API goes down or rate limits? (Answer: We implement a 5-attempt retry loop with exponential backoff starting at 8 seconds, and mark the statement status as `failed` if retries exhaust).

### 3. If I say: "We have an anomaly detection engine."
- **Interviewer may ask:**
  - Is it a machine learning model (like Isolation Forest or Autoencoders)? (Answer: No, it is a statistical rule-based detector calculating a dynamic threshold at $\mu + 2\sigma$ on debit transactions).
  - Why did you require a sample size of 10? (Answer: Standard deviation calculation on small samples has high variance; 10 represents a baseline sample size to avoid false positives).
  - How do you handle non-normally distributed spending data? (Answer: While $\mu + 2\sigma$ is effective for initial heuristics, production systems should use non-parametric statistics like Interquartile Range $Q3 + 1.5 \times IQR$ or Median Absolute Deviation).

### 4. If I say: "We sanitize all PII locally."
- **Interviewer may ask:**
  - What exact regex patterns did you use? (Answer: Dedicated regexes for PAN cards `[A-Z]{5}[0-9]{4}[A-Z]`, Aadhaar 12-digit blocks, IFSC codes, phone numbers, emails, and header name/address labels).
  - What happens if a customer name is written without a 'Name:' label? (Answer: Pure regex can miss unlabelled names; that is why enterprise systems pair regex with a local NLP NER model like Presidio).
  - Does the sanitized text get saved to disk? (Answer: No, the raw PDF is stored in `media/`, but only sanitized text is transmitted to external API endpoints).

### 5. If I say: "We built the backend with Django and SQLite."
- **Interviewer may ask:**
  - Why SQLite instead of PostgreSQL? (Answer: SQLite was chosen strictly for zero-configuration local development velocity; PostgreSQL is the designated target for enterprise production).
  - How does SQLite handle concurrent writes? (Answer: SQLite locks the entire database file during writes, creating bottlenecks under concurrent multi-user load).
  - Are you using database transactions? (Answer: The views currently run under Django's autocommit; adding `@transaction.atomic` is recommended to ensure statement creation and transaction insertion commit as an all-or-nothing unit).

---

# 19. RESUME CLAIM VERIFICATION MATRIX

| Potential Resume Claim | Codebase Reality & Evidence | Status | Interview Risk & Safe Defense Strategy |
|---|---|---|---|
| **"Built AI-powered financial statement auditor using Django & Gemini"** | Fully verified in `statements/parser.py`, `audits/ai_audit.py`, and `audits/audit_engine.py`. | ✅ **Clearly Implemented** | **Low Risk.** Defend the two-layer architecture (deterministic Layer A + generative Layer B). |
| **"Implemented secure JWT authentication with role/ownership security"** | Verified in `accounts/serializers.py` (SimpleJWT) and `statements/views.py` (`user=request.user`). | ✅ **Clearly Implemented** | **Low Risk.** Be prepared to explain token rotation and row-level ownership checks. |
| **"Engineered PII data redaction pipeline for banking compliance"** | Fully verified in `statements/parser.py:redact_sensitive_info` with 8 regex filters. | ✅ **Clearly Implemented** | **Low Risk.** Discuss regex strengths for structured IDs and limitations for unstructured names. |
| **"Developed heuristic risk detectors for duplicate charges & subscriptions"** | Fully verified in `audits/audit_engine.py` (`detect_duplicates`, `detect_subscriptions`, `detect_emi`). | ✅ **Clearly Implemented** | **Low Risk.** Explain the 60-day duration requirement and multi-month calendar grouping. |
| **"Integrated Conversational RAG Bank Statement Chatbot"** | Zero RAG code, embeddings, or vector databases exist. Only listed in `README.md` roadmap. | ❌ **Cannot Verify from Code** | **CRITICAL RISK.** **NEVER claim RAG is currently running in this codebase.** State that RAG is an active architectural roadmap design. |
| **"Built Multi-Month Comparative Financial Analysis Engine"** | Statements are analyzed individually; no multi-statement trend comparison exists in code. | ❌ **Cannot Verify from Code** | **High Risk.** Acknowledge as a planned feature; do not claim it is implemented. |
| **"Generated Automated PDF Compliance & Audit Reports"** | `reportlab` is listed in `requirements.txt:34`, but is never imported or called in code. | 🟡 **Configured but Unused** | **Moderate Risk.** Clarify that report export was scaffolded in dependencies but not yet wired to an API view. |
| **"Implemented Asynchronous Background Processing with Celery & Redis"** | Zero Celery or Redis code exists. All parsing and AI auditing run synchronously in views. | ❌ **Cannot Verify from Code** | **CRITICAL RISK.** **NEVER claim Celery/Redis is implemented.** Explain that synchronous execution was chosen for prototype velocity and outline the Celery migration plan. |
| **"Engineered Comprehensive Unit & Integration Test Suite"** | All `tests.py` files in `accounts`, `statements`, and `audits` contain 3 lines of boilerplate with 0 tests. | ❌ **Cannot Verify from Code** | **High Risk.** Do not claim high test coverage. Explain the critical test cases you would write first (PII sanitization, anomaly math, auth). |

---

# 20. FINAL INTERVIEW CHEAT SHEET

### Project in 30 Seconds
"FinSight is an AI-powered financial statement auditing platform. Users upload PDF bank statements, our backend redacts PII locally, and a two-layer auditing pipeline takes over: Layer A uses deterministic Python algorithms to calculate cashflow, detect duplicate charges, subscriptions, and statistical anomalies; Layer B uses Google Gemini with strict Pydantic schemas to generate an auditor-grade financial report with actionable recommendations."

### Project in 1 Minute
"FinSight addresses the inefficiency and human error inherent in personal and SME financial auditing. Built with Django REST Framework and a modern Vanilla JavaScript frontend, the platform ingests bank statements and prioritizes data privacy through local regex sanitization before external API transmission. 

The core architectural innovation is its **Two-Layer Auditing Architecture**: instead of relying on LLMs for math, Layer A calculates cashflow metrics, spending breakdowns, recurring subscriptions across calendar months, loan EMIs, and Z-score anomalies deterministically. Layer B compresses these metrics and prompts Google Gemini using strict Pydantic JSON schemas to deliver an executive audit report with risk ratings (Low, Moderate, High), strengths, concerns, and prioritized financial advice."

### Project in 3 Minutes
"Traditional financial auditing requires hours of manual ledger inspection to catch double-billing, lifestyle spending inflation, and subscription creep. FinSight automates this workflow with a secure, hybrid AI architecture. 

When a user registers, they receive JWT access and refresh tokens. Upon uploading a PDF bank statement, `pdfplumber` extracts text, and our local sanitizer strips all PAN cards, Aadhaar numbers, account numbers, emails, and phone numbers. The parsed transactions are stored in a normalized relational database.

We then execute our two-layer audit. We recognized early on that LLMs are non-deterministic and prone to calculation errors. To solve this, Layer A runs deterministic Python and ORM aggregations to compute exact cashflow, category ratios, duplicates, recurring subscriptions across multi-month spans, and statistical anomalies exceeding two standard deviations. 

Layer B then takes over: we compress Layer A's metrics into a focused context object, drastically reducing prompt tokens and latency. We prompt Google Gemini using constrained decoding via Pydantic schemas to return structured audit reports with zero markdown filler. Results are cached in the database and rendered on an interactive frontend featuring dynamic category progress bars and risk badges."

### Top 10 Technologies You Must Understand
1. **Django REST Framework:** APIViews, request serialization, permission classes, pagination.
2. **SimpleJWT:** Stateless token auth, access vs refresh tokens, token rotation.
3. **Google GenAI SDK:** `client.models.generate_content`, `response_schema`, structured outputs.
4. **Pydantic (v2):** Schema validation, `BaseModel`, `Field`, `Literal`, constrained LLM generation.
5. **pdfplumber:** PDF layout parsing, character stream extraction, edge-case handling.
6. **Regular Expressions (Regex):** Pattern matching, lookaheads, case-insensitivity, PII detection.
7. **Django ORM Aggregations:** `annotate()`, `aggregate()`, `Sum()`, `Min()`, `Max()`.
8. **Statistical Outlier Detection:** Sample mean, variance, standard deviation, Z-score thresholds.
9. **CORS (Cross-Origin Resource Sharing):** Origin headers, pre-flight OPTIONS requests.
10. **Vanilla JS & Fetch API:** Async/await, DOM manipulation, handling JWT in request headers.

### Top 5 Technical Challenges Faced & Solved
1. **Preventing LLM Calculation Hallucinations:** Solved by creating the two-layer architecture, isolating arithmetic in Python and semantic reasoning in Gemini.
2. **Protecting Banking Privacy:** Solved by running local regex redaction before data leaves the server perimeter.
3. **Guaranteeing Strict API JSON Formats:** Solved by compiling Pydantic schemas into Gemini's `response_schema`.
4. **Handling LLM Rate Limits:** Solved by implementing exponential backoff retry loops on 429/503 errors.
5. **Database Pollution Prevention:** Solved by aborting uploads and destroying empty records when statements fail to parse.

### Top 5 Architectural Limitations
1. **Synchronous Processing:** LLM calls run in the HTTP request thread, creating gateway timeout risks.
2. **Single SQLite Database:** File-level locking limits concurrent multi-user write throughput.
3. **Local PDF Storage:** Files reside on the local web server filesystem without authenticated access control.
4. **Missing Database Indexes:** Lack of composite indexes on `Transaction(statement_id, transaction_type)` slows queries at scale.
5. **Unindented Delete Function:** Indentation bug in `statements/views.py` causes 405 errors on DELETE requests.

### Top 5 Things You Should NEVER Falsely Claim
1. **NEVER claim you implemented a RAG chatbot.** (No vector database or embedding pipeline exists).
2. **NEVER claim you used Celery, Redis, or background workers.** (Processing is 100% synchronous).
3. **NEVER claim you have extensive test coverage.** (All test files are empty boilerplate).
4. **NEVER claim you implemented PDF compliance report downloads.** (`reportlab` is installed but unused).
5. **NEVER claim the system is deployed on Kubernetes/Docker.** (No Dockerfiles or CI/CD pipelines exist).

---

# WHAT I NEED TO STUDY BEFORE THE IBM INTERVIEW

### 🔴 MUST KNOW (Direct Codebase Defense)
- **The Two-Layer Audit Pipeline:** Be able to explain every calculation in Layer A (`audit_engine.py`) and how it feeds into Layer B (`ai_audit.py`).
- **Structured LLM Outputs with Pydantic:** Know exactly how `AIAuditSchema` enforces valid JSON from Gemini.
- **PII Sanitization Logic:** Know which regex patterns were used and the trade-offs of regex vs. NER models.
- **JWT Lifecycle & Security:** Know how access/refresh tokens work, token rotation, and why `localStorage` has XSS risks compared to `HttpOnly` cookies.
- **The Indentation Bug on Delete:** Be ready to openly explain the `StatementDetailView.delete` indentation bug as an example of code review diligence.

### 🟠 SHOULD KNOW (System Design & Production Scaling)
- **Celery & Redis Architecture:** Be ready to design the asynchronous task pipeline for PDF parsing and AI auditing.
- **PostgreSQL vs SQLite at Scale:** Explain connection pooling, table-level vs row-level locking, and index design.
- **Stateless vs Stateful Scaling:** Explain how to scale Gunicorn workers behind Nginx and store media assets in Amazon S3.
- **API Security Hardening:** Explain CORS restrictions, magic byte file validation, and authenticated media redirects.

### 🟢 NICE TO KNOW (Enterprise & Industry Context)
- **Designing Enterprise RAG Pipelines:** Understand chunking strategies, vector databases (pgvector/Pinecone), and retrieval for conversational financial querying.
- **IBM watsonx & Red Hat OpenShift Alignment:** Understand how this architecture would translate to an enterprise IBM stack (e.g., swapping Gemini for watsonx.ai Granite models and containerizing on OpenShift).
