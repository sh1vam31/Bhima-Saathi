import re

HINGLISH_WORDS = {
    "kya", "kab", "hai", "kar", "karo", "mera", "meri", "batao", 
    "nahi", "paisa", "kaise", "chahiye", "bhai", "haan", "expire",
    "hogi", "renew", "karein", "diya", "di", "raha", "gaya"
}

def detect_language(text: str, prev: str = None) -> str:
    """
    Detects language based on simple heuristics from PRD C9.
    Returns: 'hi' (Devanagari), 'hinglish', or 'en' (English).
    """
    if not text:
        return prev or "en"
        
    text_lower = text.lower()
    
    # 1. Hindi (Devanagari)
    hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    if len(text) > 0 and (hindi_chars / len(text)) > 0.3:
        return "hi"
        
    # 4. Short or ambiguous keeps previous
    tokens = re.findall(r'\b\w+\b', text_lower)
    if len(tokens) <= 1 and prev:
        return prev
        
    # 2. Hinglish
    hinglish_count = sum(1 for t in tokens if t in HINGLISH_WORDS)
    if hinglish_count >= 2 or (len(tokens) > 0 and (hinglish_count / len(tokens)) >= 0.25):
        return "hinglish"
        
    # 3. English otherwise
    return "en"
