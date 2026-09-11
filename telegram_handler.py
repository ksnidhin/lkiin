import re
import logging
from telethon import TelegramClient, events
from telethon.tl.types import MessageEntityUrl, MessageEntityTextUrl
from config import API_ID, API_HASH, LOG_CHAT_ID

# Initialize client using a persistent session file
client = TelegramClient('sessions/userbot', API_ID, API_HASH)

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
    Checks if a message contains a link and is sent by a bot.
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
    # Monitor for bot links to delete
    await check_and_delete_bot_link(event)
