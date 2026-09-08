import asyncio
import time
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
    
    model_name = "openai/gpt-oss-20b"
    logging.info(f"[GROQ] Model: {model_name}")
    
    max_retries = 1
    timeout_secs = 4.0
    
    for attempt in range(max_retries + 1):
        if attempt > 0:
            logging.info(f"[GROQ] Retry #{attempt}")
            
        logging.info("[GROQ] Sending request...")
        start_time = time.time()
        
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
                timeout=timeout_secs
            )
            
            elapsed = time.time() - start_time
            logging.info(f"[GROQ] Response received in {elapsed:.2f}s")
            
            if attempt > 0:
                logging.info("[GROQ] Retry succeeded")
                
            answer = completion.choices[0].message.content
            parsed = normalize_answer(answer)
            logging.info(f"[GROQ] Parsed answer: {parsed}")
            return parsed
            
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            logging.error(f"[GROQ] Timeout after {elapsed:.2f}s")
            continue
        except Exception as e:
            logging.error(f"[GROQ] API error: {e}")
            break
            
    logging.error("[GROQ] All attempts failed.")
    return None
