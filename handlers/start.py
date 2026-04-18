from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from config import BOT_USERNAME, SUPPORT_GROUP, UPDATE_CHANNEL, START_IMAGE, OWNER_ID
import db


def register_handlers(app: Client):
    print("✅ Start handlers registered")

    # ==========================================================
    # Start Menu
    # ==========================================================
    async def send_start_menu(message, user):
        text = f"""
💋 Hello {user}!
👋 I am ClfieBot
• Smart AI anti-spam & link shield  
• Adaptive lock system  
• Modular protection  
• Inline control panel  

More features coming soon...
"""

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Add to Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
            [
                InlineKeyboardButton("Support", url=SUPPORT_GROUP),
                InlineKeyboardButton("Updates", url=UPDATE_CHANNEL),
            ],
            [
                InlineKeyboardButton("Owner", url=f"t.me/clfie")
            ],
            [InlineKeyboardButton("Help Commands", callback_data="help")]
        ])

        if message.text:
            await message.reply_photo(
                photo=START_IMAGE,
                caption=text,
                reply_markup=buttons
            )
        else:
            media = InputMediaPhoto(
                media=START_IMAGE,
                caption=text
            )
            await message.edit_media(
                media=media,
                reply_markup=buttons
            )

    # ==========================================================
    # Start Command
    # ==========================================================
    @app.on_message(filters.private & filters.command("start"))
    async def start_command(client, message):
        user = message.from_user.first_name

        try:
            await db.add_user(message.from_user.id, user)
        except Exception as e:
            print("DB Error:", e)

        await send_start_menu(message, user)

    # ==========================================================
    # Help Menu
    # ==========================================================
    async def send_help_menu(message):
        text = """
📚 Help Menu

Choose a category below:
"""

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Greetings", callback_data="greetings"),
                InlineKeyboardButton("Locks", callback_data="locks"),
            ],
            [
                InlineKeyboardButton("Moderation", callback_data="moderation")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="back_to_start")
            ]
        ])

        media = InputMediaPhoto(media=START_IMAGE, caption=text)
        await message.edit_media(media=media, reply_markup=buttons)

    # ==========================================================
    # Help Callback
    # ==========================================================
    @app.on_callback_query(filters.regex("^help$"))
    async def help_callback(client, callback_query):
        await send_help_menu(callback_query.message)
        await callback_query.answer()

    # ==========================================================
    # Back Callback
    # ==========================================================
    @app.on_callback_query(filters.regex("^back_to_start$"))
    async def back_to_start(client, callback_query):
        await send_start_menu(callback_query.message, callback_query.from_user.first_name)
        await callback_query.answer()

    # ==========================================================
    # Greetings Callback
    # ==========================================================
    @app.on_callback_query(filters.regex("^greetings$"))
    async def greetings_callback(client, callback_query):
        text = """
⚙ Welcome Commands

/setwelcome <text>
/welcome on
/welcome off
"""

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="help")]
        ])

        media = InputMediaPhoto(media=START_IMAGE, caption=text)
        await callback_query.message.edit_media(media=media, reply_markup=buttons)
        await callback_query.answer()

    # ==========================================================
    # Locks Callback
    # ==========================================================
    @app.on_callback_query(filters.regex("^locks$"))
    async def locks_callback(client, callback_query):
        text = """
⚙ Lock Commands

/lock <type>
/unlock <type>
/locks
"""

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="help")]
        ])

        media = InputMediaPhoto(media=START_IMAGE, caption=text)
        await callback_query.message.edit_media(media=media, reply_markup=buttons)
        await callback_query.answer()

    # ==========================================================
    # Moderation Callback
    # ==========================================================
    @app.on_callback_query(filters.regex("^moderation$"))
    async def moderation_callback(client, callback_query):
        text = """
⚙ Moderation Commands

/ban
/unban
/kick
/mute
/unmute
/warn
/warns
/resetwarns
"""

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="help")]
        ])

        media = InputMediaPhoto(media=START_IMAGE, caption=text)
        await callback_query.message.edit_media(media=media, reply_markup=buttons)
        await callback_query.answer()

    # ==========================================================
    # Broadcast
    # ==========================================================
    @app.on_message(filters.private & filters.command("broadcast"))
    async def broadcast_message(client, message):
        if message.from_user.id != OWNER_ID:
            return await message.reply_text("❌ Unauthorized")

        if not message.reply_to_message:
            return await message.reply_text("Reply to a message to broadcast.")

        users = await db.get_all_users()
        sent, failed = 0, 0

        for user_id in users:
            try:
                await client.send_message(user_id, message.reply_to_message.text)
                sent += 1
            except:
                failed += 1

        await message.reply_text(f"✅ Sent: {sent}, Failed: {failed}")

    # ==========================================================
    # Stats
    # ==========================================================
    @app.on_message(filters.private & filters.command("stats"))
    async def stats_command(client, message):
        if message.from_user.id != OWNER_ID:
            return await message.reply_text("❌ Unauthorized")

        users = await db.get_all_users()
        await message.reply_text(f"👥 Total Users: {len(users)}")
