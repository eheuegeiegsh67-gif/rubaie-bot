import asyncio
import os
import json
import time
from datetime import datetime, timezone, timedelta
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, UserNotParticipant
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

# ==================== نظام قاعدة البيانات المحفوظة (JSON) ====================
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

# ==================== دالة تشغيل السورس بكافة مميزاته ====================
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
                # ضبط وقت بغداد بدقة يدوياً لتجاوز توقيت سيرفر Railway
                now = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%I:%M")
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

    @user_app.on_message(filters.me & filters.command(["الاوامر", "الأوامر", "م"], prefixes="."))
    async def main_menu(c, m):
        await m.edit_text(
            "⚡️ **قائمة اوامر سورس الربيعي (نشر تلقائي بتوقيت بغداد)** ✨\n\n"
            "🕑 الوقت واللقب: `.م1` ⭐\n"
            "🎁 التخزين السحابي: `.م2` 🎁\n"
            "🗣 النشر (نسخ تلقائي): `.م3` 🎙\n"
            "✈ أوامر الحفظ والنسخ: `.م4` ✈\n"
            "😴 وضع النوم والتحذيرات: `.م10` 🌙\n"
            "✨ نظام الكتم (خاص وكروبات): `.كتم` / `.سماح` ✨\n"
            "⚽️ الانتحال: `.انتحال` / `.اعاده` ⚽️\n"
            "❄ معلومات الحساب: `.ايدي` 🤔\n"
            "🔥 التنظيف: `.تنضيف [العدد]` 💯\n\n"
            f"[ المطور: @{ADMIN_USERNAME} ]"
        )

    @user_app.on_message(filters.me & filters.command(["م1"], prefixes="."))
    async def menu_1(c, m):
        await m.edit_text("⭐ **أوامر الوقت واللقب (.م1):**\n\n• أرسل رقم من 1 إلى 8 لتغيير خط الساعة (بتوقيت بغداد).")

    @user_app.on_message(filters.me & filters.command(["م2"], prefixes="."))
    async def menu_2(c, m):
        await m.edit_text("🎁 **أوامر التخزين السحابي (.م2):**\n\n• رد بـ `.حفظ` على أي رسالة لرفعها للمحفوظات.")

    @user_app.on_message(filters.me & filters.command(["م3"], prefixes="."))
    async def menu_3(c, m):
        await m.edit_text("🎙 **أوامر النشر التلقائي (.م3):**\n\n• رد بـ `.نشر` لنشر النص مباشرة (بدون توجيه) في كل المجموعات مع تقرير كامل.\n• `.إيقاف_نشر` لإيقاف عملية النشر الحالية.")

    @user_app.on_message(filters.me & filters.command(["م4"], prefixes="."))
    async def menu_4(c, m):
        await m.edit_text("✈ **أوامر الحفظ والنسخ (.م4):**\n\n• `.نسخ` لنسخ النصوص المقفلة.")

    @user_app.on_message(filters.me & filters.command(["م10"], prefixes="."))
    async def menu_10(c, m):
        await m.edit_text("🌙 **أوامر وضع النوم والتحذيرات (.م10):**\n\n• `.نوم` ➔ لتفعيل وضع النوم والتحذيرات (كتم تلقائي بعد 5 رسائل إزعاج).\n• `.كاعد` أو `.صاحي` ➔ لإطفاء وضع النوم.")

    @user_app.on_message(filters.me & filters.command(["نشر"], prefixes="."))
    async def auto_post_cmd(c, m):
        if not m.reply_to_message:
            await m.edit_text("⚠️ **قم بالرد على الرسالة المراد نشرها في المجموعات!**")
            return

        stop_posting_flags[user_tg_id] = False
        start_time_str = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%Y-%m-%d | %I:%M:%S %p")
        
        await m.edit_text("🔄 **جاري بدء النشر التلقائي في المجموعات...\n(لإيقافه اكتب: `.إيقاف_نشر`)**")
        
        success_count, fail_count = 0, 0
        target_msg = m.reply_to_message

        async for dialog in c.get_dialogs():
            if stop_posting_flags.get(user_tg_id, False):
                break
            if dialog.chat.type.value in ["group", "supergroup"]:
                try:
                    chat_id = dialog.chat.id
                    if target_msg.text:
                        await c.send_message(chat_id, target_msg.text)
                    elif target_msg.caption:
                        await target_msg.copy(chat_id)
                    else:
                        await target_msg.copy(chat_id)
                        
                    success_count += 1
                    await asyncio.sleep(2.5)
                except Exception as e:
                    fail_count += 1

        end_time_str = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%I:%M:%S %p")
        
        report_text = (
            f"📊 **تقرير عملية النشر التلقائي:**\n\n"
            f"• وقت البدء: `{start_time_str}`\n"
            f"• وقت الانتهاء: `{end_time_str}`\n"
            f"• حالة النشر: `{'تم الإيقاف يدوياً 🛑' if stop_posting_flags.get(user_tg_id, False) else 'مكتمل بنجاح ✅'}`\n"
            f"• عدد المجموعات المنشور لها: `{success_count}`\n"
            f"• المجموعات المتعذرة: `{fail_count}`\n\n"
            f"[ المطور: @{ADMIN_USERNAME} ]"
        )
        await m.edit_text(report_text)

    @user_app.on_message(filters.me & filters.command(["إيقاف_نشر", "ايقاف_النشر", "وقف_النشر"], prefixes="."))
    async def stop_posting_cmd(c, m):
        stop_posting_flags[user_tg_id] = True
        await m.edit_text("🛑 **تم إرسال أمر إيقاف النشر، سيتم التوقف فوراً...**")

    @user_app.on_message(filters.me & filters.command(["نوم"], prefixes="."))
    async def sleep_on(c, m):
        sleep_mode[0] = True
        warn_counts.clear()
        await m.edit_text("🌙 **تم تفعيل وضع النوم والتحذيرات بنجاح!**")

    @user_app.on_message(filters.me & filters.command(["كاعد", "صاحي", "استيقظ"], prefixes="."))
    async def sleep_off(c, m):
        sleep_mode[0] = False
        warn_counts.clear()
        await m.edit_text("☀️ **تم إطفاء وضع النوم وعودتك للوضع الطبيعي!**")

    @user_app.on_message(filters.incoming & filters.private & ~filters.me)
    async def auto_reply_sleep(c, m):
        if m.from_user and m.from_user.id in muted_users:
            try: await m.delete(revoke=True)
            except: pass
            m.stop_propagation()
            return

        if sleep_mode[0]:
            user_id = m.from_user.id
            warn_counts[user_id] = warn_counts.get(user_id, 0) + 1
            current_warns = warn_counts[user_id]

            if current_warns >= 5:
                muted_users.add(user_id)
                try: await m.reply("🚫 **تم كتمك تلقائياً لتجاوز الحد المسموح من الإزعاج أثناء وضع النوم!**")
                except: pass
            else:
                try: await m.reply(f"😴 **المستخدم نائم حالياً ({current_warns}/5). يرجى عدم الإزعاج!**")
                except: pass

    @user_app.on_message(filters.me & filters.command(["كتم"], prefixes="."))
    async def mute_user_cmd(c, m):
        uid = None
        if m.reply_to_message and m.reply_to_message.from_user:
            uid = m.reply_to_message.from_user.id
        elif m.chat.type.value == "private":
            uid = m.chat.id

        if uid:
            muted_users.add(uid)
            await m.edit_text("✨ **تم كتم الشخص بنجاح!**")
        else:
            await m.edit_text("⚠️ **قم بالرد على رسالة الشخص المراد كتمه.**")

    @user_app.on_message(filters.me & filters.command(["سماح"], prefixes="."))
    async def unmute_user_cmd(c, m):
        uid = None
        if m.reply_to_message and m.reply_to_message.from_user:
            uid = m.reply_to_message.from_user.id
        elif m.chat.type.value == "private":
            uid = m.chat.id

        if uid and uid in muted_users:
            muted_users.remove(uid)
            if uid in warn_counts: del warn_counts[uid]
            await m.edit_text("✨ **تم إلغاء كتم الشخص بنجاح!**")
        else:
            await m.edit_text("ℹ️ **المستخدم ليس في قائمة الكتم.**")

    @user_app.on_message(filters.incoming & ~filters.me)
    async def check_muted_everywhere(c, m):
        if m.from_user and m.from_user.id in muted_users:
            try: await m.delete(revoke=True)
            except: pass
            m.stop_propagation()

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
                await m.edit_text(f"❌ حدث خطأ: {e}")
        else:
            await m.edit_text("⚠️ **قم بالرد على الشخص المراد انتحاله.**")

    @user_app.on_message(filters.me & filters.command(["اعاده", "إعادة"], prefixes="."))
    async def restore_profile_cmd(c, m):
        try:
            if 'first_name' in original_profile:
                await c.update_profile(first_name=original_profile['first_name'], bio=original_profile.get('bio', ''))
                await m.edit_text("⚽️ **تمت إعادة حسابك لشخصيتك الأصلية بنجاح!** ✨")
            else:
                await m.edit_text("ℹ️ لا توجد نسخة محفوظة سابقة.")
        except Exception as e:
            await m.edit_text(f"❌ حدث خطأ: {e}")

    @user_app.on_message(filters.me & filters.command(["ايدي", "الإيدي"], prefixes="."))
    async def my_id_cmd(c, m):
        me = await c.get_me()
        await m.edit_text(f"❄ **معلومات حسابك:**\n• الأيدي: `{me.id}`\n• المعرف: `@{me.username}`")

    @user_app.on_message(filters.me & filters.command(["تنضيف", "تنظيف"], prefixes="."))
    async def purge_msgs(c, m):
        args = m.text.split()
        count = int(args[1]) if len(args) > 1 and args[1].isdigit() else 5
        deleted = 0
        async for msg in c.get_chat_history(m.chat.id, limit=count+1):
            if msg.from_user and msg.from_user.is_self and msg.id != m.id:
                try:
                    await msg.delete()
                    deleted += 1
                except:
                    pass
        await m.edit_text(f"🔥 **تم حذف ({deleted}) من رسائلك بنجاح!**")
        await asyncio.sleep(3)
        await m.delete()

    @user_app.on_message(filters.me & filters.text)
    async def fonts_handler(c, m):
        txt = m.text.strip()
        if txt in FONTS_MAP:
            current_font_style[0] = txt
            now = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%I:%M")
            clock_text = format_time_with_font(now, txt)
            try:
                await user_app.update_profile(last_name=f"{clock_text}")
                await m.edit_text(f"🟢 **تم تغيير خط الساعة إلى ({txt}) وضبط الوقت حسب بغداد: ({clock_text})**")
            except:
                pass

    try:
        await user_app.start()
        asyncio.create_task(update_clock())
        asyncio.create_task(monitor_expiration())
        user_active_sources[user_tg_id] = {"app": user_app, "session": client_session_name}
    except Exception as e:
        print(f"❌ فشل تشغيل سورس المستخدم: {e}")

