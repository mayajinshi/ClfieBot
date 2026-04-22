import asyncio
import os
import logging
import threading
import traceback
import re
from http.server import BaseHTTPRequestHandler, HTTPServer

from pyrogram import Client, filters
from pyrogram.errors import RPCError

# -------------------- EVENT LOOP FIX --------------------
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# -------------------- LOGGING --------------------
logging.basicConfig(level=logging.INFO)
print("🚀 Starting bot...")

# -------------------- ENV CHECK --------------------
try:
    print("🔍 Checking ENV variables...")
    print("API_ID:", "SET" if os.getenv("API_ID") else "MISSING")
    print("API_HASH:", "SET" if os.getenv("API_HASH") else "MISSING")
    print("BOT_TOKEN:", "SET" if os.getenv("BOT_TOKEN") else "MISSING")
    print("✅ ALL SET!")
except Exception as e:
    print("❌ ENV ERROR:", e)
    traceback.print_exc()

# -------------------- WEB SERVER --------------------
PORT = int(os.environ.get("PORT", 10000))

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def start_web_server():
    try:
        HTTPServer.allow_reuse_address = True
        server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
        logging.info(f"🌐 Web server running on port {PORT}")
        server.serve_forever()
    except Exception as e:
        print("❌ WEB SERVER ERROR:", e)
        traceback.print_exc()

threading.Thread(target=start_web_server, daemon=True).start()

# -------------------- BOT CONFIG --------------------
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client(
    "group_manager_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# -------------------- BIO LINK DETECTION --------------------
bio_pattern = re.compile(
    r"(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+|@\w+|\b\S+\.(com|net|org|io|in|xyz)\b)",
    re.IGNORECASE
)

@app.on_message(filters.group)
async def detect_bio_links(client, message):
    try:
        user = message.from_user
        if not user:
            return

        # Get user info
        full_user = await client.get_users(user.id)

        # Try reading bio
        bio = getattr(full_user, "bio", "") or ""

        print(f"👤 User: {user.first_name} | Bio: {bio}")

        # Detect links in bio
        if bio_pattern.search(bio):
            await message.delete()
            print(f"🗑")

    except RPCError as e:
        print(f"❌ Pyrogram RPC Error: {e}")
    except Exception as e:
        print(f"❌ General Error: {e}")

# -------------------- START BOT --------------------
try:
    print("🚀 Bot is running...")
    app.run()
except Exception as e:
    print("💥 BOT CRASHED:", e)
    traceback.print_exc()
