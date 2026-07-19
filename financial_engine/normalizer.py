import re

def normalize_vendor_name(vendor: str) -> str:
    """
    Cleans and normalizes merchant/vendor names by removing common payment gateway 
    artifacts, dates, transaction IDs, and special characters.
    
    Example:
    'UPI/PAYTM/123456/Swiggy' -> 'swiggy'
    'NETFLIX INC 12-05' -> 'netflix'
    """
    if not vendor:
        return "unknown"
        
    vendor = vendor.lower().strip()
    
    # Remove common UPI/banking prefixes and suffixes
    patterns_to_remove = [
        r'^upi[/-]',
        r'^pos[/-]',
        r'^atm[/-]',
        r'^neft[/-]',
        r'^imps[/-]',
        r'^rtgs[/-]',
        r'^ach[/-]',
        r'^ecs[/-]',
        r'[\b_-]ref[\b_-]',
    ]
    for pattern in patterns_to_remove:
        vendor = re.sub(pattern, '', vendor)

    # Remove UPI transaction IDs or similar numeric/alphanumeric IDs that often appear separated by slashes
    # E.g. /1234567890/ or /PAYTM/
    parts = vendor.split('/')
    if len(parts) > 1:
        # Keep the most meaningful part. Often the last or second to last is the actual merchant.
        # Let's filter out parts that are purely numeric or common bank terms.
        meaningful_parts = [p for p in parts if not re.match(r'^\d+$', p) and p not in ['upi', 'paytm', 'phonepe', 'gpay', 'cred']]
        if meaningful_parts:
            # Often the merchant name is the longest string or the last string.
            vendor = meaningful_parts[-1]
        else:
            vendor = parts[-1]
            
    # Remove dates (e.g. 12-05, 2023, 12MAY)
    vendor = re.sub(r'\b\d{2}[-/]\d{2}\b', '', vendor)
    vendor = re.sub(r'\b\d{2}[a-z]{3}\b', '', vendor)
    vendor = re.sub(r'\b20\d{2}\b', '', vendor)

    # Remove extra whitespace and special characters
    vendor = re.sub(r'[^a-z0-9\s]', ' ', vendor)
    vendor = re.sub(r'\s+', ' ', vendor).strip()
    
    # Remove common business suffixes if they're standalone
    suffixes = ['ltd', 'pvt', 'inc', 'llp', 'co']
    words = vendor.split()
    words = [w for w in words if w not in suffixes]
    vendor = ' '.join(words)
    
    return vendor or "unknown"
