# FinSight: Autonomous Financial Auditor 🚀

FinSight is a sophisticated, AI-assisted financial auditing application that allows users to upload PDF bank statements and receive deep, actionable insights into their spending habits, recurring obligations, and financial risks. 

The system employs a strict two-layer architecture, separating deterministic financial logic from generative AI analysis to ensure absolute accuracy and prevent hallucinations.

---

## 🌟 Detailed Features

### 1. Financial Intelligence Engine (Deterministic Layer)
The core of FinSight is a highly modular, deterministic analytics engine. It acts as the single source of truth for all objective financial facts.
- **Strict PII Redaction**: Strips all Personal Identifiable Information (PII) before any data ever reaches the AI layer.
- **Intelligent Parsing**: Extracts raw transactional data directly from PDF bank statements.
- **Vendor Normalization & Categorization**: Cleans messy vendor strings and maps them to categories (*Groceries, Utilities, Entertainment*). Unknown vendors are automatically categorized using AI and cached in the database to optimize future audits.
- **Subscriptions vs. Recurring Bills**: Dynamically detects and isolates entertainment subscriptions (Netflix, Prime) from recurring utility bills (Electricity, Broadband) using intelligent confidence scoring (Category + Keywords + Recurrence Enrichment).
- **Loan & EMI Detection**: Explicitly identifies active monthly loan obligations and EMIs with strict gatekeeping (using exact keywords like *ECS, Installment*) to prevent false positives.
- **Duplicate Detection**: Flags identical charges happening on the same day.
- **Anomaly Detection**: Combines statistical IQR boundary analysis with hardcoded financial rules to flag unusual spending, large ATM withdrawals, and bank penalties.
- **Income & Cashflow Analysis**: Tracks primary salary sources, total inflows, outflows, and calculates overall cashflow health.

### 2. AI Audit Engine (Generative Layer)
Powered by Google Gemini, the AI Audit layer takes the structured *Financial Intelligence Object* produced by the deterministic engine and generates a comprehensive risk assessment.
- **Contextual Reasoning**: Generates a Final Verdict, Suspicious Activity list, and Actionable Recommendations.
- **Strict Guardrails**: The AI is strictly prohibited from doing math, recalculating anomalies, or identifying subscriptions. It acts purely as a financial advisor interpreting the facts.

### 3. Conversational AI Chatbot
- An integrated chat interface allows users to ask open-ended questions about their uploaded statement (e.g., *"How much did I spend on food this month?"* or *"Can I afford a new car?"*).
- The bot leverages contextual retrieval, seamlessly injecting the deterministic findings into the prompt to provide accurate, personalized advice.

### 4. Interactive Dashboard
- **Modern UI**: Built with HTML, Vanilla JavaScript, and Bootstrap.
- **Statement Lifecycle Management**: Upload, view, audit, and cleanly delete statements.
- **Visual Analytics**: Interactive tabs displaying Cashflow, Anomalies, Duplicates, Subscriptions, and EMIs.
- **Robust Error Handling**: Graceful frontend degradation, dynamic UI updates, and intelligent cleanup when background processing fails or statements go missing.

---

## 🛠 Tech Stack

**Backend**
- **Framework**: Django & Django REST Framework (DRF)
- **Database**: SQLite (Development) / PostgreSQL (Ready)
- **AI Integration**: Google Gemini API (`google-generativeai`)
- **Authentication**: JWT / Token-based authentication (Simple JWT)

**Frontend**
- **Core**: HTML5, Vanilla JavaScript, CSS3
- **Styling framework**: Bootstrap 5
- **Icons**: Bootstrap Icons

---

## ⚙️ How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/FinSight.git
   cd FinSight
   ```

2. **Set up the Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add your API keys:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Start the Django Backend:**
   ```bash
   python manage.py runserver
   ```

7. **Access the Application:**
   Open your browser and navigate to the frontend folder or host it locally (e.g., via VS Code Live Server). By default, the frontend interacts with `http://127.0.0.1:8000/api/v1/`.

---

## 🚀 What's Coming (Roadmap)

- [ ] **Multi-Month Trend Analysis**: Compare spending habits across multiple months and quarters.
- [ ] **Export to CSV/PDF**: Allow users to export the final AI audit and deterministic tables into beautiful PDF reports.
- [ ] **Support for More Banks**: Expanding the parser to support native PDF formats for 15+ major global banks without relying on OCR.
- [ ] **Custom Budgets**: Users can set budget limits on categories and the AI will track adherence.
- [ ] **Dockerization**: Easy 1-click deployment using Docker and Docker Compose.

---

### ⭐ If you found this useful, please consider giving the repository a star!
