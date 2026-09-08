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
        
    # Handle variations like "Word: UFTTIO", "*Word:* **UFTTIO**", etc.
    # Require a colon after "word" to avoid matching random sentences
    match = re.search(r"word\s*\**:\**\s*\**([a-zA-Z]+)(?:[\s*:]|$)", text, re.IGNORECASE)
    if match:
        word = match.group(1).upper().strip()
        # Ensure it's purely alphabetic just in case
        if word.isalpha():
            return word
    return None
