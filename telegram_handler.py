import time
import asyncio
import logging
from telethon import TelegramClient, events
from config import API_ID, API_HASH
from challenge import is_challenge, extract_word
from solver import generate_guess
from validator import validate_answer
from cache import message_cache

# Initialize client using a persistent session file
client = TelegramClient('sessions/userbot', API_ID, API_HASH)

# Global tracker for active puzzles per chat
# format: { chat_id: {"active": bool, "word": str} }
active_puzzles = {}

@client.on(events.NewMessage)
async def handler(event):
    """
    Event handler for new Telegram messages.
    """
    if not event.text:
        return
        
    chat_id = event.chat_id
    
    # Check for game bot confirmation message
    # e.g. "🏆 **k -** solved it!\n💰 Coins won: 5\n⏱️ Time: 37s"
    if "🏆" in event.text and "solved it!" in event.text:
        if chat_id in active_puzzles and active_puzzles[chat_id].get("active"):
            logging.info("[GAME] Puzzle solved confirmation received! Stopping loop.")
            active_puzzles[chat_id]["active"] = False
        return
        
    # Check if the message is a new challenge
    if not is_challenge(event.text):
        return
        
    # Prevent duplicate handling by message ID
    msg_key = f"msg_{event.id}"
    if await message_cache.contains(msg_key):
        return
    await message_cache.add(msg_key)
        
    # Extract the scrambled word
    word = extract_word(event.text)
    if not word:
        logging.warning("Challenge detected but word extraction failed.")
        return
        
    # Prevent solving the exact same message twice
    word_key = f"word_{word}"
    if await message_cache.contains(word_key):
        return
    await message_cache.add(word_key)

    logging.info(f"Challenge detected: {word}")
    
    # Mark puzzle as active in this chat
    active_puzzles[chat_id] = {"active": True, "word": word}
    
    # Start the non-blocking solving loop
    asyncio.create_task(solve_loop(event, word, chat_id))


async def solve_loop(event, word, chat_id):
    """
    Background task to generate, validate, and send guesses,
    waiting for game-bot confirmation between attempts.
    """
    models_sequence = [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-20b",
        "groq/compound-mini",
        "openai/gpt-oss-20b",
        "groq/compound-mini",
        "openai/gpt-oss-20b",
        "groq/compound-mini",
        "openai/gpt-oss-20b",
        "groq/compound-mini",
        "openai/gpt-oss-20b"
    ]
    
    previous_guesses = set()
    start_time = time.time()
    
    for i, model in enumerate(models_sequence, 1):
        # Abort if the puzzle was solved by us or someone else
        puzzle_state = active_puzzles.get(chat_id, {})
        if not puzzle_state.get("active") or puzzle_state.get("word") != word:
            logging.info("[SOLVER] Loop aborted (puzzle no longer active).")
            break
            
        logging.info(f"[SOLVER] Attempt {i} with {model}...")
        
        guess = await generate_guess(word, model, previous_guesses)
        
        if not guess:
            logging.warning(f"[SOLVER] Attempt {i} failed to generate a guess.")
            continue
            
        if guess in previous_guesses:
            logging.warning(f"[SOLVER] Attempt {i} returned duplicate guess: {guess}")
            continue
            
        if not validate_answer(word, guess):
            logging.warning(f"[SOLVER] Attempt {i} returned invalid anagram: {guess}")
            continue
            
        # Valid new guess found
        previous_guesses.add(guess)
        formatted_answer = guess.capitalize()
        
        try:
            await client.send_message(chat_id, formatted_answer)
            elapsed = time.time() - start_time
            logging.info(f"[SEND] Sent guess #{i}: {formatted_answer} ({elapsed:.2f}s)")
        except Exception as e:
            logging.error(f"[SEND] Failed to send guess: {e}")
            continue
            
        # Wait for the game bot to confirm
        # This checks active_puzzles flag asynchronously
        wait_time = 1.5
        slept = 0.0
        while slept < wait_time:
            await asyncio.sleep(0.1)
            slept += 0.1
            
            # If the success message was parsed by the handler during our sleep, break early!
            puzzle_state = active_puzzles.get(chat_id, {})
            if not puzzle_state.get("active") or puzzle_state.get("word") != word:
                logging.info(f"[SOLVER] Victory confirmed after guess #{i}: {formatted_answer}")
                return
                
    logging.info("[SOLVER] Exhausted all 10 attempts. Stopping.")
