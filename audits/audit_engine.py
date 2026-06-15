from statements.models import Transaction,Statement
from django.db.models import Max, Min, Sum
from audits.ai_audit import generate_ai_audit


MIN_SUBSCRIPTION_DURATION_DAYS = 60
MIN_ANOMALY_SAMPLE_SIZE = 10
ANOMALY_STD_MULTIPLIER = 2
EMI_KEYWORDS = ["emi", "loan", "finance", "repayment"]

ESSENTIAL_CATEGORIES = [
    "Bills",
    "Rent",
    "Utilities",
    "Groceries",
    "Transport",
    "EMI",
    "Healthcare"
]

DISCRETIONARY_CATEGORIES = [
    "Shopping",
    "Entertainment",
    "Food",
    "Travel",
    "Subscription"
]


def get_audit_context(statement_id):
    """
    Build audit context metadata for a statement.

    This function gathers high-level information about the uploaded statement,
    such as total transaction count and statement duration.

    Purpose:
    - Helps detectors decide whether enough data exists
    - Subscription detection uses duration_days
    - AI audit can use context for confidence-aware reasoning

    Returns:
    dict containing:
    - transaction_count
    - start_date
    - end_date
    - duration_days
    """
    transactions = Transaction.objects.filter(statement_id=statement_id)
    transaction_count = transactions.count()

    date_info = transactions.aggregate(
        start_date=Min("date"),
        end_date=Max("date")
    )

    start_date = date_info["start_date"]
    end_date = date_info["end_date"]

    if start_date and end_date:
        duration_days = (end_date - start_date).days + 1
    else:
        duration_days = 0

    if duration_days < 30:
        audit_confidence = "low"
        warning = "Statement covers less than 30 days. Insights may be less reliable."
    elif duration_days < 90:
        audit_confidence = "medium"
        warning = "Statement covers less than 3 months. Trend-based insights may be limited."
    else:
        audit_confidence = "high"
        warning = None

    return {
        "transaction_count": transaction_count,
        "start_date": str(start_date) if start_date else None,
        "end_date": str(end_date) if end_date else None,
        "duration_days": duration_days,
        "audit_confidence": audit_confidence,
        "warning": warning,
    }


def calculate_cashflow(statement_id,context):
    """
    Calculate core cashflow metrics.

    Computes:
    - total_credit
    - total_debit
    - net_savings
    - savings_rate
    """
    total_credit = Transaction.objects.filter(
        statement_id=statement_id,
        transaction_type="credit"
    ).aggregate(total=Sum("amount"))["total"] or 0

    total_debit = Transaction.objects.filter(
        statement_id=statement_id,
        transaction_type="debit"
    ).aggregate(total=Sum("amount"))["total"] or 0

    net_savings = total_credit - total_debit

    if total_credit > 0:
        savings_rate = (net_savings / total_credit) * 100
    else:
        savings_rate = 0

    return {
        "total_credit": float(total_credit),
        "total_debit": float(total_debit),
        "net_savings": float(net_savings),
        "savings_rate": round(float(savings_rate), 2),
    }


def calculate_category_breakdown(statement_id):
    """
    Calculate spending distribution by category.

    Groups debit transactions by category and sums transaction amounts.

    Example output:
    {
        "Food": 3200,
        "Shopping": 8700
    }
    """
    category_data = (
        Transaction.objects.filter(
            statement_id=statement_id,
            transaction_type="debit"
        )
        .values("category")
        .annotate(total=Sum("amount"))
    )

    breakdown = {}

    for item in category_data:
        category = item["category"] or "Uncategorized"
        breakdown[category] = float(item["total"])

    return breakdown


