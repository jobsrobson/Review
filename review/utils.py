from datetime import datetime

def ui_to_db_date(date_str):
    """Converts DD/MM/AAAA to YYYY-MM-DD."""
    try:
        return datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
    except ValueError:
        return date_str

def db_to_ui_date(date_str):
    """Converts YYYY-MM-DD to DD/MM/AAAA."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d/%m/%Y')
    except ValueError:
        return date_str

import unicodedata

def normalize_str(text):
    """Removes accents and converts to lowercase for search comparison."""
    if not text:
        return ""
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn').lower()
