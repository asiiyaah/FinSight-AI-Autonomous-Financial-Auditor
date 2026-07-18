from typing import Dict, Any, List
from datetime import date

PROMPT_TEMPLATE = """SYSTEM INSTRUCTIONS
-------------------
You are FinSight, an AI financial assistant.

Only answer using the supplied statement context.

If the requested information is not available, reply exactly:
"I don't have enough information from this statement."

Do not infer.
Do not estimate.
Do not assume.
Never mention internal implementation, JSON, databases, or retrieval.

Current Date: {current_date}

CONTEXT
-------------------
{formatted_context}

USER QUESTION
-------------------
{user_message}

Answer Requirements:
- Respond in Markdown.
- Use bullet points when appropriate.
- Quote amounts exactly.
- Keep responses under 250 words unless asked otherwise.

Answer:"""


def format_currency(amount: Any) -> str:
    """Formats amounts cleanly, e.g., ₹12,345.67"""
    try:
        amount = float(amount)
        return f"₹{amount:,.2f}"
    except (ValueError, TypeError):
        return "₹0.00"


def format_metadata(context: Dict[str, Any]) -> str:
    metadata = context.get("metadata", {})
    if not metadata:
        return ""
    lines = ["Metadata:"]
    if "filename" in metadata:
        lines.append(f"- File Name: {metadata['filename']}")
    if "uploaded_at" in metadata:
        lines.append(f"- Uploaded: {metadata['uploaded_at']}")
    if "transaction_count" in metadata:
        lines.append(f"- Total Transactions: {metadata['transaction_count']}")
    if "duration_days" in metadata:
        lines.append(f"- Statement Duration: {metadata['duration_days']} days")
    return "\n".join(lines)


def format_ai_summary(context: Dict[str, Any]) -> str:
    ai_summary = context.get("ai_summary", {})
    if not ai_summary:
        return ""
    lines = ["AI Summary:"]
    if ai_summary.get("overall_summary"):
        lines.append(f"- Summary: {ai_summary['overall_summary']}")
    if ai_summary.get("final_verdict"):
        lines.append(f"- Verdict: {ai_summary['final_verdict']}")
    return "\n".join(lines) if len(lines) > 1 else ""


def format_cashflow(context: Dict[str, Any]) -> str:
    cashflow = context.get("cashflow", {})
    if not cashflow:
        return ""
    lines = [
        "Cashflow:",
        f"- Income (Credit): {format_currency(cashflow.get('total_credit', 0))}",
        f"- Expenses (Debit): {format_currency(cashflow.get('total_debit', 0))}",
        f"- Net Savings: {format_currency(cashflow.get('net_savings', 0))}",
        f"- Savings Rate: {cashflow.get('savings_rate', 0)}%"
    ]
    return "\n".join(lines)


def format_categories(context: Dict[str, Any]) -> str:
    category_breakdown = context.get("category_breakdown", {})
    spending_profile = context.get("spending_profile", {})
    if not category_breakdown and not spending_profile:
        return ""
    
    lines = []
    if category_breakdown:
        lines.append("Category Breakdown:")
        for cat, amount in category_breakdown.items():
            lines.append(f"- {cat}: {format_currency(amount)}")
            
    if spending_profile:
        if lines:
            lines.append("") # Blank line separator
        lines.append("Spending Profile:")
        lines.append(f"- Essential Spend: {format_currency(spending_profile.get('essential_spend', 0))} ({spending_profile.get('essential_ratio', 0)}%)")
        lines.append(f"- Discretionary Spend: {format_currency(spending_profile.get('discretionary_spend', 0))} ({spending_profile.get('discretionary_ratio', 0)}%)")
        
    return "\n".join(lines)


