import pandas as pd
import pdfplumber as pl
from .models import Transaction
from django.conf import settings
import time
import re
from services.llm import get_llm_provider

from pydantic import BaseModel,Field
from financial_engine.pii_redactor import redact_sensitive_info

#schema for gemini using pydantic
class ExtractedTransaction(BaseModel):
    """Defines what fields MUST exist for a single row."""
    date: str = Field(description="The date of the transaction in YYYY-MM-DD format.")
    vendor: str = Field(description="The vendor, merchant, or description of who was paid.")
    amount: float = Field(description="The transaction amount as a numeric float value.")
    transaction_type: str = Field(description="Either credit or debit.")
    raw_description: str = Field(description="Original transaction description exactly as seen in statement.")


class StatementData(BaseModel):
    """Defines that Gemini must return a wrapper list called 'transactions'."""
    transactions: list[ExtractedTransaction]





# =========================================================
def parse_statement(statement):
    file_path = statement.file.path

    if not statement.file.name.lower().endswith('.pdf'):
        raise ValueError("Only PDF files supported")

    import os
    mock_parser = getattr(settings, "MOCK_PARSER", True) or not getattr(settings, "GEMINI_API_KEY", None)

    if mock_parser:
        time.sleep(1.5)
        
        from .generate_data import generate_transactions
        
        mock_txs = generate_transactions()
        parsed_count = 0
        for tx in mock_txs:
            extracted_date = pd.to_datetime(tx["date"]).date()
            extracted_vendor = tx["vendor"].strip() if tx["vendor"] else "Unknown"
            extracted_amount = tx["amount"]
            extracted_category = tx["category"].strip() if tx["category"] else "Other"
            
            extracted_type = "debit"
            if extracted_category == "Income":
                extracted_type = "credit"
            
            Transaction.objects.create(
                statement=statement,
                date=extracted_date,
                vendor=extracted_vendor,
                amount=extracted_amount,
                category=extracted_category,
                transaction_type=extracted_type,
                raw_description=f"MOCK: {extracted_vendor}"
            )
            parsed_count += 1
            
        if parsed_count > 0:
            statement.is_parsed = True
            statement.save()
            
        return parsed_count

    raw_text = ""
    try:
        with pl.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    raw_text += page_text + "\n"
    except Exception as e:
        print(f"PdfPlumber failed! :{e}")
        return 0

    if not raw_text.strip():
        return 0

    # Redact sensitive PII before transmitting to external API
    redacted_text = redact_sensitive_info(raw_text)

    # SEND TO GEMINI & SAVE TO DATABASE
    provider = get_llm_provider(
        operation="parse_statement",
        statement_id=statement.id,
        user_id=statement.user.id
    )

    prompt = f"""
            You are a financial statement parser.

            Extract ALL transactions from the bank statement text.

            Return JSON in this exact schema.

            Each transaction must contain:
            - date (YYYY-MM-DD)
            - vendor (clean short merchant name)
            - amount (numeric only)
            - transaction_type (ONLY 'credit' or 'debit')
            - raw_description (original text from statement row)

            Rules:
        1. Money entering account = credit
          Examples: salary, refund, deposit

        2. Money leaving account = debit
            Examples: purchase, transfer, UPI payment, card payment

        3. Preserve original transaction text in raw_description.

        Bank statement text:
        {redacted_text}
        """

    result = provider.generate_content(prompt=prompt, schema=StatementData)
    
    try:
        transactions = result.get("transactions", [])
        if not transactions:
            print("No transactions extracted from Gemini.")
            return 0
        parsed_count = 0

        for tx in transactions:
            extracted_date = pd.to_datetime(tx.date).date()
            extracted_vendor = tx.vendor.strip() if tx.vendor else "Unknown"
            extracted_amount = tx.amount
            extracted_category = "Uncategorized" # Categories will be handled by the Financial Intelligence Engine
            extracted_type = (
                tx.transaction_type.lower().strip()
                if tx.transaction_type else "debit"
            )

            if extracted_type not in ["credit", "debit"]:
                extracted_type = "debit"

            extracted_raw = (
                tx.raw_description.strip()
                if tx.raw_description else extracted_vendor
            )

            Transaction.objects.create(
                statement=statement,
                date=extracted_date,
                vendor=extracted_vendor,
                amount=extracted_amount,
                category=extracted_category,
                transaction_type=extracted_type,
                raw_description=extracted_raw,
            )
            parsed_count += 1

        if parsed_count > 0:
            statement.is_parsed = True
            statement.save()

        return parsed_count

    except Exception as e:
        print(f"Database insertion failed! :{e}")
        return 0