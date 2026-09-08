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
    Optimized for minimum latency with model fallbacks.
    """
    logging.info(f"[GROQ] Preparing request for word: {scrambled}")
    logging.info(f"[GROQ] API key configured: {'YES' if GROQ_API_KEY else 'NO'}")
    
    models = ["openai/gpt-oss-20b", "groq/compound-mini"]
    max_retries = 1
    timeout_secs = 4.0
    
    for model_name in models:
        logging.info(f"[GROQ] Trying model: {model_name}")
        
        for attempt in range(max_retries + 1):
            if attempt > 0:
                logging.info(f"[GROQ] Retry #{attempt} for {model_name}")
                
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
                        # Increased max_tokens from 20 to 300 to allow reasoning models to finish
                        max_tokens=300,
                    ),
                    timeout=timeout_secs
                )
                
                elapsed = time.time() - start_time
                logging.info(f"[GROQ] Response received in {elapsed:.2f}s")
                
                # Safe parsing
                choice = completion.choices[0]
                message = choice.message
                content = getattr(message, 'content', '') or ''
                
                # Some reasoning models return thought process in reasoning_content
                reasoning = getattr(message, 'reasoning_content', getattr(message, 'reasoning', None))
                
                # Temporary debug logs
                logging.info(f"[GROQ DEBUG] finish_reason: {choice.finish_reason}")
                logging.info(f"[GROQ DEBUG] content repr: {repr(content)}")
                logging.info(f"[GROQ DEBUG] reasoning present: {'YES' if reasoning else 'NO'}")
                if reasoning:
                    logging.info(f"[GROQ DEBUG] reasoning length: {len(reasoning)}")
                if hasattr(completion, 'usage') and completion.usage:
                    logging.info(f"[GROQ DEBUG] usage: {completion.usage.completion_tokens} completion / {completion.usage.prompt_tokens} prompt")

                if attempt > 0:
                    logging.info("[GROQ] Retry succeeded")
                    
                import re
                # If the model outputs reasoning inside <think> tags in the content block, strip it out
                if "<think>" in content and "</think>" in content:
                    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
                    
                answer = content.strip()
                parsed = normalize_answer(answer)
                logging.info(f"[GROQ] Parsed answer: {parsed}")
                return parsed
                
            except asyncio.TimeoutError:
                elapsed = time.time() - start_time
                logging.error(f"[GROQ] Timeout after {elapsed:.2f}s on {model_name}")
                continue
            except Exception as e:
                logging.error(f"[GROQ] API error on {model_name}: {e}")
                break # Fatal error for this model, break retry loop and move to next model
                
        logging.warning(f"[GROQ] Model {model_name} exhausted all attempts.")
            
    logging.error("[GROQ] All fallback models failed.")
    return None
