import asyncio
import os
import json
import time
from datetime import datetime, timezone, timedelta
from pyrogram import Client, filters, idle
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==================== الإعدادات الأساسية ====================
BOT_TOKEN = "8812362880:AAEkXtnj03KM27QiP9kADZyQHKASe9WEMcY"
API_ID = 38183563
API_HASH = "7d3d3b9379c6840a72c983865c8d927d"

ADMIN_ID = 7989509412
ADMIN_USERNAME = "Al_Rubaie15"

# ==================== إعدادات البروكسي لتجاوز الحظر ====================
USE_PROXY = False  # اجعلها True إذا أردت تفعيل البروكسي وأدخل البيانات أدناه
PROXY_CONFIG = {
    "scheme": "socks5",  # أو "http" أو "mtproto"
    "hostname": "PROXY_IP_HERE",
    "port": 1080,
    "username": "USERNAME_IF_ANY",
    "password": "PASSWORD_IF_ANY"
} if USE_PROXY else None

BAGHDAD_TZ = timezone(timedelta(hours=3))

bot_app = Client(
    "Rubaie_Maker_Bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    proxy=PROXY_CONFIG
)

DB_FILE = "database.json"

def load_database():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"subscriptions": {}, "user_sessions": {}, "forced_channel": None}

def save_database(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"خطأ في حفظ قاعدة البيانات: {e}")

db = load_database()
active_subscriptions = db.get("subscriptions", {})
user_sessions = db.get("user_sessions", {})
forced_channel = db.get("forced_channel", None)

temp_users = {}       
user_active_sources = {}  
muted_users = set()       
original_profile = {}     

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

def decorate_text(text, style_num):
    if style_num == "1":
        return "".join(chr(ord(c) + 65248) if 33 <= ord(c) <= 126 else c for c in text)
    elif style_num == "2":
        chars = {"a":"𝖆","b":"𝖇","c":"𝖈","d":"🇩","e":"𝖊","f":"𝖋","g":"𝖌","h":"𝖍","i":"𝖎","j":"j","k":"𝖐","l":"𝖑","m":"𝖒","n":"𝖓","o":"𝖔","p":"𝖕","q":"q","r":"𝖗","s":"𝖘","t":"𝖙","u":"𝖚","v":"v","w":"w","x":"x","y":"y","z":"z"}
        return "".join(chars.get(c.lower(), c) for c in text)
    elif style_num == "3":
        return " ⚡️ ".join(text)
    elif style_num == "4":
        return f"༺ {text} ༻"
    elif style_num == "5":
        return f"• {text} •"
    elif style_num == "6":
        return "".join(c + "̸" for c in text)
    elif style_num == "7":
        return f"『 {text} 』"
    elif style_num == "8":
        return f"𝓡ُ {text} 𝓡ُ"
    return text

