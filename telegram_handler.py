import time
import asyncio
import logging
from datetime import datetime, timezone
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from config import API_ID, API_HASH
from challenge import is_challenge, extract_word
from solver import solve_word
from validator import validate_answer
from cache import message_cache

# Initialize client using a persistent session file
client = TelegramClient('sessions/userbot', API_ID, API_HASH)

@client.on(events.NewMessage)
async def handler(event):
    """
    Event handler for new Telegram messages.
    """
    if not event.text:
        return
        
    # Check if the message is a challenge
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
        
        # Safe debug logging for analysis
        safe_text = repr(event.text) if event.text else "None"
        raw_text = repr(event.raw_text) if hasattr(event, 'raw_text') else "None"
        logging.info(f"--- EXTRACTION DEBUG ---")
        logging.info(f"Chat ID: {event.chat_id}")
        logging.info(f"Message ID: {event.id}")
        logging.info(f"Media/Caption present: {bool(event.media)}")
        logging.info(f"event.text: {safe_text}")
        logging.info(f"event.raw_text: {raw_text}")
        logging.info(f"------------------------")
        return
        
    # Prevent solving the same word repeatedly if it's spammed or retried
    word_key = f"word_{word}"
    if await message_cache.contains(word_key):
        logging.info(f"Challenge already processed for word: {word}")
        return
    await message_cache.add(word_key)

    logging.info(f"Challenge detected: {word}")
    start_time = time.time()
    
    # Send to Groq for solving
    answer = await solve_word(word)
    valid = answer and validate_answer(word, answer)
    
    if not valid:
        logging.warning(f"Groq failed or returned invalid answer for {word}")
        return
        
    # Format answer as title case before sending
    formatted_answer = answer.capitalize()
    
    # Send answer back to the same chat
    try:
        await client.send_message(event.chat_id, formatted_answer)
        elapsed = time.time() - start_time
        logging.info(f"[SEND] Sending answer: {formatted_answer}")
        logging.info(f"[SEND] Success")
        logging.info(f"Challenge received -> answer sent: {elapsed:.2f}s")
    except Exception as e:
        logging.error(f"Failed to send message: {e}")
