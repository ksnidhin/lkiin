import logging
import asyncio
import sys
from telegram_handler import client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

async def main():
    logging.info("Starting...")
    
    # Check if sessions directory exists
    import os
    os.makedirs('sessions', exist_ok=True)
    
    try:
        await client.start()
        logging.info("Userbot online — waiting for Scrambled Word Challenges...")
        await client.run_until_disconnected()
    except KeyboardInterrupt:
        logging.info("Shutting down cleanly...")
    except Exception as e:
        logging.error(f"Unexpected error in main loop: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