def detect_duplicates(statement_id):
    """
    Detect possible duplicate charges.

    A transaction is flagged as a possible duplicate if:
    - transaction_type is debit
    - same date
    - same vendor
    - same amount

    Important:
    This detects suspicious repeated charges,
    not confirmed fraud.

    Purpose:
    Helps identify accidental double charges or suspicious billing.
    """
    transactions = Transaction.objects.filter(
        statement_id=statement_id,
        transaction_type="debit"
    )

    groups = {}

    for tx in transactions:
        normalized_vendor = tx.vendor.lower().strip()
        key = (tx.date, normalized_vendor, tx.amount)

        if key in groups:
            groups[key].append(tx)
        else:
            groups[key] = [tx]

    duplicates = []

    for group in groups.values():
        if len(group) > 1:
            group_data = []

            for tx in group:
                group_data.append({
                    "date": str(tx.date),
                    "vendor": tx.vendor,
                    "amount": float(tx.amount),
                    "category": tx.category,
                    "raw_description": tx.raw_description,
                })

            duplicates.append(group_data)

    return duplicates


def detect_subscriptions(statement_id, context):
    """
    Detect recurring subscription-like payments.

    Conditions:
    - Statement duration must be at least 60 days
    - Same vendor
    - Same amount
    - Appears in at least 2 unique months

    Example:
    Netflix ₹499 in Jan and Feb -> likely subscription

    Purpose:
    Identifies recurring monthly expenses such as
    streaming, SaaS, or membership payments.
    """
    if context["duration_days"] < MIN_SUBSCRIPTION_DURATION_DAYS:
        return []

    transactions = Transaction.objects.filter(
        statement_id=statement_id,
        transaction_type="debit"
    )

    groups = {}

    for tx in transactions:
        normalized_vendor = tx.vendor.lower().strip()
        key = (normalized_vendor, tx.amount)

        if key in groups:
            groups[key].append(tx)
        else:
            groups[key] = [tx]

    subscriptions = []

    for group in groups.values():
        if len(group) >= 2:
            unique_months = set()

            for tx in group:
                unique_months.add((tx.date.year, tx.date.month))

            if len(unique_months) >= 2:
                sample = group[0]

                subscriptions.append({
                    "vendor": sample.vendor,
                    "amount": float(sample.amount),
                    "occurrences": len(group),
                    "months_detected": len(unique_months),
                    "category": sample.category
                })

    return subscriptions


def detect_emi(statement_id, context):
    """
    Detect recurring EMI / loan repayment transactions.

    Conditions:
    - Statement duration must be at least 60 days
    - Transaction description contains EMI-related keywords
    - Same vendor + same amount recurring across months

    Purpose:
    Identifies debt obligations such as loan EMIs or finance payments.
    """
    if context["duration_days"] < MIN_SUBSCRIPTION_DURATION_DAYS:
        return {
        "detected": False,
        "total_monthly_emi": 0,
        "loans": []
                }

    transactions = Transaction.objects.filter(
    statement_id=statement_id,
    transaction_type="debit"
    )

    emi_candidates = []

    for tx in transactions:
        text = f"{tx.vendor} {tx.raw_description or ''}".lower()

        if any(keyword in text for keyword in EMI_KEYWORDS):
            emi_candidates.append(tx)

    groups = {}

    for tx in emi_candidates:
        normalized_vendor = tx.vendor.lower().strip()
        key = (normalized_vendor, tx.amount)

        if key in groups:
            groups[key].append(tx)
        else:
            groups[key] = [tx]
    
    loans = []
    total_monthly_emi = 0

    for group in groups.values():
        unique_months = set()

        for tx in group:
            unique_months.add((tx.date.year, tx.date.month))

        if len(unique_months) >= 2:
            sample = group[0]

            loan = {
                    "vendor": sample.vendor,
                    "amount": float(sample.amount),
                    "months_detected": len(unique_months)
                    }
                
            loans.append(loan)
            total_monthly_emi += float(sample.amount)

    return {
    "detected": len(loans) > 0,
    "total_monthly_emi": total_monthly_emi,
    "loans": loans
        }

