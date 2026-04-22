from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
import re

from helper.utils import (
    is_admin,
    get_config, update_config,
    increment_warning, reset_warnings,
    is_whitelisted, add_whitelist, remove_whitelist, get_whitelist
)

from config import API_ID, API_HASH, BOT_TOKEN

# -------------------- APP --------------------
app = Client(
    "biolink_protector_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# -------------------- BIO LINK DETECTION PATTERN --------------------
BIO_LINK_PATTERN = re.compile(
    r"(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+|@\w+|\b\S+\.(com|net|org|io|in|xyz)\b)",
    re.IGNORECASE
)

# -------------------- START --------------------
@app.on_message(filters.command("start"))
async def start_handler(client, message):
    bot = await client.get_me()
    add_url = f"https://t.me/{bot.username}?startgroup=true"

    text = (
        "**✨ Welcome to BioLink Protector Bot! ✨**\n\n"
        "Protects your group from users having links in bio."
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me", url=add_url)]
    ])

    await message.reply_text(text, reply_markup=kb)

# -------------------- HELP --------------------
@app.on_message(filters.command("help"))
async def help_handler(client, message):
    help_text = (
        "**Commands:**\n\n"
        "`/config` - configure warn/penalty\n"
        "`/free` - whitelist user\n"
        "`/unfree` - remove whitelist\n"
        "`/freelist` - list whitelist"
    )
    await message.reply_text(help_text)

# -------------------- CONFIG --------------------
@app.on_message(filters.group & filters.command("config"))
async def configure(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        return

    mode, limit, penalty = await get_config(chat_id)

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Warn Limit", callback_data="warn")],
        [
            InlineKeyboardButton("Mute ✅" if penalty=="mute" else "Mute", callback_data="mute"),
            InlineKeyboardButton("Ban ✅" if penalty=="ban" else "Ban", callback_data="ban")
        ]
    ])

    await message.reply_text("**Configure punishment**", reply_markup=kb)

# -------------------- WHITELIST --------------------
@app.on_message(filters.group & filters.command("free"))
async def command_free(client, message):
    chat_id = message.chat.id
    admin_id = message.from_user.id

    if not await is_admin(client, chat_id, admin_id):
        return

    if message.reply_to_message:
        target = message.reply_to_message.from_user
    else:
        return await message.reply_text("Reply to user to whitelist.")

    await add_whitelist(chat_id, target.id)
    await reset_warnings(chat_id, target.id)

    await message.reply_text(f"✅ {target.mention} whitelisted.")

@app.on_message(filters.group & filters.command("unfree"))
async def command_unfree(client, message):
    chat_id = message.chat.id
    admin_id = message.from_user.id

    if not await is_admin(client, chat_id, admin_id):
        return

    if message.reply_to_message:
        target = message.reply_to_message.from_user
    else:
        return await message.reply_text("Reply to user to unwhitelist.")

    await remove_whitelist(chat_id, target.id)

    await message.reply_text(f"❌ {target.mention} removed from whitelist.")

@app.on_message(filters.group & filters.command("freelist"))
async def command_freelist(client, message):
    chat_id = message.chat.id
    admin_id = message.from_user.id

    if not await is_admin(client, chat_id, admin_id):
        return

    ids = await get_whitelist(chat_id)

    if not ids:
        return await message.reply_text("No whitelisted users.")

    text = "**Whitelisted Users:**\n\n"
    for uid in ids:
        try:
            user = await client.get_users(uid)
            text += f"- {user.mention}\n"
        except:
            text += f"- `{uid}`\n"

    await message.reply_text(text)

# -------------------- CALLBACK --------------------
@app.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id

    if data == "mute":
        await update_config(chat_id, penalty="mute")
        await callback_query.answer("Penalty set to mute")

    elif data == "ban":
        await update_config(chat_id, penalty="ban")
        await callback_query.answer("Penalty set to ban")

    elif data == "warn":
        await update_config(chat_id, limit=3)
        await callback_query.answer("Warn limit set to 3")

    elif data.startswith("unmute_"):
        user_id = int(data.split("_")[1])
        await client.restrict_chat_member(
            chat_id,
            user_id,
            ChatPermissions(can_send_messages=True)
        )
        await callback_query.message.edit_text("✅ User unmuted")

    elif data.startswith("unban_"):
        user_id = int(data.split("_")[1])
        await client.unban_chat_member(chat_id, user_id)
        await callback_query.message.edit_text("✅ User unbanned")

# -------------------- BIO CHECK --------------------
@app.on_message(filters.group & ~filters.service)
async def check_bio(client, message):
    try:
        if not message.from_user:
            return

        chat_id = message.chat.id
        user_id = message.from_user.id

        if await is_admin(client, chat_id, user_id):
            return

        if await is_whitelisted(chat_id, user_id):
            return

        user = await client.get_users(user_id)
        bio = user.bio or ""

        if BIO_LINK_PATTERN.search(bio):
            try:
                await message.delete()
            except:
                return

            mode, limit, penalty = await get_config(chat_id)
            count = await increment_warning(chat_id, user_id)

            sent = await message.reply_text(
                f"⚠ {user.mention} warning {count}/{limit}: Link in bio detected."
            )

            if count >= limit:
                if penalty == "mute":
                    await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                    kb = InlineKeyboardMarkup([
                        [InlineKeyboardButton("Unmute", callback_data=f"unmute_{user_id}")]
                    ])
                    await sent.edit_text(
                        f"🔇 {user.mention} muted for link in bio.",
                        reply_markup=kb
                    )

                elif penalty == "ban":
                    await client.ban_chat_member(chat_id, user_id)
                    kb = InlineKeyboardMarkup([
                        [InlineKeyboardButton("Unban", callback_data=f"unban_{user_id}")]
                    ])
                    await sent.edit_text(
                        f"🔨 {user.mention} banned for link in bio.",
                        reply_markup=kb
                    )
        else:
            await reset_warnings(chat_id, user_id)

    except Exception as e:
        print(f"Bio check error: {e}")

# -------------------- RUN --------------------
app.run()
