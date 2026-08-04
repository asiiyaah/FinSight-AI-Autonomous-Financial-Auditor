# Centralized Merchant to Category Mapping

# We map normalized vendor names to their deterministic category.
MERCHANT_CATEGORY_MAP = {
    # Food
    'swiggy': 'Food',
    'zomato': 'Food',
    'mcdonalds': 'Food',
    'dominos': 'Food',
    'starbucks': 'Food',
    'kfc': 'Food',
    
    # Housing
    'rent': 'Housing',
    'house rent': 'Housing',
    'apartment rent': 'Housing',
    'flat rent': 'Housing',
    
    # Groceries
    'blinkit': 'Groceries',
    'zepto': 'Groceries',
    'instamart': 'Groceries',
    'bigbasket': 'Groceries',
    'dmart': 'Groceries',
    'reliance fresh': 'Groceries',
    
    # Utilities
    'bescom': 'Utilities',
    'adani electricity': 'Utilities',
    'bses': 'Utilities',
    'mahavitaran': 'Utilities',
    'jio': 'Utilities',
    'airtel': 'Utilities',
    'vi': 'Utilities',
    
    # Shopping
    'amazon': 'Shopping',
    'flipkart': 'Shopping',
    'myntra': 'Shopping',
    'ajio': 'Shopping',
    'nykaa': 'Shopping',
    
    # Entertainment & Subscriptions
    'netflix': 'Subscription',
    'amazon prime': 'Subscription',
    'spotify': 'Subscription',
    'spotify premium': 'Subscription',
    'hotstar': 'Subscription',
    'bookmyshow': 'Entertainment',
    'pvrcinemas': 'Entertainment',
    
    # Transport & Travel
    'uber': 'Transport',
    'ola': 'Transport',
    'rapido': 'Transport',
    'irctc': 'Travel',
    'makemytrip': 'Travel',
    'goibibo': 'Travel',
    'indigo': 'Travel',
    
    # Finance / EMI
    'bajaj finance': 'EMI',
    'hdfc bank loan': 'EMI',
    'sbi card': 'Credit Card Bill',
    'cred': 'Credit Card Bill',
    
    # Healthcare
    'apollo': 'Healthcare',
    'pharmeasy': 'Healthcare',
    'netmeds': 'Healthcare',
    '1mg': 'Healthcare',
    
    # Gaming
    'dream11': 'Gaming',
    'rummycircle': 'Gaming',
    'mpl': 'Gaming',
    
    # Bank Charges & ATM
    'atm cash withdrawal': 'ATM Withdrawal',
    'bank penalty': 'Bank Charges',
    'bank charges': 'Bank Charges',
    'service charge': 'Bank Charges',
    'unknown merchant': 'Uncategorized',
}

# Mapping of categories to high-level groups
ESSENTIAL_CATEGORIES = {
    'Utilities', 'Groceries', 'Transport', 'Healthcare', 'EMI', 'Housing', 'Bills'
}

DISCRETIONARY_CATEGORIES = {
    'Food', 'Shopping', 'Entertainment', 'Subscription', 'Travel', 'Gaming'
}