# ==================== دالة تشغيل السورس بكافة الأوامر ====================
async def start_user_source(client_session_name, expire_timestamp, user_tg_id):
    user_app = Client(
        client_session_name,
        api_id=API_ID,
        api_hash=API_HASH,
        proxy=PROXY_CONFIG
    )
    
    is_clock_running = [True]  
    current_font_style = ["2"]

    async def update_clock():
        last_updated_time = ""
        while is_clock_running[0]:
            try:
                now = datetime.now(BAGHDAD_TZ).strftime("%I:%M")
                if now != last_updated_time:
                    clock_text = format_time_with_font(now, current_font_style[0])
                    await user_app.update_profile(last_name=f"{clock_text}")
                    last_updated_time = now
            except Exception as e:
                print(f"خطأ بالساعة للمستخدم: {e}")
            await asyncio.sleep(15)

    async def monitor_expiration():
        while is_clock_running[0]:
            if time.time() >= expire_timestamp:
                try:
                    await user_app.stop()
                except:
                    pass
                is_clock_running[0] = False
                if str(user_tg_id) in user_sessions:
                    del user_sessions[str(user_tg_id)]
                    db["user_sessions"] = user_sessions
                    save_database(db)
                if user_tg_id in user_active_sources:
                    del user_active_sources[user_tg_id]
                break
            await asyncio.sleep(60)

    # ==================== نظام الكتم التلقائي (يعمل حتى لو كنت عضواً في الكروبات) ====================
    @user_app.on_message(~filters.me & (filters.group | filters.supergroup | filters.private))
    async def global_mute_handler(c, m):
        if m.from_user and m.from_user.id in muted_users:
            try:
                await m.delete()
            except Exception as e:
                print(f"خطأ في حذف رسالة الشخص المكتوم: {e}")
            m.stop_propagation()

    # ==================== القائمة الرئيسية ====================
    @user_app.on_message(filters.me & filters.command(["الاوامر", "الأوامر", "م"], prefixes="."))
    async def main_menu(c, m):
        await m.edit_text(
            "┌─────── **source Al-Rubaie** ───────┐\n\n"
            "• `.م1` ➔ اوامر الخاص وكتم الأعضاء\n"
            "• `.م3` ➔ اوامر النشر التلقائي\n"
            "• `.م12` ➔ اوامر المغادرات والكروبات\n"
            "• `.م19` ➔ اوامر الزخرفة (8 أنواع)\n"
            "• `.م23` ➔ اوامر التقليد والانتحال\n"
            "• `.م29` ➔ اوامر التحذيرات ونضع النوم\n\n"
            "• `.create_groups` ➔ صانع الكروبات التلقائي 🚀\n\n"
            f"└─────── **@{ADMIN_USERNAME}** ───────┘"
        )

    @user_app.on_message(filters.me & filters.command(["م1"], prefixes="."))
    async def menu_1(c, m):
        await m.edit_text("⭐ **أوامر الخاص والكتم (.م1):**\n• استخدم `.كتم` بالرد على الشخص لكتمه في الخاص والكروبات (حتى لو كنت عضواً).\n• استخدم `.سماح` لإلغاء الكتم.")

    @user_app.on_message(filters.me & filters.command(["م12"], prefixes="."))
    async def menu_12(c, m):
        await m.edit_text("🌐 **أوامر المغادرات والكروبات (.م12):**\n• استخدم الأمر `.create_groups [العدد]` لإنشاء الكروبات التلقائية وإرسال الروابط للخاص.")

    @user_app.on_message(filters.me & filters.command(["زخرفة", "زخرفه"], prefixes="."))
    async def decorate_command(c, m):
        args = m.text.split(maxsplit=2)
        if len(args) < 3:
            return await m.edit_text("⚠️ **استخدام خاطئ!**\nاكتب هكذا: `.زخرفة [1-8] [النص المراد زخرفته]`")
        style_num, text_to_decorate = args[1], args[2]
        if style_num not in [str(i) for i in range(1, 9)]:
            return await m.edit_text("⚠️ **اختر رقماً للزخرفة من 1 إلى 8 فقط!**")
        result = decorate_text(text_to_decorate, style_num)
        await m.edit_text(f"✨ **النص بعد الزخرفة (نوع {style_num}):**\n\n`{result}`")

    @user_app.on_message(filters.me & filters.command(["create_groups", "صنع_كروبات"], prefixes="."))
    async def create_auto_groups_cmd(c, m):
        total_groups = 50
        args = m.text.split()
        if len(args) > 1 and args[1].isdigit():
            total_groups = int(args[1])
        await m.edit_text(f"⌔︙جاري بدء صنع {total_groups} كروب...")
        for i in range(1, total_groups + 1):
            try:
                current_date_str = datetime.now(BAGHDAD_TZ).strftime("%Y-%m-%d")
                group_title = f"Al-Rubaie Group {current_date_str} #{i}"
                group_about = f"source by @{ADMIN_USERNAME}"
                created_chat = await c.create_supergroup(title=group_title, description=group_about)
                chat_id = created_chat.id
                message_text = "الذكريات تجمعنا يوما ما"
                for _ in range(7):
                    await c.send_message(chat_id, message_text)
                    await asyncio.sleep(0.4)
                invite_link = await c.export_chat_invite_link(chat_id)
                await c.leave_chat(chat_id)
                await c.send_message("me", f"⌔︙تم صنع كروب رقم {i}\n🌐︙الرابط : {invite_link}")
                await asyncio.sleep(2)
            except Exception as e:
                await c.send_message("me", f"❌ خطأ في الكروب رقم {i}: {str(e)}")
                await asyncio.sleep(3)
        await c.send_message("me", "✅ **تم الانتهاء من إنشاء جميع الكروبات وإرسال الروابط بنجاح!**")

    @user_app.on_message(filters.me & filters.command(["كتم"], prefixes="."))
    async def mute_user_cmd(c, m):
        uid = None
        if m.reply_to_message and m.reply_to_message.from_user:
            uid = m.reply_to_message.from_user.id
        elif len(m.text.split()) > 1:
            arg = m.text.split()[1]
            if arg.isdigit():
                uid = int(arg)
            else:
                try:
                    user_obj = await c.get_users(arg)
                    uid = user_obj.id
                except:
                    pass
        
        if uid:
            muted_users.add(uid)
            await m.edit_text(f"✨ **تم كتم المستخدم (`{uid}`) بنجاح في الخاص والكروبات!**")
        else:
            await m.edit_text("⚠️ **رد على الشخص أو أكتب آيديه/معرفه لكتمه.**")

    @user_app.on_message(filters.me & filters.command(["سماح"], prefixes="."))
    async def unmute_user_cmd(c, m):
        uid = None
        if m.reply_to_message and m.reply_to_message.from_user:
            uid = m.reply_to_message.from_user.id
        elif len(m.text.split()) > 1:
            arg = m.text.split()[1]
            if arg.isdigit():
                uid = int(arg)
            else:
                try:
                    user_obj = await c.get_users(arg)
                    uid = user_obj.id
                except:
                    pass

        if uid and uid in muted_users:
            muted_users.remove(uid)
            await m.edit_text(f"✨ **تم إلغاء كتم المستخدم (`{uid}`) بنجاح!**")
        else:
            await m.edit_text("ℹ️ **المستخدم ليس في قائمة الكتم أو لم تحدده بشكل صحيح.**")

    @user_app.on_message(filters.me & filters.command(["انتحال"], prefixes="."))
    async def impersonate_cmd(c, m):
        if m.reply_to_message and m.reply_to_message.from_user:
            target = m.reply_to_message.from_user
            me = await c.get_me()
            original_profile['first_name'] = me.first_name
            original_profile['bio'] = (await c.get_chat(me.id)).bio or ""
            try:
                target_chat = await c.get_chat(target.id)
                await c.update_profile(first_name=target.first_name, bio=target_chat.bio or "")
                if target.photo:
                    photo = await c.download_media(target.photo.big_file_id)
                    await c.set_profile_photo(photo=photo)
                    os.remove(photo)
                await m.edit_text("⚽️ **تم انتحال الحساب بنجاح!** 🎭")
            except Exception as e:
                await m.edit_text(f"❌ خطأ: {e}")
        else:
            await m.edit_text("⚠️ **رد على الشخص المراد انتحاله.**")

    @user_app.on_message(filters.me & filters.command(["اعاده", "إعادة"], prefixes="."))
    async def restore_profile_cmd(c, m):
        try:
            if 'first_name' in original_profile:
                await c.update_profile(first_name=original_profile['first_name'], bio=original_profile.get('bio', ''))
                await m.edit_text("⚽️ **تمت إرجاع شخصيتك الأصلية بنجاح!** ✨")
            else:
                await m.edit_text("ℹ️ لا توجد نسخة سابقة محفوظة.")
        except Exception as e:
            await m.edit_text(f"❌ خطأ: {e}")

    try:
        await user_app.start()
        asyncio.create_task(update_clock())
        asyncio.create_task(monitor_expiration())
        user_active_sources[user_tg_id] = {"app": user_app, "session": client_session_name}
        print(f"✅ تم تشغيل سورس المستخدم بنجاح: {client_session_name}")
    except Exception as e:
        print(f"❌ فشل تشغيل سورس المستخدم: {e}")