def format_subscriptions(context: Dict[str, Any]) -> str:
    subscriptions = context.get("subscriptions", [])
    if not subscriptions:
        return ""
    lines = ["Subscriptions:"]
    for sub in subscriptions:
        lines.append(f"- {sub.get('vendor', 'Unknown')}: {format_currency(sub.get('amount', 0))} (Found {sub.get('occurrences', 0)} times)")
    return "\n".join(lines)


def format_emi(context: Dict[str, Any]) -> str:
    emi = context.get("emi", {})
    if not emi or not emi.get("detected"):
        return ""
    lines = [f"EMIs/Loans (Total Monthly: {format_currency(emi.get('total_monthly_emi', 0))}):"]
    for loan in emi.get("loans", []):
        lines.append(f"- {loan.get('vendor', 'Unknown')}: {format_currency(loan.get('amount', 0))}")
    return "\n".join(lines)


def format_anomalies(context: Dict[str, Any]) -> str:
    anomalies = context.get("anomalies", [])
    duplicates = context.get("duplicates", [])
    if not anomalies and not duplicates:
        return ""
        
    lines = []
    if anomalies:
        lines.append("Anomalies (High-value transactions):")
        for anomaly in anomalies:
            lines.append(f"- {anomaly.get('date', '')} – {anomaly.get('vendor', 'Unknown')} – {format_currency(anomaly.get('amount', 0))}")
    
    if duplicates:
        if lines:
            lines.append("")
        lines.append("Possible Duplicate Transactions:")
        for idx, group in enumerate(duplicates, 1):
            lines.append(f"Group {idx}:")
            for tx in group:
                lines.append(f"  - {tx.get('date', '')} – {tx.get('vendor', 'Unknown')} – {format_currency(tx.get('amount', 0))}")
                
    return "\n".join(lines)


def format_recommendations(context: Dict[str, Any]) -> str:
    recommendations = context.get("recommendations", [])
    strengths = context.get("strengths", [])
    concerns = context.get("concerns", [])
    
    if not recommendations and not strengths and not concerns:
        return ""
    
    lines = []
    if strengths:
        lines.append("Strengths:")
        for s in strengths:
            lines.append(f"- {s}")
    
    if concerns:
        if lines: lines.append("")
        lines.append("Concerns:")
        for c in concerns:
            lines.append(f"- {c}")
            
    if recommendations:
        if lines: lines.append("")
        lines.append("Recommendations:")
        for r in recommendations:
            lines.append(f"- {r}")
            
    return "\n".join(lines)


def format_transactions(context: Dict[str, Any]) -> str:
    transactions = context.get("transactions", [])
    if not transactions:
        return ""
        
    # Cap transactions to prevent massive prompt overflow
    capped_transactions = transactions[:30]
    
    lines = [f"Transactions (Showing {len(capped_transactions)}):"]
    for tx in capped_transactions:
        tx_type = tx.get('type', '').upper()
        lines.append(f"- {tx.get('date', '')} – {tx.get('vendor', 'Unknown')} – {format_currency(tx.get('amount', 0))} ({tx_type})")
        
    return "\n".join(lines)


# Formatter Registry
FORMATTERS = [
    format_metadata,
    format_ai_summary,
    format_cashflow,
    format_categories,
    format_subscriptions,
    format_emi,
    format_anomalies,
    format_recommendations,
    format_transactions
]


def build_prompt(user_message: str, context: Dict[str, Any]) -> str:
    """
    Constructs the final prompt string to be passed to the LLM.
    Uses registered formatters to transform structured context into readable text.
    """
    sections = []
    
    # Iterate through all formatters dynamically
    for formatter in FORMATTERS:
        section_text = formatter(context)
        if section_text:
            sections.append(section_text)
            
    # Combine sections with double newlines
    formatted_context = "\n\n".join(sections)
    if not formatted_context.strip():
        formatted_context = "No relevant context found."
        
    current_date = date.today().strftime("%d %B %Y")
        
    # Inject into template
    return PROMPT_TEMPLATE.format(
        current_date=current_date,
        formatted_context=formatted_context,
        user_message=user_message
    )
