import re

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
