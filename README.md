# FinSight — AI-Powered Financial Statement Auditing Platform

FinSight allows users to securely upload PDF bank statements and receive automated financial analysis, risk detection, and AI-powered audit insights.
The project combines deterministic statement parsing with Gemini-backed AI audit and chatbot features, all served through a Django backend.

## Key Features

- PDF statement upload and secure backend file access
- Deterministic transaction extraction and analytics
- PII redaction before external AI processing
- Merchant normalization, duplicate detection, subscription/EMI detection, anomaly detection, and cashflow insights
- AI audit generation using Google Gemini (real or mock mode)
- Statement chatbot with retrieval-aware context
- JWT authentication via Django REST Framework and Simple JWT
- Frontend delivered through Django static files and `collectstatic`

## Architecture / Workflow

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

## Tech Stack

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

Live URL: https://finsight-pqcd.onrender.com

The current deployment is configured for Render with:
- Gunicorn
- Django staticfiles
- environment-driven settings
- PostgreSQL support

Build command:
```bash
pip install -r requirements.txt && ./build.sh
```

Start command:
```bash
gunicorn finsight.wsgi:application
```

## Deployment Limitations

- Render free services may spin down when idle, so the first request after inactivity can be slow.
- Free PostgreSQL instances are temporary and not intended for permanent production storage.
- Uploaded PDF files stored on the app filesystem are ephemeral on free Render web services.
- This deployment is best suited for portfolio/demo purposes, not long-term production financial storage.

## Security / Privacy

- JWT authentication protects API access.
- Statement files are served through backend views and permission checks.
- PII is redacted before external AI processing.
- Secrets are loaded from environment variables.
- Production deployments should use `DEBUG=False`.

## Current Status

FinSight is an ongoing portfolio project with working PDF upload, parsing, analytics, AI audit, and chatbot interactions.
The app is integrated end-to-end, with remaining improvements focused on production persistence, deployment stability, and testing.

## Future Improvements

- Persistent production storage for uploaded statements
- Permanent PostgreSQL deployment
- Improved deployment infrastructure and monitoring
- Expanded chatbot retrieval and context handling
- Stronger automated tests and validation

## License

No license has been specified yet.
