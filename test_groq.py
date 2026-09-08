import asyncio
from solver import solve_word
import logging
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def test_groq():
    word = "DSELOT"
    print(f"Testing Groq independently with word: {word}")
    answer = await solve_word(word)
    print(f"Groq returned: {answer}")
    
    if answer == "OLDEST":
        print("SUCCESS! Groq is working perfectly.")
    else:
        print("FAILURE! Groq returned the wrong answer or failed.")

if __name__ == "__main__":
    asyncio.run(test_groq())
