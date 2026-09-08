import time
import logging
from telethon import TelegramClient, events
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
    if not answer:
        logging.error("Solver failed to provide an answer.")
        return
        
    # Local validation
    if not validate_answer(word, answer):
        logging.warning(f"Invalid answer generated: {answer} for {word}")
        return
        
    # Send answer back to the same chat
    try:
        await client.send_message(event.chat_id, answer)
        elapsed = time.time() - start_time
        logging.info(f"Solved: {answer}")
        logging.info(f"Challenge received -> answer sent: {elapsed:.2f}s")
    except Exception as e:
        logging.error(f"Failed to send message: {e}")

