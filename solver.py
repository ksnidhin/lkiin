import asyncio
import time
import logging
import re
from groq import AsyncGroq
from config import GROQ_API_KEY
from validator import normalize_answer

client = AsyncGroq(api_key=GROQ_API_KEY)

async def generate_guess(scrambled: str, model_name: str, previous_guesses: set) -> str | None:
    """
    Generates a single anagram guess using the specified model.
    Instructs the model to avoid previous guesses.
    """
    avoid_text = ""
    if previous_guesses:
        avoid_text = "\n- DO NOT return any of these previously guessed words: " + ", ".join(previous_guesses)
        
    try:
        completion = await asyncio.wait_for(
            client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You solve anagram games. Return the most common/intended English word using ALL letters exactly once. Output ONLY the word."
                    },
                    {
                        "role": "user",
                        "content": f"Unscramble: {scrambled}\n\nIMPORTANT:\n- Prefer the normal/common English word.\n- Do not return an obscure or uncommon valid anagram when a common word exists.\n- Use every letter exactly once.\n- Return ONLY the final word.{avoid_text}"
                    }
                ],
                model=model_name,
                # Use slight temperature if we need alternatives, otherwise 0.0 for first guess
                temperature=0.0 if not previous_guesses else 0.4,
                max_tokens=300,
            ),
            timeout=4.0
        )
        
        choice = completion.choices[0]
        content = getattr(choice.message, 'content', '') or ''
        
        if "<think>" in content and "</think>" in content:
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
            
        answer = content.strip()
        parsed = normalize_answer(answer)
        
        if not parsed:
            logging.warning(f"[GROQ] {model_name} returned empty content (finish_reason: {choice.finish_reason})")
            return None
            
        return parsed
        
    except asyncio.TimeoutError:
        logging.warning(f"[GROQ] {model_name} timed out.")
        return None
    except Exception as e:
        logging.warning(f"[GROQ] {model_name} API error: {e}")
        return None
