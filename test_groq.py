import asyncio
from solver import generate_guess
import logging
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def test_groq():
    words = {
        "eitragla": "TRIANGLE",
        "orcurc": "OCCUR",
        "ufttio": "OUTFIT",
        "aknte": "TAKEN"
    }
    
    for word, expected in words.items():
        print(f"\n[CHALLENGE] Challenge detected")
        print(f"[EXTRACT] {word}")
        answer = await generate_guess(word, "openai/gpt-oss-20b", set())
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
