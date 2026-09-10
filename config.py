import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Optional log chat (can be an integer ID like -100123456789 or string like @mychannel)
LOG_CHAT_ID = os.getenv("LOG_CHAT_ID")
if LOG_CHAT_ID:
    try:
        LOG_CHAT_ID = int(LOG_CHAT_ID)
    except ValueError:
        pass

if not all([API_ID, API_HASH, GROQ_API_KEY]):
    logging.error("Missing required environment variables. Please check your .env file.")
    sys.exit(1)

try:
    API_ID = int(API_ID)
except ValueError:
    logging.error("API_ID must be an integer.")
    sys.exit(1)

# Ensure sessions directory exists before Telethon tries to create the sqlite database
os.makedirs('sessions', exist_ok=True)
