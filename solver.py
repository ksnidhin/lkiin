import asyncio
import logging
from groq import AsyncGroq
from config import GROQ_API_KEY
from validator import normalize_answer

client = AsyncGroq(api_key=GROQ_API_KEY)

async def solve_word(scrambled: str) -> str | None:
    """
    Sends the scrambled word to Groq API and returns the normalized answer.
    Optimized for minimum latency.
    """
    try:
        completion = await asyncio.wait_for(
            client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"Unscramble this word.\n\nLetters: {scrambled}\n\nReturn ONLY the single English word.\nNo explanation.\nNo punctuation."
                    }
                ],
                model="groq/compound-mini",
                temperature=0.0,
                max_tokens=20,
            ),
            timeout=5.0
        )
        answer = completion.choices[0].message.content
        return normalize_answer(answer)
    except asyncio.TimeoutError:
        logging.error("Groq API timeout")
        return None
    except Exception as e:
        logging.error(f"Groq API error: {e}")
        return None