# ==================== بوت التنصيب (رئيسي) ====================

@bot_app.on_message(filters.command("code") & filters.private)
async def create_subscription_code(client, message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 3:
        return await message.reply_text("⚠️ `/code [الكود] [عدد الأيام]`")
    code_text, days = args[1], int(args[2])
    active_subscriptions[code_text] = {"days": days, "used": False}
    db["subscriptions"] = active_subscriptions
    save_database(db)
    await message.reply_text(f"✅ **تم إنشاء الكود:** `{code_text}` لمدة `{days} أيام`")

@bot_app.on_message(filters.command("addch") & filters.private)
async def set_forced_channel(client, message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    global forced_channel
    if len(args) < 2: return await message.reply_text("⚠️ `/addch @ChannelUsername`")
    forced_channel = args[1].strip()
    db["forced_channel"] = forced_channel
    save_database(db)
    await message.reply_text(f"✅ تم ضبط القناة الإجبارية: `{forced_channel}`")

@bot_app.on_message(filters.command("delch") & filters.private)
async def remove_forced_channel(client, message):
    if message.from_user.id != ADMIN_ID: return
    global forced_channel
    forced_channel = None
    db["forced_channel"] = None
    save_database(db)
    await message.reply_text("✅ تم إلغاء القناة الإجبارية.")

async def check_subscription(client, user_id):
    if user_id == ADMIN_ID or not forced_channel: return True
    try:
        member = await client.get_chat_member(forced_channel, user_id)
        if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
            return True
    except: return False
    return False

@bot_app.on_message(filters.command("start") & filters.private)
async def start_bot(client, message):
    user_id = message.from_user.id
    if forced_channel and not await check_subscription(client, user_id):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 اشترك في قناة البوت", url=f"https://t.me/{forced_channel.replace('@', '')}")],
            [InlineKeyboardButton("🔄 تحقق من الاشتراك", callback_data="check_sub")]
        ])
        return await message.reply_text("⚠️ **يجب عليك الاشتراك في قناة البوت أولاً!**", reply_markup=keyboard)

    temp_users[user_id] = {"step": "waiting_code"}
    await message.reply_text(f"👋 أهلاً بك في بوت تنصيب **سورس الربيعي برو** ⚡️\n\n🔑 أرسل **كود الاشتراك** لتفعيل التنصيب:")

