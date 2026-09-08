# Telegram Word Solver Userbot

A fast, fully asynchronous Telegram userbot designed to instantly solve scrambled word challenges in Telegram groups using the Groq API.

## Requirements
- Python 3.11+
- A Telegram account (API ID and Hash from [my.telegram.org](https://my.telegram.org))
- Groq API key

## Setup Instructions

1. Clone or download this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and add your `API_ID`, `API_HASH`, and `GROQ_API_KEY`.

## Running the Userbot

Start the bot with:
```bash
python main.py
```

**First time login:**
The first time you run the script, Telethon will ask for your Telegram phone number, login code (sent to your Telegram app), and 2FA password (if enabled). This will generate a persistent `.session` file inside the `sessions/` directory. On subsequent runs, it will use this session and won't ask for login details again.

## Running Continuously

For a production environment (like a VPS), it is recommended to use `systemd` or `pm2` to keep the bot running in the background.

Example using `pm2`:
```bash
pip install pm2
pm2 start main.py --name tg-word-solver --interpreter python
```

Example using `systemd`:
Create `/etc/systemd/system/tg-word-solver.service`:
```ini
[Unit]
Description=Telegram Word Solver
After=network.target

[Service]
User=youruser
WorkingDirectory=/path/to/tg-word-solver
ExecStart=/path/to/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```
Then `systemctl enable --now tg-word-solver`.

## Running Tests

To run the test suite:
```bash
pytest test_solver.py -v
```

## How it works

1. The bot listens passively using Telegram's event-driven updates.
2. When a message containing "Scrambled Word Challenge!" appears, it triggers the handler.
3. The scrambled word is extracted via regex.
4. It calls the `groq/compound-mini` model asynchronously with a very short prompt to solve it.
5. A local validation confirms the multiset of letters in the model's answer matches the original scrambled word perfectly.
6. The valid answer is immediately sent to the same Telegram chat group where the challenge was spotted. 
7. Caching prevents answering the same puzzle twice.
