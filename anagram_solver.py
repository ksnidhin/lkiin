import os
import urllib.request
import logging
from collections import defaultdict

WORDS_FILE = "words.txt"
WORDS_URL = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"

anagram_dict = defaultdict(list)

def init_dictionary():
    if not os.path.exists(WORDS_FILE):
        logging.info("Downloading word dictionary for local fallback...")
        try:
            urllib.request.urlretrieve(WORDS_URL, WORDS_FILE)
            logging.info("Dictionary downloaded successfully.")
        except Exception as e:
            logging.error(f"Failed to download dictionary: {e}")
            return
            
    try:
        with open(WORDS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().upper()
                if word:
                    # Signature is the sorted letters
                    key = "".join(sorted(word))
                    anagram_dict[key].append(word)
        logging.info(f"Local dictionary loaded with {len(anagram_dict)} unique letter signatures.")
    except Exception as e:
        logging.error(f"Failed to read local dictionary: {e}")

def solve_anagram_local(scrambled: str) -> str | None:
    """
    Instantly solves an anagram using a pre-indexed local dictionary.
    """
    if not scrambled:
        return None
        
    scrambled = scrambled.upper().strip()
    key = "".join(sorted(scrambled))
    
    matches = anagram_dict.get(key)
    if matches:
        return matches[0] # Return the first matching word
    return None

# Initialize on module import
init_dictionary()
