from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME
import logging

# ==========================================================
# MongoDB Connection
# ==========================================================

client = AsyncIOMotorClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True,
    serverSelectionTimeoutMS=5000
)

db = client[DB_NAME]

logging.basicConfig(level=logging.INFO)
logging.info("✅ MongoDB client initialized")


# ==========================================================
# 🟢 Welcome
# ==========================================================

async def set_welcome_message(chat_id, text: str):
    try:
        await db.welcome.update_one(
            {"chat_id": chat_id},
            {"$set": {"message": text}},
            upsert=True
        )
    except Exception as e:
        logging.error(f"set_welcome_message error: {e}")


async def get_welcome_message(chat_id):
    try:
        data = await db.welcome.find_one({"chat_id": chat_id})
        return data.get("message") if data else None
    except Exception as e:
        logging.error(f"get_welcome_message error: {e}")
        return None


async def set_welcome_status(chat_id, status: bool):
    try:
        await db.welcome.update_one(
            {"chat_id": chat_id},
            {"$set": {"enabled": status}},
            upsert=True
        )
    except Exception as e:
        logging.error(f"set_welcome_status error: {e}")


async def get_welcome_status(chat_id) -> bool:
    try:
        data = await db.welcome.find_one({"chat_id": chat_id})
        return bool(data.get("enabled", True)) if data else True
    except Exception as e:
        logging.error(f"get_welcome_status error: {e}")
        return True


# ==========================================================
# 🔒 Lock
# ==========================================================

async def set_lock(chat_id, lock_type, status: bool):
    try:
        await db.locks.update_one(
            {"chat_id": chat_id},
            {"$set": {f"locks.{lock_type}": status}},
            upsert=True
        )
    except Exception as e:
        logging.error(f"set_lock error: {e}")


async def get_locks(chat_id):
    try:
        data = await db.locks.find_one({"chat_id": chat_id})
        return data.get("locks", {}) if data else {}
    except Exception as e:
        logging.error(f"get_locks error: {e}")
        return {}


# ==========================================================
# ⚠️ Warn
# ==========================================================

async def add_warn(chat_id: int, user_id: int) -> int:
    try:
        data = await db.warns.find_one({"chat_id": chat_id, "user_id": user_id})
        warns = data.get("count", 0) + 1 if data else 1

        await db.warns.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"count": warns}},
            upsert=True
        )
        return warns
    except Exception as e:
        logging.error(f"add_warn error: {e}")
        return 0


async def get_warns(chat_id: int, user_id: int) -> int:
    try:
        data = await db.warns.find_one({"chat_id": chat_id, "user_id": user_id})
        return data.get("count", 0) if data else 0
    except Exception as e:
        logging.error(f"get_warns error: {e}")
        return 0


async def reset_warns(chat_id: int, user_id: int):
    try:
        await db.warns.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"count": 0}},
            upsert=True
        )
    except Exception as e:
        logging.error(f"reset_warns error: {e}")


# ==========================================================
# 🧹 Cleanup
# ==========================================================

async def clear_group_data(chat_id: int):
    try:
        await db.welcome.delete_one({"chat_id": chat_id})
        await db.locks.delete_one({"chat_id": chat_id})
        await db.warns.delete_many({"chat_id": chat_id})
    except Exception as e:
        logging.error(f"clear_group_data error: {e}")


# ==========================================================
# 👤 User
# ==========================================================

async def add_user(user_id, first_name):
    try:
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"first_name": first_name}},
            upsert=True
        )
    except Exception as e:
        logging.error(f"add_user error: {e}")


async def get_all_users():
    users = []
    try:
        async for document in db.users.find({}, {"_id": 0, "user_id": 1}):
            if "user_id" in document:
                users.append(document["user_id"])
    except Exception as e:
        logging.error(f"get_all_users error: {e}")
    return users
async def get_welcome_message(chat_id):
    data = await db.welcome.find_one({"chat_id": chat_id})
    return data.get("message") if data else None

async def set_welcome_status(chat_id, status: bool):
    await db.welcome.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": status}},
        upsert=True
    )

async def get_welcome_status(chat_id) -> bool:
    data = await db.welcome.find_one({"chat_id": chat_id})
    return bool(data.get("enabled", True)) if data else True


# ==========================================================
# 🔒 Lock
# ==========================================================

async def set_lock(chat_id, lock_type, status: bool):
    await db.locks.update_one(
        {"chat_id": chat_id},
        {"$set": {f"locks.{lock_type}": status}},
        upsert=True
    )

async def get_locks(chat_id):
    data = await db.locks.find_one({"chat_id": chat_id})
    return data.get("locks", {}) if data else {}


# ==========================================================
# ⚠️ Warn
# ==========================================================

async def add_warn(chat_id: int, user_id: int) -> int:
    data = await db.warns.find_one({"chat_id": chat_id, "user_id": user_id})
    warns = data.get("count", 0) + 1 if data else 1

    await db.warns.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": warns}},
        upsert=True
    )
    return warns

async def get_warns(chat_id: int, user_id: int) -> int:
    data = await db.warns.find_one({"chat_id": chat_id, "user_id": user_id})
    return data.get("count", 0) if data else 0

async def reset_warns(chat_id: int, user_id: int):
    await db.warns.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": 0}},
        upsert=True
    )


# ==========================================================
# 🧹 Cleanup
# ==========================================================

async def clear_group_data(chat_id: int):
    await db.welcome.delete_one({"chat_id": chat_id})
    await db.locks.delete_one({"chat_id": chat_id})
    await db.warns.delete_many({"chat_id": chat_id})


# ==========================================================
# 👤 User
# ==========================================================

async def add_user(user_id, first_name):
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"first_name": first_name}},
        upsert=True
    )

async def get_all_users():
    users = []
    async for document in db.users.find({}, {"_id": 0, "user_id": 1}):
        if "user_id" in document:
            users.append(document["user_id"])
    return users
