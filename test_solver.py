import pytest
import asyncio
from challenge import is_challenge, extract_word
from validator import validate_answer
from cache import ExpiringCache

def test_is_challenge():
    assert is_challenge("🌟 Scrambled Word Challenge! 🌟") == True
    assert is_challenge("scrambled word challenge!") == True
    assert is_challenge("Just a normal message") == False
    assert is_challenge("") == False

def test_extract_word():
    assert extract_word("🔤 Word: UFTTIO") == "UFTTIO"
    assert extract_word("Word: UFTTIO") == "UFTTIO"
    assert extract_word("word: ufttio") == "UFTTIO"
    assert extract_word("word: UFTTIO123") == None # regex expects whitespace or end of string after word
    assert extract_word("Word: UFTTIO\nSome other text") == "UFTTIO"
    assert extract_word("Unscramble: UFTTIO") == "UFTTIO"
    assert extract_word("🔤 UFTTIO") == "UFTTIO"
    assert extract_word("No word here") == None

def test_validate_answer():
    # Valid cases
    assert validate_answer("UFTTIO", "OUTFIT") == True
    assert validate_answer("AABBC", "CABBA") == True
    
    # Invalid cases
    assert validate_answer("UFTTIO", "HELLO") == False
    assert validate_answer("UFTTIO", "OUTLINE") == False
    assert validate_answer("AABBC", "ABC") == False # length mismatch
    assert validate_answer("AABBC", "ABBBC") == False # different multiset
    assert validate_answer("ABC", "ABCD") == False
    
    # Case normalization
    assert validate_answer("ufttio", "Outfit") == True
    
    # Stray formatting from model
    assert validate_answer("UFTTIO", "OUTFIT.") == True

@pytest.mark.asyncio
async def test_cache():
    cache = ExpiringCache(ttl=0.1)
    await cache.add("test_key")
    assert await cache.contains("test_key") == True
    
    await asyncio.sleep(0.2)
    assert await cache.contains("test_key") == False
