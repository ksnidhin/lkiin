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
    logging.info(f"[GROQ] Preparing request for word: {scrambled}")
    logging.info(f"[GROQ] API key configured: {'YES' if GROQ_API_KEY else 'NO'}")
    
    model_name = "groq/compound-mini"
    logging.info(f"[GROQ] Model: {model_name}")
    logging.info(f"[GROQ] Sending request...")
    
    try:
        completion = await asyncio.wait_for(
            client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"Unscramble this word.\n\nLetters: {scrambled}\n\nReturn ONLY the single English word.\nNo explanation.\nNo punctuation."
                    }
                ],
                model=model_name,
                temperature=0.0,
                max_tokens=20,
            ),
            timeout=5.0
        )
        
        logging.info("[GROQ] Response received")
        answer = completion.choices[0].message.content
        parsed = normalize_answer(answer)
        logging.info(f"[GROQ] Parsed answer: {parsed}")
        return parsed
    except asyncio.TimeoutError:
        logging.error("[GROQ] Timeout waiting for API")
        return None
    except Exception as e:
        logging.error(f"[GROQ] API error: {e}")
        return None
