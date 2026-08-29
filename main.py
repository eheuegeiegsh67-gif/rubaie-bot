import os
import json
import time
from datetime import datetime, timezone, timedelta
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import SessionPasswordNeeded
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8938082118:AAHWa070-4EKOTg5ukM50smhfyf"
API_ID = 38183563
API_HASH = "7d3d3b379c6840a72c983865c8d927d"

ADMIN_ID = 7989509412
ADMIN_USERNAME = "Al_Rubaie15"

# تحديد التوقيت (UTC+3) خلف الكواليس لتحديث الساعة فقط
BAGHDAD_TZ = timezone(timedelta(hours=3))

# بوت التحكم الرئيسي
bot_app = Client(
    "Rubaie_Maker_Bot",
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
sleep_mode = [False]      
warn_counts = {}          
last_warn_msgs = {}   
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
                print(f"انقضاء الوقت للمستخدم: {user_tg_id}")
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

    # ==================== القائمة الرئيسة ====================
    @user_app.on_message(filters.me & filters.command(["الاوامر", "الأوامر", "م"], prefixes="."))
    async def main_menu(c, m):
        await m.edit_text(
            "⚡️ **قائمة اوامر سورس الربيعي** ✨\n\n"
            "🕑 الوقت واللقب: `.م1` ⭐\n"
            "🎁 التخزين السحابي: `.م2` 🎁\n"
            "🗣 النشر والتوجيه: `.م3` 🎙\n"
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
        await m.edit_text("⭐ **أوامر الوقت واللقب (.م1):**\n\n• `.اسم وقتي` لتشغيل الساعة.\n• أرسل رقم من 1 إلى 8 لتغيير خط الساعة.")

    @user_app.on_message(filters.me & filters.command(["م2"], prefixes="."))
    async def menu_2(c, m):
        await m.edit_text("🎁 **أوامر التخزين السحابي (.م2):**\n\n• رد بـ `.حفظ` على أي رسالة لرفعها للمحفوظات.")

    @user_app.on_message(filters.me & filters.command(["م3"], prefixes="."))
    async def menu_3(c, m):
        await m.edit_text("🎙 **أوامر النشر والتوجيه (.م3):**\n\n• رد بـ `.نشر` أو `.توجيه` لنشرها بكل المجموعات.\n• `.إيقاف_نشر` لإيقاف عملية النشر الحالية.")

    @user_app.on_message(filters.me & filters.command(["م4"], prefixes="."))
    async def menu_4(c, m):
        await m.edit_text("✈ **أوامر الحفظ والنسخ (.م4):**\n\n• `.نسخ` لنسخ النصوص المقفلة.")

    @user_app.on_message(filters.me & filters.command(["م10"], prefixes="."))
    async def menu_10(c, m):
        await m.edit_text("🌙 **أوامر وضع النوم والتحذيرات (.م10):**\n\n• `.نوم` ➔ لتفعيل وضع النوم والتحذيرات التلقائية (حذف القديم وإرسال جديد حتى يصل للـ 5 ثم يكتمه).\n• `.كاعد` أو `.صاحي` ➔ لإطفاء وضع النوم.")

    # ==================== الأوامر والوظائف ====================

    @user_app.on_message(filters.me & filters.command(["نشر", "توجيه"], prefixes="."))
    async def auto_post_cmd(c, m):
        if not m.reply_to_message:
            await m.edit_text("⚠️ **قم بالرد على الرسالة المراد نشرها في المجموعات!**")
            return

        stop_posting_flags[user_tg_id] = False
        await m.edit_text("🔄 **جاري بدء النشر التلقائي في المجموعات...\n(لإيقافه في أي وقت اكتب: `.إيقاف_نشر`)**")
        
        success_count, fail_count = 0, 0

        async for dialog in c.get_dialogs():
            if stop_posting_flags.get(user_tg_id, False):
                break
            if dialog.chat.type.value in ["group", "supergroup"]:
                try:
                    await m.reply_to_message.forward(dialog.chat.id)
                    success_count += 1
                    await asyncio.sleep(2)
                except:
                    fail_count += 1

        if stop_posting_flags.get(user_tg_id, False):
            await m.edit_text(f"🛑 **تم إيقاف النشر التلقائي بنجاح!**\n• تم النشر في: `{success_count}` مجموعة.")
        else:
            await m.edit_text(f"✅ **تم الانتهاء من النشر التلقائي بنجاح!**\n• المنشور فيها: `{success_count}`\n• المتعذرة: `{fail_count}`")

    @user_app.on_message(filters.me & filters.command(["إيقاف_نشر", "ايقاف_النشر", "وقف_النشر"], prefixes="."))
    async def stop_posting_cmd(c, m):
        stop_posting_flags[user_tg_id] = True
        await m.edit_text("🛑 **تم إرسال أمر إيقاف النشر، سيتم التوقف فوراً...**")

    @user_app.on_message(filters.me & filters.command(["نوم"], prefixes="."))
    async def sleep_on(c, m):
        sleep_mode[0] = True
        warn_counts.clear()
        last_warn_msgs.clear()
        await m.edit_text("🌙 **تم تفعيل وضع النوم والتحذيرات بنجاح!**\nكل مراسلة ستتضمن تحديث التحذيرات (حذف القديم وإرسال جديد)، وعند وصوله 5 سيتم كتمه.")

    @user_app.on_message(filters.me & filters.command(["كاعد", "صاحي", "استيقظ"], prefixes="."))
    async def sleep_off(c, m):
        sleep_mode[0] = False
        warn_counts.clear()
        last_warn_msgs.clear()
        await m.edit_text("☀️ **تم إطفاء وضع النوم وعودتك للوضع الطبيعي!**")

    @user_app.on_message(filters.incoming & filters.private & ~filters.me)
    async def auto_reply_sleep(c, m):
        if m.from_user and m.from_user.id in muted_users:
            try:
                await m.delete(revoke=True)
            except:
                pass
            m.stop_propagation()
            return

        if sleep_mode[0]:
            user_id = m.from_user.id
            warn_counts[user_id] = warn_counts.get(user_id, 0) + 1
            current_warns = warn_counts[user_id]

            if user_id in last_warn_msgs:
                try:
                    await last_warn_msgs[user_id].delete()
                except:
                    pass

            if current_warns >= 5:
                muted_users.add(user_id)
                if user_id in last_warn_msgs:
                    del last_warn_msgs[user_id]
                try:
                    await m.reply("🚫 **لقد تجاوزت الحد المسموح من الرسائل (5/5) أثناء وضع النوم، تم كتمك تلقائياً!**")
                except:
                    pass
            else:
                try:
                    sent_msg = await m.reply(f"😴 **المستخدم في وضع النوم حالياً ({current_warns}/5). يرجى عدم الإزعاج!**")
                    last_warn_msgs[user_id] = sent_msg
                except:
                    pass

    @user_app.on_message(filters.me & filters.command(["كتم"], prefixes="."))
    async def mute_user_cmd(c, m):
        uid = None
        if m.reply_to_message and m.reply_to_message.from_user:
            uid = m.reply_to_message.from_user.id
        elif m.chat.type.value == "private":
            uid = m.chat.id

        if uid:
            me = await c.get_me()
            if uid == me.id or uid == int(BOT_TOKEN.split(":")[0]):
                await m.edit_text("⚠️ **لا يمكنك كتم نفسك أو بوت التنصيب!**")
                return

            muted_users.add(uid)
            await m.edit_text("✨ **تم كتم الشخص بنجاح (سيتم حذف رسائله في الخاص والكروبات التي تتواجد بها)!**")
        else:
            await m.edit_text("⚠️ **قم بالرد على رسالة الشخص المراد كتمه في الكروب أو الخاص، أو اكتب الأمر في محادثته الخاصة.**")

    @user_app.on_message(filters.me & filters.command(["سماح"], prefixes="."))
    async def unmute_user_cmd(c, m):
        uid = None
        if m.reply_to_message and m.reply_to_message.from_user:
            uid = m.reply_to_message.from_user.id
        elif m.chat.type.value == "private":
            uid = m.chat.id

        if uid and uid in muted_users:
            muted_users.remove(uid)
            if uid in warn_counts:
                del warn_counts[uid]
            if uid in last_warn_msgs:
                del last_warn_msgs[uid]
            await m.edit_text("✨ **تم إلغاء كتم الشخص بنجاح!**")
        else:
            await m.edit_text("ℹ️ **المستخدم ليس في قائمة الكتم، أو لم تحدد الشخص بشكل صحيح.**")

    @user_app.on_message(filters.incoming & ~filters.me)
    async def check_muted_everywhere(c, m):
        if m.from_user and m.from_user.id in muted_users:
            try:
                await m.delete(revoke=True)
            except:
                pass
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
                target_bio = target_chat.bio or ""
                await c.update_profile(first_name=target.first_name, bio=target_bio)
                if target.photo:
                    photo = await c.download_media(target.photo.big_file_id)
                    await c.set_profile_photo(photo=photo)
                    os.remove(photo)
                await m.edit_text("⚽️ **تم انتحال الحساب بنجاح!** 🎭")
            except Exception as e:
                await m.edit_text(f"❌ حدث خطأ أثناء الانتحال: {e}")
        else:
            await m.edit_text("⚠️ **قم بالرد على الشخص المراد انتحاله.**")

    @user_app.on_message(filters.me & filters.command(["اعاده", "إعادة"], prefixes="."))
    async def restore_profile_cmd(c, m):
        try:
            if 'first_name' in original_profile:
                await c.update_profile(first_name=original_profile['first_name'], bio=original_profile.get('bio', ''))
                await m.edit_text("⚽️ **تمت إعادة حسابك لشخصيتك الأصلية بنجاح!** ✨")
            else:
                await m.edit_text("ℹ️ لا توجد نسخة محفوظة سابقة للاستعادة.")
        except Exception as e:
            await m.edit_text(f"❌ حدث خطأ: {e}")

    @user_app.on_message(filters.me & filters.command(["ايدي", "الإيدي"], prefixes="."))
    async def my_id_cmd(c, m):
        me = await c.get_me()
        await m.edit_text(
            f"❄ **معلومات حسابك الشخصي:**\n\n"
            f"• الاسم: `{me.first_name}`\n"
            f"• المعرف: `@{me.username}`\n"
            f"• الأيدي (ID): `{me.id}`\n"
            f"• المطور: `@{ADMIN_USERNAME}` ⚡️"
        )

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
        await m.edit_text(f"🔥 **تم تنظيف وحذف ({deleted}) من رسائلك بنجاح!** 💯")
        await asyncio.sleep(3)
        await m.delete()

    @user_app.on_message(filters.me & filters.text)
    async def fonts_handler(c, m):
        txt = m.text.strip()
        if txt in FONTS_MAP:
            current_font_style[0] = txt
            now = datetime.now(BAGHDAD_TZ).strftime("%I:%M")
            clock_text = format_time_with_font(now, txt)
            try:
                await user_app.update_profile(last_name=f"{clock_text}")
                await m.edit_text(f"🟢 **تم تغيير الخط إلى ({txt}) وضبط الساعة بنجاح: ({clock_text})**")
            except:
                pass

    try:
        await user_app.start()
        asyncio.create_task(update_clock())
        asyncio.create_task(monitor_expiration())
        user_active_sources[user_tg_id] = {"app": user_app, "session": client_session_name}
        print(f"✅ تم تشغيل سورس المستخدم بكافة الأوامر بنجاح: {client_session_name}")
    except Exception as e:
        print(f"❌ فشل تشغيل سورس المستخدم: {e}")


# ==================== بوت التنصيب (رئيسي) ====================

@bot_app.on_message(filters.command("code") & filters.private)
async def create_subscription_code(client, message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply_text("⛔️ هذا الأمر خاص بالمطور فقط!")
    args = message.text.split()
    if len(args) < 3:
        return await message.reply_text("⚠️ **خطأ بالاستخدام!**\nاكتب بالشكل التالي:\n`/code [الكود] [عدد الأيام]`\nمثال: `/code PRO2026 7`")
    code_text, days = args[1], int(args[2])
    active_subscriptions[code_text] = {"days": days, "used": False}
    db["subscriptions"] = active_subscriptions
    save_database(db)
    await message.reply_text(f"✅ **تم إنشاء وحفظ كود الاشتراك بنجاح!**\n\n• الكود: `{code_text}`\n• المدة: `{days} أيام`")

@bot_app.on_message(filters.command("addch") & filters.private)
async def set_forced_channel(client, message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply_text("⛔️ هذا الأمر خاص بالمطور فقط!")
    args = message.text.split()
    global forced_channel
    if len(args) < 2:
        if forced_channel:
            await message.reply_text(f"ℹ️ قناة الاشتراك الإجباري الحالية: `{forced_channel}`\n\nلإلغائها أرسل: `/delch` أو لتغييرها أرسل `/addch [المعرف]`")
        else:
            await message.reply_text("⚠️ **استخدم الأمر هكذا:**\n`/addch @ChannelUsername`")
        return
    
    forced_channel = args[1].strip()
    db["forced_channel"] = forced_channel
    save_database(db)
    await message.reply_text(f"✅ **تم تحديد قناة الاشتراك الإجباري بنجاح:**\n`{forced_channel}`")

@bot_app.on_message(filters.command("delch") & filters.private)
async def remove_forced_channel(client, message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply_text("⛔️ هذا الأمر خاص بالمطور فقط!")
    global forced_channel
    forced_channel = None
    db["forced_channel"] = None
    save_database(db)
    await message.reply_text("✅ **تم إلغاء وتعطيل قناة الاشتراك الإجباري بنجاح!**")

async def check_subscription(client, user_id):
    if user_id == ADMIN_ID:
        return True
    if not forced_channel:
        return True
    try:
        member = await client.get_chat_member(forced_channel, user_id)
        if member.status in [
            ChatMemberStatus.OWNER, 
            ChatMemberStatus.ADMINISTRATOR, 
            ChatMemberStatus.MEMBER
        ]:
            return True
    except UserNotParticipant:
        return False
    except Exception as e:
        print(f"خطأ في التحقق من الاشتراك للقناة {forced_channel}: {e}")
        return False  
    return False

@bot_app.on_message(filters.command("start") & filters.private)
async def start_bot(client, message):
    user_id = message.from_user.id
    
    if forced_channel:
        is_subbed = await check_subscription(client, user_id)
        if not is_subbed:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 اضغط هنا للاشتراك بالقناة", url=f"https://t.me/{forced_channel.replace('@', '')}")],
                [InlineKeyboardButton("🔄 اضغط هنا بعد الاشتراك", callback_data="check_sub")]
            ])
            await message.reply_text(
                "⚠️ **عذراً، يجب عليك الاشتراك في قناة البوت أولاً لتمكين الاستخدام!**\n\n"
                f"• القناة: `{forced_channel}`\n\n"
                "اشتَرِك بالقناة ثم اضغط على زر التحقق أدناه 👇",
                reply_markup=keyboard
            )
            return

    temp_users[user_id] = {"step": "waiting_code"}
    await message.reply_text(
        f"👋 أهلاً بك عزيزي في بوت تنصيب **سورس الربيعي برو** ⚡️\n\n"
        f"🔑 **الخطوة الأولى:**\nيرجى إرسال **كود الاشتراك** الخاص بك لتفعيل التنصيب:\n\n"
        f"[ المطور: @{ADMIN_USERNAME} ]"
    )

@bot_app.on_callback_query(filters.regex("check_sub"))
async def check_sub_callback(client, callback_query):
    user_id = callback_query.from_user.id
    is_subbed = await check_subscription(client, user_id)
    if is_subbed:
        await callback_query.message.delete()
        temp_users[user_id] = {"step": "waiting_code"}
        await callback_query.message.reply_text(
            f"✅ **شكراً لاشتراكك في القناة!**\n\n"
            f"👋 أهلاً بك عزيزي في بوت تنصيب **سورس الربيعي برو** ⚡️\n\n"
            f"🔑 **الخطوة الأولى:**\nيرجى إرسال **كود الاشتراك** الخاص بك لتفعيل التنصيب:\n\n"
            f"[ المطور: @{ADMIN_USERNAME} ]"
        )
    else:
        await callback_query.answer("❌ عذراً, أنت لم تشترك في القناة بعد أو لم يتم التحقق بنجاح! يرجى التأكد من الاشتراك أولاً.", show_alert=True)

@bot_app.on_message(filters.private & ~filters.command("start") & ~filters.command("code") & ~filters.command("addch") & ~filters.command("delch"))
async def handle_user_input(client, message):
    user_id = message.from_user.id
    
    if forced_channel and user_id not in temp_users and str(user_id) not in user_sessions:
        is_subbed = await check_subscription(client, user_id)
        if not is_subbed:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 اضغط هنا للاشتراك بالقناة", url=f"https://t.me/{forced_channel.replace('@', '')}")],
                [InlineKeyboardButton("🔄 اضغط هنا بعد الاشتراك", callback_data="check_sub")]
            ])
            await message.reply_text(
                "⚠️ **يجب عليك الاشتراك في قناة البوت أولاً!**\n\nاشترك بالقناة ثم اضغط التحقق:",
                reply_markup=keyboard
            )
            return

    if user_id not in temp_users:
        return await message.reply_text("أرسل /start للبدء من جديد.")
    
    user_data = temp_users[user_id]
    step = user_data.get("step")

    if step == "waiting_code":
        code = message.text.strip()
        if code not in active_subscriptions:
            return await message.reply_text("❌ **الكود غير صحيح!** تأكد من الكود وأرسله مرة أخرى:")
        
        sub_info = active_subscriptions[code]
        if sub_info["used"]:
            return await message.reply_text("⚠️ **هذا الكود تم استخدامه مسبقاً ولا يمكن استخدامه مرة أخرى!**")
        
        user_data["days"] = sub_info["days"]
        sub_info["used"] = True
        
        db["subscriptions"] = active_subscriptions
        save_database(db)
        
        user_data["step"] = "waiting_phone"
        await message.reply_text(f"✅ **تم قبول الكود بنجاح! (اشتراك لمدة {sub_info['days']} أيام)**\n\n📱 **الخطوة الثانية:**\nالآن أرسل رقم هاتفك مع رمز الدولة (مثال:\n`+9647700000000`):")

    elif step == "waiting_phone":
        phone_number = message.text.strip()
        session_name = f"rubaie_session_{user_id}"
        user_client = Client(session_name, api_id=API_ID, api_hash=API_HASH)
        await user_client.connect()
        try:
            sent_code = await user_client.send_code(phone_number)
            user_data.update({"client": user_client, "phone": phone_number, "phone_code_hash": sent_code.phone_code_hash, "step": "waiting_tg_code"})
            await message.reply_text("🔄 **جاري الاتصال بتليجرام وإرسال كود التحقق...**\n\n✉️ تم إرسال كود التحقق إلى حسابك في تليجرام.\n\nأرسل الكود الآن:")
        except Exception as e:
            await user_client.disconnect()
            del temp_users[user_id]
            await message.reply_text(f"❌ حدث خطأ: `{e}`\nأرسل /start وابدأ من جديد.")

    elif step == "waiting_tg_code":
        code = message.text.strip().replace(" ", "")
        try:
            await user_data["client"].sign_in(user_data["phone"], user_data["phone_code_hash"], code)
            await finalize_success(message, user_data["client"], user_data)
        except SessionPasswordNeeded:
            user_data["step"] = "waiting_password"
            await message.reply_text("🔒 **الحساب محمي بكلمة مرور (التحقق بخطوتين).**\n\nأرسل كلمة المرور الخاصة بحسابك الآن:")
        except PhoneCodeInvalid:
            await message.reply_text("❌ **الكود غير صحيح!** أرسل الكود الصحيح مرة أخرى:")
        except Exception as e:
            await message.reply_text(f"❌ خطأ: `{e}`\nأرسل /start وابدأ من جديد.")
            try: await user_data["client"].disconnect()
            except: pass
            del temp_users[user_id]

    elif step == "waiting_password":
        try:
            await user_data["client"].check_password(message.text.strip())
            await finalize_success(message, user_data["client"], user_data)
        except Exception as e:
            await message.reply_text(f"❌ كلمة المرور غير صحيحة أو حدث خطأ: `{e}`\nأرسل /start وابدأ من جديد.")
            try: await user_data["client"].disconnect()
            except: pass
            del temp_users[user_id]

async def finalize_success(message, user_client, user_data):
    await message.reply_text("🎉 **تم تسجيل الدخول وحفظ الجلسة بنجاح!**\n\n🚀 **جاري تشغيل سورس الربيعي بكافة الأوامر على حسابك الآن...**")
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
    await message.reply_text(f"✅ **تم تنصيب وتشغيل سورس الربيعي بنجاح!**\n⏳ اشتراكك فعال لمدة `{days_count} أيام`.\n\nتستطيع الآن استخدام الأوامر مثل `.الاوامر` أو `.م` في أي محادثة.\n[ المطور: @{ADMIN_USERNAME} ]")

async def restore_saved_sessions():
    current_time = time.time()
    for uid_str, data in list(user_sessions.items()):
        if current_time < data["expire_time"]:
            asyncio.create_task(start_user_source(data["session_name"], data["expire_time"], int(uid_str)))
            print(f"🔄 تمت استعادة وتفعيل سورس المستخدم: {uid_str}")
        else:
            del user_sessions[uid_str]
    db["user_sessions"] = user_sessions
    save_database(db)

async def main():
    print(f"🚀 [بوت صانع سورسات الربيعي المتكامل للمطور @{ADMIN_USERNAME}] يعمل الآن...")
    await restore_saved_sessions()
    await bot_app.start()
    print("✅ تم بدء تشغيل بوت التنصيب بنجاح ويستمع للأوامر الآن.")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 تم إيقاف البوت يدويياً.")
