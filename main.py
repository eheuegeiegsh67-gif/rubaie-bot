import asyncio
import os
import json
import time
from datetime import datetime, timezone, timedelta
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==================== الإعدادات الأساسية ====================
BOT_TOKEN = "8648735860:AAHIXbAq8by99wYWb1ZpkkWtDguX-lghBkA"
API_ID = 38183563
API_HASH = "7d3d3b9379c6840a72c983865c8d927d"

ADMIN_ID = 7989509412
ADMIN_USERNAME = "Al_Rubaie15"

# بوت التحكم الرئيسي
bot_app = Client(
    "Rubaie_Maker_Bot_New",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ==================== نظام قاعدة البيانات (JSON) ====================
DB_FILE = "database.json"

def load_database():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"subscriptions": {}, "user_sessions": {}, "forced_channels": ["Al_Rubaie02"]}

def save_database(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"خطأ في حفظ قاعدة البيانات: {e}")

db = load_database()
active_subscriptions = db.get("subscriptions", {})
user_sessions = db.get("user_sessions", {})
forced_channels = db.get("forced_channels", ["Al_Rubaie02"])

temp_users = {}       
user_active_sources = {}  
muted_users = set()       
original_profile = {}     
sleep_mode = [False]      
warn_counts = {}          
stop_posting_flags = {}   

FONTS_MAP = {
    "1": {"0":"٠", "1":"١", "2":"٢", "3":"٣", "4":"٤", "5":"٥", "6":"٦", "7":"٧", "8":"٨", "9":"٩"},
    "2": {"0":"𝟎", "1":"𝟏", "2":"𝟐", "3":"𝟑", "4":"𝟒", "5":"𝟓", "6":"𝟔", "7":"𝟕", "8":"𝟖", "9":"𝟗"},
    "3": {"0":"𝟶", "1":"𝟷", "2":"𝟸", "3":"𝟹", "4":"𝟺", "5":"𝟻", "6":"𝟼", "7":"𝟽", "8":"𝟾", "9":"𝟿"},
    "4": {"0":"⓪", "1":"①", "2":"②", "3":"③", "4":"④", "5":"⑤", "6":"⑥", "7":"⑦", "8":"⑧", "9":"⑨"},
    "5": {"0":"⓿", "1":"❶", "2":"❷", "3":"❸", "4":"❹", "5":"❺", "6":"❻", "7":"❼", "8":"❽", "9":"❾"},
    "6": {"0":"⓪", "1":"①", "2":"②", "3":"③", "4":"④", "5":"⑤", "6":"⑥", "7":"⑦", "8":"⑧", "9":"⑨"},
    "7": {"0":"0", "1":"1", "2":"2", "3":"3", "4":"4", "5":"5", "6":"6", "7":"7", "8":"8", "9":"9"},
    "8": {"0":"𝟶", "1":"𝟷", "2":"𝟸", "3":"𝟹", "4":"𝟺", "5":"𝟻", "6":"𝟼", "7":"𝟽", "8":"𝟾", "9":"𝟿"}
}

def format_time_with_font(time_str, style):
    font_dict = FONTS_MAP.get(style, FONTS_MAP["2"])
    return "".join(font_dict.get(char, char) for char in time_str)

# ==================== دالة تشغيل السورس ووقت بغداد ====================
async def start_user_source(client_session_name, expire_timestamp, user_tg_id):
    user_app = Client(
        client_session_name,
        api_id=API_ID,
        api_hash=API_HASH
    )
    
    is_clock_running = [True]  
    current_font_style = ["2"]

    async def update_clock():
        last_updated_time = ""
        while is_clock_running[0]:
            try:
                # حساب وقت بغداد بدقة (UTC + 3)
                now = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%I:%M")
                if now != last_updated_time:
                    clock_text = format_time_with_font(now, current_font_style[0])
                    await user_app.update_profile(last_name=f"{clock_text}")
                    last_updated_time = now
            except Exception as e:
                print(f"خطأ بالساعة: {e}")
            await asyncio.sleep(15)

    async def monitor_expiration():
        while is_clock_running[0]:
            if time.time() >= expire_timestamp:
                try: await user_app.stop()
                except: pass
                is_clock_running[0] = False
                if str(user_tg_id) in user_sessions:
                    del user_sessions[str(user_tg_id)]
                    db["user_sessions"] = user_sessions
                    save_database(db)
                break
            await asyncio.sleep(60)

    @user_app.on_message(filters.me & filters.command(["الاوامر", "الأوامر", "م"], prefixes="."))
    async def main_menu(c, m):
        await m.edit_text(f"⚡️ **قائمة اوامر سورس الربيعي (توقيت بغداد)** ✨\n\n• `.م1` إلى `.م10` الأوامر مفعلة.\n[ المطور: @{ADMIN_USERNAME} ]")

    try:
        await user_app.start()
        asyncio.create_task(update_clock())
        asyncio.create_task(monitor_expiration())
        user_active_sources[user_tg_id] = {"app": user_app, "session": client_session_name}
    except Exception as e:
        print(f"فشل تشغيل سورس المستخدم: {e}")