@bot_app.on_callback_query(filters.regex("check_sub"))
async def check_sub_callback(client, callback_query):
    user_id = callback_query.from_user.id
    if await check_subscription(client, user_id):
        await callback_query.message.delete()
        temp_users[user_id] = {"step": "waiting_code"}
        await callback_query.message.reply_text("✅ **تم التحقق!** أرسل كود الاشتراك الآن:")
    else:
        await callback_query.answer("❌ لم تشترك في القناة بعد!", show_alert=True)

@bot_app.on_message(filters.private & ~filters.command("start") & ~filters.command("code") & ~filters.command("addch") & ~filters.command("delch"))
async def handle_user_input(client, message):
    user_id = message.from_user.id
    if user_id not in temp_users:
        return await message.reply_text("أرسل /start للبدء من جديد.")
    
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
        await message.reply_text("📱 أرسل رقم هاتفك مع رمز الدولة (`+964...`):")

    elif step == "waiting_phone":
        phone_number = message.text.strip()
        session_name = f"rubaie_session_{user_id}"
        user_client = Client(
            session_name,
            api_id=API_ID,
            api_hash=API_HASH,
            proxy=PROXY_CONFIG
        )
        await user_client.connect()
        try:
            sent_code = await user_client.send_code(phone_number)
            user_data.update({"client": user_client, "phone": phone_number, "phone_code_hash": sent_code.phone_code_hash, "step": "waiting_tg_code"})
            await message.reply_text("✉️ تم إرسال كود التليجرام، أرسله الآن:")
        except Exception as e:
            await user_client.disconnect()
            del temp_users[user_id]
            await message.reply_text(f"❌ خطأ: `{e}`")

    elif step == "waiting_tg_code":
        code = message.text.strip().replace(" ", "")
        try:
            await user_data["client"].sign_in(user_data["phone"], user_data["phone_code_hash"], code)
            await finalize_success(message, user_data["client"], user_data)
        except SessionPasswordNeeded:
            user_data["step"] = "waiting_password"
            await message.reply_text("🔒 **الحساب محمي بالتحقق بخطوتين.** أرسل كلمة المرور:")
        except PhoneCodeInvalid:
            await message.reply_text("❌ **الكود غير صحيح!** أرسله مجدداً:")
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
            await message.reply_text(f"❌ كلمة المرور غير صحيحة: `{e}`")
            try: await user_data["client"].disconnect()
            except: pass
            del temp_users[user_id]

async def finalize_success(message, user_client, user_data):
    await message.reply_text("🎉 **تم تسجيل الدخول وجاري تشغيل سورس الربيعي...**")
    session_name = user_client.name
    await user_client.disconnect()
    days_count = user_data.get("days", 1)
    expire_timestamp = time.time() + (days_count * 86400)
    
    user_sessions[str(message.from_user.id)] = {
        "session_name": session_name,
        "expire_time": expire_timestamp
    }
    db["user_sessions"] = user_sessions
    save_database(db)

    asyncio.create_task(start_user_source(session_name, expire_timestamp, message.from_user.id))
    if message.from_user.id in temp_users:
        del temp_users[message.from_user.id]
    await message.reply_text(f"✅ **تم تنصيب سورس الربيعي بنجاح لمدة {days_count} أيام!** 🚀\n[ المطور: @{ADMIN_USERNAME} ]")

async def restore_saved_sessions():
    current_time = time.time()
    for uid_str, data in list(user_sessions.items()):
        if current_time < data["expire_time"]:
            asyncio.create_task(start_user_source(data["session_name"], data["expire_time"], int(uid_str)))
        else:
            del user_sessions[uid_str]
    db["user_sessions"] = user_sessions
    save_database(db)

async def main():
    print(f"🚀  يعملس الربيعي للمطور @{ADMIN_USERNAME}]ل الآن...")
    await restore_saved_sessions()
    await bot_app.start()
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