# ==================== بوت التنصيب (رئيسي) ====================

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

@bot_app.on_message(filters.command("اضافه_قناة") & filters.private)
async def add_forced_channel(client, message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split(maxsplit=1)
    if len(args) < 2: return await message.reply_text("⚠️ اكتب المعرف: `/اضافه_قناة معرف_القناة`")
    ch = args[1].strip().replace("@", "").replace("https://t.me/", "")
    if ch not in forced_channels:
        forced_channels.append(ch)
        db["forced_channels"] = forced_channels
        save_database(db)
        await message.reply_text(f"✅ تمت إضافة `@{ch}` للاشتراك الإجباري.")

@bot_app.on_message(filters.command("حذف_قناة") & filters.private)
async def remove_forced_channel(client, message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split(maxsplit=1)
    if len(args) < 2: return await message.reply_text("⚠️ اكتب المعرف: `/حذف_قناة معرف_القناة`")
    ch = args[1].strip().replace("@", "").replace("https://t.me/", "")
    if ch in forced_channels:
        forced_channels.remove(ch)
        db["forced_channels"] = forced_channels
        save_database(db)
        await message.reply_text(f"🗑 تم حذف `@{ch}`.")

async def check_all_subscriptions(client, user_id):
    if user_id == ADMIN_ID: return True
    if not forced_channels: return True
    for ch in forced_channels:
        try:
            member = await client.get_chat_member(ch, user_id)
            if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
                return False
        except:
            return False
    return True

@bot_app.on_message(filters.command("start") & filters.private)
async def start_bot(client, message):
    user_id = message.from_user.id
    if forced_channels and not await check_all_subscriptions(client, user_id):
        keyboard_buttons = [[InlineKeyboardButton(f"📢 اشترك في @{ch}", url=f"https://t.me/{ch}")] for ch in forced_channels]
        keyboard_buttons.append([InlineKeyboardButton("🔄 تحقق من الاشتراك", callback_data="check_sub")])
        return await message.reply_text("⚠️ **عذراً، يجب عليك الاشتراك في القنوات أولاً!**", reply_markup=InlineKeyboardMarkup(keyboard_buttons))

    temp_users[user_id] = {"step": "waiting_code"}
    await message.reply_text(f"👋 أهلاً بك في بوت تنصيب **سورس الربيعي** ⚡️\n\n🔑 أرسل **كود الاشتراك** الخاص بك الآن:")

@bot_app.on_callback_query(filters.regex("check_sub"))
async def check_sub_callback(client, cq):
    if await check_all_subscriptions(client, cq.from_user.id):
        await cq.message.delete()
        temp_users[cq.from_user.id] = {"step": "waiting_code"}
        await cq.message.reply_text("✅ **شكراً لاشتراكك!**\n\n🔑 الآن أرسل **كود الاشتراك** الخاص بك:")
    else:
        await cq.answer("❌ لم تشترك في جميع القنوات بعد!", show_alert=True)

@bot_app.on_message(filters.private & ~filters.command(["start", "code", "اضافه_قناة", "حذف_قناة"]))
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
        await message.reply_text(f"✅ **تم قبول الكود ({sub_info['days']} أيام)!**\n\n📱 أرسل رقم هاتفك مع رمز الدولة (مثال: `+9647700000000`):")

    elif step == "waiting_phone":
        phone = message.text.strip()
        session_name = f"rubaie_session_{user_id}"
        user_client = Client(session_name, api_id=API_ID, api_hash=API_HASH)
        await user_client.connect()
        try:
            sent_code = await user_client.send_code(phone)
            user_data.update({"client": user_client, "phone": phone, "phone_code_hash": sent_code.phone_code_hash, "step": "waiting_tg_code"})
            await message.reply_text("🔄 **تم إرسال كود التحقق لحسابك في تليجرام.**\nأرسل الكود الآن:")
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
            await message.reply_text("🔒 **الحساب محمي بكلمة مرور (تحقق بخطوتين).**\nأرسل كلمة المرور:")
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
    await message.reply_text(f"✅ **تم تنصيب سورس الربيعي بنجاح وتفعيل توقيت بغداد!** 🚀")

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
    await restore_saved_sessions()
    await bot_app.start()
    await asyncio.gather(*(c.wait() for c in bot_app.get_dialogs()))

if __name__ == "__main__":
    bot_app.run()
