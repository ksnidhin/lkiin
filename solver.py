import asyncio
import time
import logging
from groq import AsyncGroq
from config import GROQ_API_KEY
from validator import normalize_answer, validate_answer
import re

client = AsyncGroq(api_key=GROQ_API_KEY)

async def solve_word(scrambled: str) -> str | None:
    """
    Sends the scrambled word to Groq API and returns the normalized answer.
    Optimized for minimum latency with model fallbacks and internal validation.
    """
    logging.info(f"[GROQ] Preparing request for word: {scrambled}")
    logging.info(f"[GROQ] API key configured: {'YES' if GROQ_API_KEY else 'NO'}")
    
    primary_model = "openai/gpt-oss-20b"
    fallback_model = "groq/compound-mini"
    
    timeout_secs = 4.0
    
    attempts_plan = [
        ("Attempt 1", primary_model),
        ("Attempt 2", primary_model),
        ("Fallback", fallback_model)
    ]
    
    logging.info(f"[GROQ] Primary model: {primary_model}")
    
    for attempt_name, model_name in attempts_plan:
        if attempt_name == "Fallback":
            logging.info(f"[GROQ] Falling back to: {model_name}")
        else:
            logging.info(f"[GROQ] {attempt_name}...")
            
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
                    # Increased max_tokens from 20 to 300 to allow reasoning models to finish
                    max_tokens=300,
                ),
                timeout=timeout_secs
            )
            
            choice = completion.choices[0]
            message = choice.message
            content = getattr(message, 'content', '') or ''
            
            # If the model outputs reasoning inside <think> tags in the content block, strip it out
            if "<think>" in content and "</think>" in content:
                content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
                
            answer = content.strip()
            parsed = normalize_answer(answer)
            
            # Validate output internally before succeeding
            if not parsed:
                reason = f"Empty content (finish_reason: {choice.finish_reason})"
                logging.warning(f"[GROQ] {attempt_name} failed: {reason}")
                continue
                
            if not validate_answer(scrambled, parsed):
                logging.warning(f"[GROQ] {attempt_name} failed: Invalid answer '{parsed}' (Length/Letters mismatch)")
                continue
                
            elapsed = time.time() - start_time
            if attempt_name == "Fallback":
                logging.info(f"[GROQ] Fallback succeeded in {elapsed:.2f}s: {parsed}")
            else:
                logging.info(f"[GROQ] {attempt_name} succeeded in {elapsed:.2f}s: {parsed}")
            return parsed
            
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            logging.warning(f"[GROQ] {attempt_name} failed: Timeout after {elapsed:.2f}s")
            continue
        except Exception as e:
            logging.warning(f"[GROQ] {attempt_name} failed: API error - {e}")
            continue
            
    logging.error("[GROQ] All attempts and fallbacks failed.")
    return None
