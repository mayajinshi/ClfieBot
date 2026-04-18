import asyncio
import os
import logging
import threading
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer

# ==========================================================
# Async loop setup
# ==========================================================
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# ==========================================================
# Logging setup
# ==========================================================
logging.basicConfig(level=logging.INFO)
print("🚀 Starting bot...")

# ==========================================================
# Check environment variables
# ==========================================================
try:
    print("🔍 Checking ENV variables...")
    print("API_ID:", "SET" if os.getenv("API_ID") else "MISSING")
    print("API_HASH:", "SET" if os.getenv("API_HASH") else "MISSING")
    print("BOT_TOKEN:", "SET" if os.getenv("BOT_TOKEN") else "MISSING")
    print("MONGO_URI:", "SET" if os.getenv("MONGO_URI") else "MISSING")
    print("✅ ALL SET!")
except Exception as e:
    print("❌ ENV ERROR:", e)
    traceback.print_exc()

# ==========================================================
# Web server for Render health checks
# ==========================================================
PORT = int(os.environ.get("PORT", 10000))

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ClfieBot is running")

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

# ==========================================================
# Start Telegram Bot
# ==========================================================
try:
    from pyrogram import Client
    from config import API_ID, API_HASH, BOT_TOKEN
    from handlers import register_all_handlers

    print("🔧 Initializing bot client...")

    app = Client(
        "group_manager_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )

    register_all_handlers(app)

    print("🚀 Bot is running...")
    app.run()

except Exception as e:
    print("💥 BOT CRASHED:", e)
    traceback.print_exc()
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ClfieBot is running")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def start_web_server():
    try:
        server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
        logging.info(f"🌐 Web server running on port {PORT}")
        server.serve_forever()
    except Exception as e:
        print("❌ WEB SERVER ERROR:", e)
        traceback.print_exc()

threading.Thread(target=start_web_server, daemon=True).start()

try:
    from pyrogram import Client
    from config import API_ID, API_HASH, BOT_TOKEN
    from handlers import register_all_handlers

    print("🔧 Initializing bot client...")

    app = Client(
        "group_manager_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )

    register_all_handlers(app)

    print("🚀 Starting bot now...")
    app.run()
    print("🛑 Bot stopped")

except Exception as e:
    print("💥 BOT CRASHED:", e)
    traceback.print_exc()
