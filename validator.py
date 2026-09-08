import collections
import re

def validate_answer(scrambled: str, answer: str) -> bool:
    """
    Validate that the generated answer is a valid unscrambling of the input word.
    """
    if not scrambled or not answer:
        return False
        
    # Strip whitespace and make uppercase
    scrambled = scrambled.upper().strip()
    answer = answer.upper().strip()
    
    # Remove any stray punctuation returned by the model (e.g. trailing period)
    answer = re.sub(r'[^A-Z]', '', answer)
    
    if not answer:
        return False
        
    # Check length
    if len(scrambled) != len(answer):
        return False
        
    # Check if exact multiset of letters matches
    return collections.Counter(scrambled) == collections.Counter(answer)
    
def normalize_answer(answer: str) -> str:
    """
    Normalizes the answer to just uppercase letters, removing formatting or punctuation.
    """
    if not answer:
        return ""
    return re.sub(r'[^A-Z]', '', answer.upper().strip())
