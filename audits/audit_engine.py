import datetime
from django.utils import timezone
from statements.models import Transaction, Statement
from django.db.models import Max, Min
from audits.ai_audit import generate_ai_audit
from financial_engine.normalizer import normalize_vendor_name
from financial_engine.categorizer import batch_categorize_vendors
from financial_engine.detectors.duplicates import detect_duplicates
from financial_engine.detectors.subscriptions import detect_subscriptions
from financial_engine.detectors.emi import detect_emi
from financial_engine.detectors.anomalies import detect_anomalies
from financial_engine.detectors.recurring_bills import detect_recurring_bills
from financial_engine.detectors.cashflow import calculate_cashflow
from financial_engine.detectors.spending import calculate_spending
from financial_engine.detectors.salary import detect_salary

def get_audit_context(transactions_qs):
    transaction_count = transactions_qs.count()
    date_info = transactions_qs.aggregate(
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

def run_audit(statement_id):
    """
    Main Layer A audit orchestrator (Financial Intelligence Engine).
    Creates the structured Financial Intelligence Object.
    """
    qs = Transaction.objects.filter(statement_id=statement_id)
    
    # 1. Context
    context = get_audit_context(qs)
    
    # 2. Extract into Dicts, Normalize, Categorize
    txs = list(qs)
    vendors = [tx.vendor for tx in txs]
    normalized_vendors = [normalize_vendor_name(v) for v in vendors]
    
    # Categorize all unknown vendors in bulk
    categories_map = batch_categorize_vendors(normalized_vendors)
    
    tx_dicts = []
    for tx, norm_vendor in zip(txs, normalized_vendors):
        # Apply category and save to DB
        cat_info = categories_map.get(norm_vendor, {"category": "Uncategorized", "source": "deterministic", "confidence": 0.0})
        
        # Update category on transaction if it was uncategorized or different
        if tx.category != cat_info["category"]:
            tx.category = cat_info["category"]
            tx.save(update_fields=["category"])
            
        tx_dicts.append({
            "id": tx.id,
            "date": tx.date,
            "vendor": tx.vendor,
            "normalized_vendor": norm_vendor,
            "amount": float(tx.amount),
            "category": tx.category,
            "transaction_type": tx.transaction_type,
            "raw_description": tx.raw_description,
        })
        
    # 3. Detectors
    cashflow = calculate_cashflow(tx_dicts)
    spending = calculate_spending(tx_dicts)
    salary = detect_salary(tx_dicts)
    
    risks = {
        "duplicates": detect_duplicates(tx_dicts),
        "subscriptions": detect_subscriptions(tx_dicts, context),
        "recurring_bills": detect_recurring_bills(tx_dicts, context),
        "anomalies": detect_anomalies(tx_dicts),
        "emi": detect_emi(tx_dicts, context)
    }
    
    metadata = {
        "schema_version": "1.1",
        "generated_at": timezone.now().isoformat(),
        "statement_id": statement_id
    }
    
    analytics = {
        "metadata": metadata,
        "audit_context": context,
        "cashflow": cashflow,
        "spending": spending,
        "income": salary,
        "risks": risks
    }
    return analytics

def run_full_audit(statement_id):
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
