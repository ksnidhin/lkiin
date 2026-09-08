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

async def liveness_watchdog():
    """
    Periodic health check to prevent silent socket zombies.
    Pings the Telegram API every 5 minutes.
    """
    import os as _os
    while True:
        await asyncio.sleep(300)
        try:
            # Quick API ping with strict timeout
            await asyncio.wait_for(client.get_me(), timeout=10.0)
            logging.debug("Watchdog: Telegram connection is alive.")
        except Exception as e:
            logging.error(f"WATCHDOG FAILED: {e}. Terminating process to allow PM2 restart.")
            # Force immediate exit so PM2 detects the crash and restarts cleanly
            _os._exit(1)

async def main():
    logging.info("Starting...")
    
    # Check if sessions directory exists
    import os
    os.makedirs('sessions', exist_ok=True)
    
    try:
        await client.start()
        logging.info("Userbot online — waiting for Scrambled Word Challenges...")
        
        # Start the watchdog in the background
        asyncio.create_task(liveness_watchdog())
        
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
