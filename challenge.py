import re

def is_challenge(text: str) -> bool:
    """
    Detect if a message is a scrambled word challenge.
    Looks for the primary identifier in the text.
    """
    if not text:
        return False
    return "scrambled word challenge!" in text.lower()

def extract_word(text: str) -> str | None:
    """
    Extract the scrambled word from the challenge text.
    Expected format is similar to: 'Word: UFTTIO'
    """
    if not text:
        return None
        
    # Handle variations like "Word: UFTTIO", "*Word:* **UFTTIO**"
    # Also support "Letters: UFTTIO" or "Unscramble: UFTTIO"
    patterns = [
        r"(?:word|letters|unscramble|scrambled)\s*\**:\**\s*\**([a-zA-Z]+)(?:[\s*:]|$)",
        r"🔤\s*\**([a-zA-Z]+)\**",  # Sometimes they just put the emoji then the word
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            word = match.group(1).upper().strip()
            if word.isalpha():
                return word
                
    return None
