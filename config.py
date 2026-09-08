import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not all([API_ID, API_HASH, GROQ_API_KEY]):
    logging.error("Missing required environment variables. Please check your .env file.")
    sys.exit(1)

try:
    API_ID = int(API_ID)
except ValueError:
    logging.error("API_ID must be an integer.")
    sys.exit(1)
