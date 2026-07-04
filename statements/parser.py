import pandas as pd
import pdfplumber as pl
from .models import Transaction
from google import genai
from django.conf import settings
import time
import re

from pydantic import BaseModel,Field


#schema for gemini using pydantic
class ExtractedTransaction(BaseModel):
    """Defines what fields MUST exist for a single row."""
    date: str = Field(description="The date of the transaction in YYYY-MM-DD format.")
    vendor: str = Field(description="The vendor, merchant, or description of who was paid.")
    amount: float = Field(description="The transaction amount as a numeric float value.")
    category: str = Field(description="A clean category name like Food, Utilities, or Entertainment.")
    transaction_type: str = Field(description="Either credit or debit.")
    raw_description: str = Field(description="Original transaction description exactly as seen in statement.")


class StatementData(BaseModel):
    """Defines that Gemini must return a wrapper list called 'transactions'."""
    transactions: list[ExtractedTransaction]


def redact_sensitive_info(text: str) -> str:
    """
    Sanitize raw statement text to remove sensitive PII (emails, names, phone numbers,
    PAN, Aadhaar, account numbers) before transmission to external APIs.
    """
    # 1. Redact Customer Names / Account Names in headers (using non-newline whitespace [ \t])
    text = re.sub(
        r'(?i)(customer name|a/c holder|account name|holder|name)\s*:\s*([a-zA-Z \t]+)',
        lambda m: f"{m.group(1)}: [NAME_REDACTED]",
        text
    )
    
    # 2. Redact Addresses in headers
    text = re.sub(
        r'(?i)(address|residence|location)\s*:\s*([a-zA-Z0-9, \t\.\-\#\/]+)',
        lambda m: f"{m.group(1)}: [ADDRESS_REDACTED]",
        text
    )
    
    # 3. Redact Email Addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', text)
    
    # 4. Redact Phone / Mobile Numbers (matching optional leading + and country code prefixes)
    text = re.sub(r'\+?\b(?:\+?91|0)?[6-9]\d{9}\b', '[PHONE_REDACTED]', text)
    
    # 5. Redact Indian IFSC Codes
    text = re.sub(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', '[IFSC_REDACTED]', text)
    
    # 6. Redact PAN Card Numbers
    text = re.sub(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', '[PAN_REDACTED]', text)
    
    # 7. Redact Aadhaar Numbers
    text = re.sub(r'\b\d{4}\s\d{4}\s\d{4}\b', '[AADHAAR_REDACTED]', text)
    text = re.sub(r'\b\d{12}\b', '[AADHAAR_REDACTED]', text)
    
    # 8. Redact Potential Account Numbers / Credit Card Numbers (9 to 18 digits)
    text = re.sub(r'\b\d{9,18}\b', '[ACCOUNT_REDACTED]', text)
    
    return text


# =========================================================
def parse_statement(statement):
    file_path = statement.file.path

    if not statement.file.name.lower().endswith('.pdf'):
        raise ValueError("Only PDF files supported")

    import os
    mock_parser = os.getenv("MOCK_PARSER", "True").lower() == "true" or not getattr(settings, "GEMINI_API_KEY", None)

    if mock_parser:
        import time
        time.sleep(1.5)
        
        from .generate_data import generate_transactions
        import pandas as pd
        
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
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = f"""
            You are a financial statement parser.

            Extract ALL transactions from the bank statement text.

            Return JSON in this exact schema.

            Each transaction must contain:
            - date (YYYY-MM-DD)
            - vendor (clean short merchant name)
            - amount (numeric only)
            - category (Food, Bills, Shopping, Subscription, Transport, Income, Other)
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

    max_retries = 5
    retry_delay = 8
    response = None

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
                config=dict(
                    response_mime_type="application/json",
                    response_schema=StatementData,
                ),
            )
            # If successful, break out of the retry loop completely!
            break
        except Exception as e:
            # Catch temporary high-demand or rate limits
            if ("503" in str(e) or "429" in str(e)) and attempt < max_retries - 1:
                print(f"Gemini busy ({e}). Retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"Gemini processing failed! :{e}")
                return 0

    if not response:
        return 0

    try:
        result_data = response.parsed
        if not result_data or not result_data.transactions:
            print("No transactions extracted from Gemini.")
            return 0
        parsed_count = 0

        for tx in result_data.transactions:
            extracted_date = pd.to_datetime(tx.date).date()
            extracted_vendor = tx.vendor.strip() if tx.vendor else "Unknown"
            extracted_amount = tx.amount
            extracted_category = tx.category.strip() if tx.category else "Uncategorized"
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