# ==================== بوت التنصيب الرئيسي ====================

@bot_app.on_message(filters.command("code") & filters.private)
async def create_subscription_code(client, message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    if len(args) < 3: return await message.reply_text("⚠️ استعمل: `/code [الكود] [الايام]`")
    code_text, days = args[1], int(args[2])
    active_subscriptions[code_text] = {"days": days, "used": False}
    db["subscriptions"] = active_subscriptions
    save_database(db)
    await message.reply_text(f"✅ **تم إنشاء الكود:** `{code_text}` لمدة `{days} أيام`")

@bot_app.on_message(filters.command("start") & filters.private)
async def start_bot(client, message):
    temp_users[message.from_user.id] = {"step": "waiting_code"}
    await message.reply_text(f"👋 أهلاً بك في بوت تنصيب **سورس الربيعي** ⚡️\n\n🔑 أرسل **كود الاشتراك** الخاص بك الآن:")

@bot_app.on_message(filters.private & ~filters.command(["start", "code"]))
async def handle_user_input(client, message):
    user_id = message.from_user.id
    if user_id not in temp_users: return await message.reply_text("أرسل /start للبدء.")
    
    user_data = temp_users[user_id]
    step = user_data.get("step")

    if step == "waiting_code":
        code = message.text.strip()
        if code not in active_subscriptions or active_subscriptions[code]["used"]:
            return await message.reply_text("❌ **الكود غير صحيح أو مستخدم مسبقاً!**")
        
        sub_info = active_subscriptions[code]
        sub_info["used"] = True
        user_data["days"] = sub_info["days"]
        db["subscriptions"] = active_subscriptions
        save_database(db)
        
        user_data["step"] = "waiting_phone"
        await message.reply_text("📱 أرسل رقم هاتفك مع رمز الدولة (مثال:\n`+9647700000000`):")

    elif step == "waiting_phone":
        phone = message.text.strip()
        session_name = f"rubaie_session_{user_id}"
        user_client = Client(session_name, api_id=API_ID, api_hash=API_HASH)
        await user_client.connect()
        try:
            sent_code = await user_client.send_code(phone)
            user_data.update({"client": user_client, "phone": phone, "phone_code_hash": sent_code.phone_code_hash, "step": "waiting_tg_code"})
            await message.reply_text("✉️ تم إرسال كود التحقق لحسابك في تليجرام. أرسل الكود الآن:")
        except Exception as e:
            await user_client.disconnect()
            del temp_users[user_id]
            await message.reply_text(f"❌ خطأ: `{e}`")

    elif step == "waiting_tg_code":
        raw_code = message.text.strip()
        code = "".join(filter(str.isdigit, raw_code))
        try:
            await user_data["client"].sign_in(user_data["phone"], user_data["phone_code_hash"], code)
            await finalize_success(message, user_data["client"], user_data)
        except SessionPasswordNeeded:
            user_data["step"] = "waiting_password"
            await message.reply_text("🔒 **الحساب محمي بكلمة مرور.** أرسل كلمة المرور:")
        except PhoneCodeInvalid:
            await message.reply_text("❌ **الكود غير صحيح!** أعد إرساله:")
        except Exception as e:
            await message.reply_text(f"❌ خطأ: `{e}`")
            try: await user_data["client"].disconnect()
            except: pass
            del temp_users[user_id]

    elif step == "waiting_password":
        try:
            await user_data["client"].check_password(message.text.strip())
            await finalize_success(message, user_data["client"], user_data)
        except Exception as e:
            await message.reply_text(f"❌ كلمة المرور خطأ: `{e}`")
            try: await user_data["client"].disconnect()
            except: pass
            del temp_users[user_id]

async def finalize_success(message, user_client, user_data):
    session_name = user_client.name
    await user_client.disconnect()
    expire_time = time.time() + (user_data.get("days", 1) * 86400)
    
    user_sessions[str(message.from_user.id)] = {"session_name": session_name, "expire_time": expire_time}
    db["user_sessions"] = user_sessions
    save_database(db)

    asyncio.create_task(start_user_source(session_name, expire_time, message.from_user.id))
    if message.from_user.id in temp_users: del temp_users[message.from_user.id]
    await message.reply_text("✅ **تم تنصيب السورس وتفعيل توقيت بغداد بنجاح!** 🚀")

async def restore_saved_sessions():
    current_time = time.time()
    for uid_str, data in list(user_sessions.items()):
        if current_time < data["expire_time"]:
            asyncio.create_task(start_user_source(data["session_name"], data["expire_time"], int(uid_str)))
        else:
            del user_sessions[uid_str]
    db["user_sessions"] = user_sessions
    save_database(db)

# التشغيل الصحيح الذي يمنع تعليق البوت
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(restore_saved_sessions())
    bot_app.run()
