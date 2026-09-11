import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

# Optional log chat (can be an integer ID like -100123456789 or string like @mychannel)
LOG_CHAT_ID = os.getenv("LOG_CHAT_ID")
if LOG_CHAT_ID:
    try:
        LOG_CHAT_ID = int(LOG_CHAT_ID)
    except ValueError:
        pass

if not all([API_ID, API_HASH]):
    logging.error("Missing required environment variables (API_ID, API_HASH). Please check your .env file.")
    sys.exit(1)