def calculate_spending_profile(category_breakdown):
    """
    Calculate essential vs discretionary spending ratios.

    Essential spending:
    Mandatory or necessary expenses such as bills, rent, utilities,
    groceries, healthcare, and EMI.

    Discretionary spending:
    Non-essential lifestyle spending such as shopping, food delivery,
    entertainment, travel, and subscriptions.

    Purpose:
    Helps AI understand whether spending is necessity-driven
    or lifestyle-driven.
    """
    essential_spend = 0
    discretionary_spend = 0

    for category, amount in category_breakdown.items():
        if category in ESSENTIAL_CATEGORIES:
            essential_spend += amount
        elif category in DISCRETIONARY_CATEGORIES:
            discretionary_spend += amount
        else:
            discretionary_spend += amount

    total_spend = essential_spend + discretionary_spend

    if total_spend > 0:
        essential_ratio = (essential_spend / total_spend) * 100
        discretionary_ratio = (discretionary_spend / total_spend) * 100
    else:
        essential_ratio = 0
        discretionary_ratio = 0

    return {
        "essential_spend": round(float(essential_spend), 2),
        "discretionary_spend": round(float(discretionary_spend), 2),
        "essential_ratio": round(float(essential_ratio), 2),
        "discretionary_ratio": round(float(discretionary_ratio), 2)
    }


def detect_anomalies(statement_id):
    """
    Detect unusually high spending transactions.

    Uses statistical anomaly detection:
        threshold = mean + (2 * standard deviation)

    A transaction is flagged if:
        amount > threshold

    Notes:
    - Only debit transactions are analyzed
    - Detects unusual spending, not fraud

    Purpose:
    Highlights large transactions that may need attention.
    """
    transactions = list(
        Transaction.objects.filter(
            statement_id=statement_id,
            transaction_type="debit"
        )
    )

    if len(transactions) < MIN_ANOMALY_SAMPLE_SIZE:
        return []

    amounts = [float(tx.amount) for tx in transactions]

    if not amounts:
        return []

    mean = sum(amounts) / len(amounts)

    variance = sum((x - mean) ** 2 for x in amounts) / len(amounts)

    std_dev = variance ** 0.5

    threshold = mean + (ANOMALY_STD_MULTIPLIER * std_dev)

    anomalies = []

    for tx in transactions:
        if float(tx.amount) > threshold:
            anomalies.append({
                "date": str(tx.date),
                "vendor": tx.vendor,
                "amount": float(tx.amount),
                "category": tx.category,
                "threshold": round(threshold, 2)
            })

    return anomalies


def run_audit(statement_id):
    """
    Main Layer A audit orchestrator.

    Runs all feature extraction modules:
    - audit context
    - cashflow analysis
    - spending analysis
    - risk detectors

    Combines all outputs into a structured audit JSON.

    Purpose:
    Produces deterministic financial intelligence for Layer B (Gemini).
    """
    context = get_audit_context(statement_id)

    cashflow = calculate_cashflow(statement_id,context)

    category_breakdown = calculate_category_breakdown(statement_id)
    spending_profile = calculate_spending_profile(category_breakdown)

    spending = {
        "category_breakdown": category_breakdown,
        "spending_profile": spending_profile
              }

    risks = {
        "duplicates": detect_duplicates(statement_id),
        "subscriptions": detect_subscriptions(statement_id, context),
        "anomalies": detect_anomalies(statement_id),
        "emi":detect_emi(statement_id, context)
    }

    analytics= {
        "audit_context": context,
        "cashflow": cashflow,
        "spending": spending,
        "risks": risks
    }
    return analytics

def run_full_audit(statement_id):
    """
    Execute complete FinSight audit pipeline.
        -> Layer A deterministic analytics
        -> Save analytics to database
        -> Layer B Gemini auditing
        -> Save AI audit to database
    """

    statement = Statement.objects.get(id=statement_id)

    try:
        analytics = run_audit(statement_id)

        statement.analytics = analytics
        statement.audit_status = "analytics_ready"
        statement.save()

        ai_result = generate_ai_audit(analytics)

        statement.ai_audit = ai_result
        statement.audit_status = "completed"
        statement.save()

        return {
            "analytics": analytics,
            "ai_audit": ai_result
        }

    except Exception as e:
        statement.audit_status = "failed"
        statement.save()
        raise e 

