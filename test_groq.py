import asyncio
from solver import solve_word
import logging
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def test_groq():
    words = {
        "IICMTV": "VICTIM",
        "CTAOUUIS": "CAUTIOUS",
        "DSELOT": "OLDEST"
    }
    
    for word, expected in words.items():
        print(f"\n[CHALLENGE] Challenge detected")
        print(f"[EXTRACT] {word}")
        answer = await solve_word(word)
        if answer:
            formatted_answer = answer.capitalize()
            print(f"[SOLVER] {answer}")
            print(f"[SEND] Sending answer: {formatted_answer}")
            
            if answer == expected and formatted_answer == expected.capitalize():
                print(f"[SEND] Success")
            else:
                print("FAILURE: Wrong answer returned.")
        else:
            print("FAILURE: Solver returned None.")

if __name__ == "__main__":
    asyncio.run(test_groq())
