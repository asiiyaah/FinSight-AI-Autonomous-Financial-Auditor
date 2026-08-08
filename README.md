# FinSight — AI-Powered Financial Statement Auditing Platform 🚀

FinSight allows users to securely upload PDF bank statements and receive automated financial analysis, risk detection, and AI-powered audit insights.
The project combines deterministic statement parsing with Gemini-backed AI audit and chatbot features, all served through a Django backend.

## Key Features ✨

- PDF statement upload and secure backend file access
- Deterministic transaction extraction and analytics
- PII redaction before external AI processing
- Merchant normalization, duplicate detection, subscription/EMI detection, anomaly detection, and cashflow insights
- AI audit generation using Google Gemini (real or mock mode)
- Statement chatbot with retrieval-aware context
- JWT authentication via Django REST Framework and Simple JWT
- Frontend delivered through Django static files and `collectstatic`

## Architecture / Workflow 🧠

User
  ↓
Frontend
  ↓
Django REST API
  ↓
PDF Processing + PII Redaction
  ↓
Financial Intelligence Engine (Layer A)
  ↓
AI Audit / Gemini (Layer B)
  ↓
Audit Results + Insights
  ↓
Chatbot / Statement Retrieval

- **Layer A**: deterministic parsing and analytics
- **Layer B**: Gemini-powered AI audit and chatbot response generation

## AI / Gemini Limitation Notes ⚠️

- Gemini availability depends on the external Gemini API and can be interrupted by quota, rate limits, network failures, or service outages.
- If AI parsing fails during PDF upload, FinSight returns a safe failure message and removes the partially uploaded statement file to avoid inconsistent state.
- If AI audit generation fails, the app keeps existing deterministic analytics intact and returns a controlled error response without overwriting any successful audit results.
- Chatbot responses also handle Gemini errors gracefully and fall back to safe messaging when the AI service is unavailable.
- Deterministic Layer A analytics remain separate from AI Layer B audit generation, so the app still supports statement parsing and deterministic analytics even when Gemini is unavailable.

## Tech Stack 🛠

- **Backend**: Django, Django REST Framework, Simple JWT
- **Database**: PostgreSQL support, SQLite fallback for local development
- **AI / LLM**: Google Gemini via `google-generativeai` / `google-genai`
- **Frontend**: HTML, Vanilla JavaScript, Bootstrap 5, CSS
- **Document Processing**: pdfplumber, pandas, Django file uploads
- **Deployment**: Render, Gunicorn, Django staticfiles

## Project Structure

- `accounts/` — authentication, registration, JWT login, custom user model
- `statements/` — statement upload, parsing, analytics, audit APIs, secure file serving
- `audits/` — analytics engine, AI audit orchestration, prompts, schemas
- `financial_engine/` — merchant mapping, normalization, PII redaction, detectors
- `chatbot/` — chatbot API, intent detection, retrieval context, prompt construction
- `services/` — Gemini provider integration and error handling
- `finsight/` — Django settings, URLs, WSGI, static/media configuration
- `frontend/` — HTML pages and static JS/CSS frontend app
- `media/` — uploaded statement files
- `staticfiles/` — collected production static assets
- `manage.py` — Django management entrypoint

## Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/FinSight.git
   cd FinSight
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Update `.env` with your values.

5. Database configuration:
   - If `POSTGRES_DB` is set, the app uses PostgreSQL.
   - If `POSTGRES_DB` is not set, the app falls back to SQLite.

6. Run migrations:
   ```bash
   python manage.py migrate
   ```

7. Optional static collection:
   ```bash
   python manage.py collectstatic --noinput
   ```

8. Start the development server:
   ```bash
   python manage.py runserver
   ```

9. Open `http://127.0.0.1:8000/` in your browser.

> Do not commit secrets such as `GEMINI_API_KEY` or `SECRET_KEY`.

## Environment Variables

The current settings use:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `GEMINI_API_KEY`
- `USE_MOCK_AI`
- `MOCK_PARSER`
- `MOCK_AUDIT`
- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`

## Deployment

The current deployment is configured for Render and uses Gunicorn to serve the Django application. Static assets are served via Django staticfiles and runtime configuration is controlled by environment variables.

Build command:
```bash
pip install -r requirements.txt && ./build.sh
```

Start command:
```bash
gunicorn finsight.wsgi:application
```

## Live Demo & Deployment Limitations

- Live demo: https://finsight-pqcd.onrender.com
- Hosting: the live site runs on Render's Free tier.
- Cold starts: the web service may spin down after inactivity, so the first request after a period of idle time can be slower.
- Database: the free PostgreSQL instance used by the demo is temporary and has a limited lifetime.
- Storage: the deployed free service uses ephemeral filesystem storage — uploaded PDFs are not permanently retained and should not be relied upon for long-term storage.
- Intended use: the public demo is provided for portfolio demonstration and evaluation of the application's features and architecture; it is not a production financial service.
- Safety: do not upload real bank statements, passwords, API keys, or other sensitive personal/financial information to the public demo.

Note: these limitations apply to the hosted demo only. A local development setup (running the app locally with your own database and storage) can provide persistent storage and stronger operational control.

## Security / Privacy

- JWT authentication protects API access.
- Statement files are served through backend views and permission checks.
- PII is redacted before external AI processing.
- Secrets are loaded from environment variables.
- Production deployments should use `DEBUG=False`.

## Current Status

FinSight is a completed portfolio project with working PDF upload, parsing, analytics, AI audit, and chatbot interactions.
The app is integrated end-to-end and demonstrates a full-stack financial auditing workflow.

## Future Improvements

- Persistent production storage for uploaded statements
- Permanent PostgreSQL deployment
- Improved deployment infrastructure and monitoring
- Expanded chatbot retrieval and context handling
- Stronger automated tests and validation

## Star the Project ⭐

If you found this project helpful or interesting, please give it a star on GitHub — it really helps support the work and future improvements.

