import time
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from config import API_ID, API_HASH, LOG_CHAT_ID
from challenge import is_challenge, extract_word
from solver import generate_guess
from validator import validate_answer
from cache import message_cache

# Initialize client using a persistent session file
client = TelegramClient('sessions/userbot', API_ID, API_HASH)

# Global tracker for active puzzles per chat
# format: { chat_id: {"active": bool, "word": str} }
active_puzzles = {}

import re
from telethon.tl.types import MessageEntityUrl, MessageEntityTextUrl

async def send_log_message(text):
    """Safely sends a message to the configured log chat."""
    if not LOG_CHAT_ID:
        return
    try:
        await client.send_message(LOG_CHAT_ID, text)
    except Exception as e:
        logging.error(f"Failed to send to log chat: {e}")

async def check_and_delete_bot_link(event):
    """
    Checks if a non-challenge message contains a link and is sent by a bot.
    Deletes the message if the userbot has admin privileges.
    """
    try:
        has_link = False
        if event.message.entities:
            has_link = any(isinstance(ent, (MessageEntityUrl, MessageEntityTextUrl)) for ent in event.message.entities)
            
        if not has_link and event.text:
            has_link = bool(re.search(r'(https?://|t\.me/|www\.)[^\s]+', event.text, re.IGNORECASE))
            
        if has_link:
            sender = await event.get_sender()
            # If sender is a bot and not ourselves
            if sender and getattr(sender, 'bot', False) and not event.message.out:
                msg_text = event.text or "No text"
                chat = await event.get_chat()
                chat_title = getattr(chat, 'title', str(event.chat_id))
                
                chat_username = getattr(chat, 'username', None)
                if chat_username:
                    group_link = f"https://t.me/{chat_username}"
                else:
                    group_link = f"ID: {event.chat_id}"
                
                bot_username = getattr(sender, 'username', 'unknown')
                
                await event.delete()
                logging.info(f"[MOD] Deleted link sent by bot (@{bot_username}) in chat {event.chat_id}")
                
                # Send to log chat
                from datetime import datetime
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_msg = (
                    f"🗑 **Deleted Bot Link**\n"
                    f"⏰ Time: `{now_str}`\n"
                    f"🔗 Content: {msg_text}\n"
                    f"🛡 Group: {chat_title} ({group_link})"
                )
                await send_log_message(log_msg)
    except Exception:
        # Fail silently if we are not admin or don't have delete privileges
        pass

@client.on(events.NewMessage)
async def handler(event):
    """
    Event handler for new Telegram messages.
    """
    if not event.text:
        await check_and_delete_bot_link(event)
        return
        
    chat_id = event.chat_id
    
    # Check for game bot confirmation message
    # e.g. "🏆 **k -** solved it!\n💰 Coins won: 5\n⏱️ Time: 37s"
    if "🏆" in event.text and "solved it!" in event.text:
        if chat_id in active_puzzles and active_puzzles[chat_id].get("active"):
            logging.info("[GAME] Puzzle solved confirmation received! Stopping loop.")
            
            puzzle_info = active_puzzles[chat_id]
            scrambled_word = puzzle_info.get("word", "Unknown")
            solved_word = puzzle_info.get("solved_word", "Unknown")
            
            start_time = puzzle_info.get("start_time", time.time())
            elapsed_total = time.time() - start_time
            
            chat = await event.get_chat()
            chat_title = getattr(chat, 'title', str(chat_id))
            from datetime import datetime
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_msg = (
                f"✅ **Puzzle Solved!**\n"
                f"🛡 Group: {chat_title}\n"
                f"🔤 Scrambled: `{scrambled_word}`\n"
                f"🔓 Answer: `{solved_word}`\n"
                f"⏱ Time taken: `{elapsed_total:.2f}s`\n"
                f"⏰ Time: `{now_str}`"
            )
            await send_log_message(log_msg)
            
            active_puzzles[chat_id]["active"] = False
        return
        
    # Check if the message is a new challenge
    if not is_challenge(event.text):
        # If it's not a puzzle, monitor for bot links to delete
        await check_and_delete_bot_link(event)
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
    
    # Mark puzzle as active in this chat and record start time
    active_puzzles[chat_id] = {
        "active": True, 
        "word": word,
        "solved_word": None,
        "start_time": time.time()
    }
    
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
            
            if chat_id in active_puzzles:
                active_puzzles[chat_id]["solved_word"] = formatted_answer
                
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
