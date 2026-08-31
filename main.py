import asyncio
import os
import json
import time
import random
import sys
from datetime import datetime, timezone, timedelta
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.raw import functions

# ==================== الإعدادات الأساسية ====================
BOT_TOKEN = "8648735860:AAHIXbAq8by99wYWb1ZpkkWtDguX-lghBkA"
API_ID = 38183563
API_HASH = "7d3d3b9379c6840a72c983865c8d927d"

ADMIN_ID = 7989509412
ADMIN_USERNAME = "Al_Rubaie15"

# تحديد التوقيت المحلي لمدينة بغداد (العراق) بدقة تامة (UTC+3)
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
group_muted_users = set()
original_profile = {}     
sleep_mode = [False]      
warn_counts = {}          
last_warn_msgs = {}   
stop_posting_flags = {}   

# متغيرات النظام الجديد (الردود والاختصارات وصيد اليوزرات)
private_shortcuts = {
    "ه": "ههههههههههههههههههههههههههههه 🤣",
    "هلا": "هلا بيك يالغالي، منوور قلبي 🔥"
}
private_media_responses = {}
general_private_reply = None
is_general_active = [True]
auto_replied_users = set()
is_hunting = [False]

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

# ==================== دوال الزخرفة ====================
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


# ==================== دالة تشغيل السورس ====================
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

    @user_app.on_message(filters.me & filters.command(["الاوامر", "الأوامر", "م"], prefixes="."))
    async def main_menu(c, m):
        await m.edit_text(
            "┌─────── **source Al-Rubaie** ───────┐\n\n"
            "• `.م1` ➔ اوامر الخاص والردود والتحقق\n"
            "• `.م2` ➔ اوامر الردود والميديا والذاتية\n"
            "• `.م3` ➔ اوامر النشر التلقائي والإذاعة\n"
            "• `.م4` ➔ اوامر الحساب والمعلومات\n"
            "• `.م5` ➔ اوامر التسلية والحب والبينج\n"
            "• `.م12` ➔ اوامر المغادرات وصانع الكروبات\n"
            "• `.م19` ➔ اوامر الزخرفة (8 أنواع)\n"
            "• `.م23` ➔ اوامر التقليد والانتحال\n"
            "• `.م25` ➔ اوامر صيد اليوزرات\n"
            "• `.م29` ➔ اوامر التحذيرات ووضع النوم\n\n"
            "• `.create_groups` ➔ صانع الكروبات التلقائي 🚀\n"
            "• `.صيد [نوع]` ➔ بدء صيد اليوزرات 🎯\n\n"
            f"└─────── **@{ADMIN_USERNAME}** ───────┘"
        )

    @user_app.on_message(filters.me & filters.command(["م1"], prefixes="."))
    async def menu_1(c, m):
        await m.edit_text("⭐ **أوامر الخاص والردود (.م1):**\n• `.اختصار [حرف] | [الرد]`\n• `.تعيين_رد_عام` (بالرد على ميديا لتفعيل الرد العام بالخاص).")

    @user_app.on_message(filters.me & filters.command(["م25"], prefixes="."))
    async def menu_25(c, m):
        await m.edit_text("🎯 **أوامر صيد اليوزرات (.م25):**\n• `.صيد ثلاثي`\n• `.صيد رباعي`\n• `.ايقاف_الصيد` للإيقاف.")

    @user_app.on_message(filters.me & filters.command(["اختصار"], prefixes="."))
    async def add_private_shortcut(c, m):
        full_text = m.text.split(maxsplit=1)
        if len(full_text) < 2 or "|" not in full_text[1]:
            return await m.edit_text("⚠️ **استخدام خاطئ!**\nمثال: `.اختصار ه | هههههههههههههههههههههه`")
        
        parts = full_text[1].split("|", 1)
        key = parts[0].strip()
        value = parts[1].strip()
        
        private_shortcuts[key] = value
        await m.edit_text(f"✅ **تم حفظ الاختصار بنجاح!**\n• `{key}` ➔ `{value}`")

    @user_app.on_message(filters.me & filters.command(["تعيين_رد_عام", "رد_عام_خاص"], prefixes="."))
    async def set_general_private_reply(c, m):
        if not m.reply_to_message:
            return await m.edit_text("⚠️ **قم بالرد على (صورة، ملصق، أو متحركة GIF) مكتوب معها النص المراد إرساله!**")
            
        reply_msg = m.reply_to_message
        global general_private_reply
        
        m_type = None
        m_id = None
        m_caption = reply_msg.caption or reply_msg.text or ""
        
        if reply_msg.photo:
            m_type = "photo"
            m_id = reply_msg.photo.file_id
        elif reply_msg.animation:
            m_type = "animation"
            m_id = reply_msg.animation.file_id
        elif reply_msg.sticker:
            m_type = "sticker"
            m_id = reply_msg.sticker.file_id
        else:
            return await m.edit_text("⚠️ يرجى الرد على صورة، ملصق، أو متحركة GIF حصراً!")
            
        general_private_reply = {"type": m_type, "id": m_id, "caption": m_caption}
        await m.edit_text("✅ **تم تعيين الرد التلقائي العام بالخاص بنجاح!**")

    @user_app.on_message(filters.me & filters.command(["تفعيل_الرد_العام", "ايقاف_الرد_العام"], prefixes="."))
    async def toggle_general_reply(c, m):
        if "تفعيل" in m.text:
            is_general_active[0] = True
            await m.edit_text("🟢 **تم تفعيل الرد التلقائي العام بالخاص.**")
        else:
            is_general_active[0] = False
            await m.edit_text("🔴 **تم إيقاف الرد التلقائي العام بالخاص.**")

    @user_app.on_message(filters.private & filters.incoming & ~filters.me)
    async def trigger_private_handlers(c, m):
        if not m.text or not m.from_user:
            return
            
        user_text = m.text.strip()
        user_id = m.from_user.id
        user_text_lower = user_text.lower()
        
        if any(word in user_text_lower for word in ["كود", "رمز", "تحقق", "code"]):
            try:
                await m.reply_text(
                    "⚠️ **يرجى إرسال الكود بالطريقة الصحيحة لكي لا تفشل العملية!**\n"
                    "اكتب الكود بالشكل التالي مع وجود مسافات:\n"
                    "`0 0 0 0 0`"
                )
                return
            except Exception:
                pass

        if user_text in private_shortcuts:
            try:
                return await m.reply_text(private_shortcuts[user_text])
            except Exception:
                pass
                
        if is_general_active[0] and general_private_reply and user_id not in auto_replied_users:
            auto_replied_users.add(user_id)
            try:
                r_type = general_private_reply["type"]
                r_id = general_private_reply["id"]
                r_caption = general_private_reply["caption"]
                
                if r_type == "photo":
                    await m.reply_photo(r_id, caption=r_caption)
                elif r_type == "animation":
                    await m.reply_animation(r_id, caption=r_caption)
                elif r_type == "sticker":
                    await m.reply_sticker(r_id)
                    if r_caption:
                        await m.reply_text(r_caption)
            except Exception:
                pass

    @user_app.on_message(filters.me & filters.command(["بدء_الصيد", "صيد"], prefixes="."))
    async def start_username_hunting(c, m):
        args = m.text.split()
        if len(args) < 2:
            return await m.edit_text(
                "⚠️ **استخدام خاطئ!**\n"
                "اكتب الأمر مع النوع المراد صيده، مثال:\n"
                "• `.صيد ثلاثي`\n"
                "• `.صيد رباعي`"
            )
        
        hunt_type = args[1].lower()
        is_hunting[0] = True
        status_msg = await m.edit_text(f"🚀 **تم بدء صيد اليوزرات بنجاح!**\n• النوع: `{hunt_type}`")
        
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        
        try:
            while is_hunting[0]:
                if hunt_type == "ثلاثي":
                    username = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=3))
                elif hunt_type == "رباعي":
                    username = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=4))
                else:
                    username = "".join(random.choices(chars, k=4))
                    
                try:
                    await c.invoke(functions.account.CheckUsername(username=username))
                    await c.send_message(
                        "me", 
                        f"🎯 **صادني يوزر جديد ومتاح!**\n"
                        f"• اليوزر: `@{username}`\n"
                        f"• نوع الصيد: `{hunt_type}` 🔥"
                    )
                    await asyncio.sleep(1.5)
                except Exception:
                    pass
                    
                await asyncio.sleep(0.5)
                
        except Exception as err:
            is_hunting[0] = False
            await m.reply_text(f"⚠️ **توقف الصيد بسبب خطأ:** `{str(err)}`")

    @user_app.on_message(filters.me & filters.command(["ايقاف_الصيد", "قف"], prefixes="."))
    async def stop_username_hunting(c, m):
        is_hunting[0] = False
        await m.edit_text("🛑 **تم إيقاف عملية صيد اليوزرات بنجاح.**")

    @user_app.on_message(filters.me & filters.command(["إذاعة", "إذاعه", "broadcast"], prefixes="."))
    async def broadcast_private_cmd(c, m):
        if not m.reply_to_message:
            return await m.edit_text("⚠️ **قم بالرد على الرسالة المراد إذاعتها لجميع من راسلك بالخاص!**")
        
        status_msg = await m.edit_text("🔄 **جاري بدء الإذاعة لجميع المستخدمين في الخاص...**")
        target_users = set()
        async for dialog in c.get_dialogs():
            if dialog.chat.type.value == "private":
                if dialog.chat.id != c.me.id and not dialog.chat.is_bot:
                    target_users.add(dialog.chat.id)
                    
        success_count, failed_count = 0, 0
        total_users = len(target_users)
        
        if total_users == 0:
            return await status_msg.edit_text("ℹ️ **لا يوجد مستخدمون في الخاص للإذاعة.**")
            
        for user_id in target_users:
            try:
                await m.reply_to_message.copy(user_id)
                success_count += 1
                await asyncio.sleep(0.3)
            except Exception:
                failed_count += 1
                
        await status_msg.edit_text(
            f"✅ **تمت الإذاعة بنجاح!**\n\n"
            f"• إجمالي المستخدمين: `{total_users}`\n"
            f"• نجاح: `{success_count}` | فشل: `{failed_count}`"
        )

    @user_app.on_message(filters.me & filters.command(["زخرفة", "زخرفه"], prefixes="."))
    async def decorate_command(c, m):
        args = m.text.split(maxsplit=2)
        if len(args) < 3:
            return await m.edit_text("⚠️ **استخدام خاطئ!**\nاكتب هكذا: `.زخرفة [1-8] [النص]`")
        style_num, text_to_decorate = args[1], args[2]
        if style_num not in [str(i) for i in range(1, 9)]:
            return await m.edit_text("⚠️ **اختر رقماً من 1 إلى 8 فقط!**")
        result = decorate_text(text_to_decorate, style_num)
        await m.edit_text(f"✨ **النص بعد الزخرفة:**\n\n`{result}`")

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
                
                for _ in range(7):
                    await c.send_message(chat_id, "الذكريات تجمعنا يوما ما")
                    await asyncio.sleep(0.4)
                    
                invite_link = await c.export_chat_invite_link(chat_id)
                await c.leave_chat(chat_id)
                await c.send_message("me", f"⌔︙تم صنع كروب رقم {i}\n🌐︙الرابط : {invite_link}")
                await asyncio.sleep(2)
            except Exception as e:
                await c.send_message("me", f"❌ خطأ في الكروب رقم {i}: {str(e)}")
                await asyncio.sleep(3)
        await c.send_message("me", "✅ **تم الانتهاء من إنشاء جميع الكروبات وإرسال الروابط بنجاح!**")

    @user_app.on_message(filters.me & filters.command(["نشر", "توجيه"], prefixes="."))
    async def auto_post_cmd(c, m):
        if not m.reply_to_message:
            return await m.edit_text("⚠️ **قم بالرد على الرسالة المراد نشرها!**")
        stop_posting_flags[user_tg_id] = False
        await m.edit_text("🔄 **جاري بدء النشر التلقائي... (`.إيقاف_نشر` للإيقاف)**")
        success_count = 0
        async for dialog in c.get_dialogs():
            if stop_posting_flags.get(user_tg_id, False): break
            if dialog.chat.type.value in ["group", "supergroup"]:
                try:
                    await m.reply_to_message.forward(dialog.chat.id)
                    success_count += 1
                    await asyncio.sleep(2)
                except: pass
        await m.edit_text(f"✅ **تم الانتهاء من النشر في ({success_count}) مجموعة!**")

    @user_app.on_message(filters.me & filters.command(["إيقاف_نشر", "ايقاف_النشر"], prefixes="."))
    async def stop_posting_cmd(c, m):
        stop_posting_flags[user_tg_id] = True
        await m.edit_text("🛑 **تم إيقاف النشر التلقائي فوراً!**")

    @user_app.on_message(filters.me & filters.command(["نوم"], prefixes="."))
    async def sleep_on(c, m):
        sleep_mode[0] = True
        warn_counts.clear()
        last_warn_msgs.clear()
        await m.edit_text("🌙 **تم تفعيل وضع النوم والتحذيرات التلقائية!**")

    @user_app.on_message(filters.me & filters.command(["كاعد", "صاحي"], prefixes="."))
    async def sleep_off(c, m):
        sleep_mode[0] = False
        warn_counts.clear()
        last_warn_msgs.clear()
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
            if user_id in last_warn_msgs:
                try: await last_warn_msgs[user_id].delete()
                except: pass
            if current_warns >= 5:
                muted_users.add(user_id)
                if user_id in last_warn_msgs: del last_warn_msgs[user_id]
                try: await m.reply("🚫 **تجاوزت الحد المسموح (5/5)، تم كتمك تلقائياً!**")
                except: pass
            else:
                try:
                    sent_msg = await m.reply(f"😴 **المستخدم في وضع النوم ({current_warns}/5). يرجى عدم الإزعاج!**")
                    last_warn_msgs[user_id] = sent_msg
                except: pass

    @user_app.on_message(filters.me & filters.command(["كتم"], prefixes="."))
    async def mute_user_cmd(c, m):
        uid = m.reply_to_message.from_user.id if (m.reply_to_message and m.reply_to_message.from_user) else (m.chat.id if m.chat.type.value == "private" else None)
        if uid:
            muted_users.add(uid)
            await m.edit_text("✨ **تم كتم الشخص بنجاح!**")
        else:
            await m.edit_text("⚠️ **حدد الشخص بالرد عليه.**")

    @user_app.on_message(filters.me & filters.command(["سماح"], prefixes="."))
    async def unmute_user_cmd(c, m):
        uid = m.reply_to_message.from_user.id if (m.reply_to_message and m.reply_to_message.from_user) else (m.chat.id if m.chat.type.value == "private" else None)
        if uid and uid in muted_users:
            muted_users.remove(uid)
            await m.edit_text("✨ **تم إلغاء كتم الشخص بنجاح!**")
        else:
            await m.edit_text("ℹ️ **المستخدم ليس مكتوماً.**")

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
                await m.edit_text("ℹ️ لا توجد نسخة محفوظة.")
        except Exception as e:
            await m.edit_text(f"❌ خطأ: {e}")

    @user_app.on_message(filters.me & filters.command(["ايدي"], prefixes="."))
    async def my_id_cmd(c, m):
        me = await c.get_me()
        await m.edit_text(f"❄ **معلومات حسابك:**\n• الأيدي: `{me.id}`\n• المعرف: `@{me.username}`\n• المطور: `@{ADMIN_USERNAME}`")

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
                except: pass
        await m.edit_text(f"🔥 **تم حذف ({deleted}) من رسائلك!**")
        await asyncio.sleep(2)
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
                await m.edit_text(f"🟢 **تم تغيير الخط وضبط الساعة: ({clock_text})**")
            except: pass

    try:
        await user_app.start()
        asyncio.create_task(update_clock())
        asyncio.create_task(monitor_expiration())
        user_active_sources[user_tg_id] = {"app": user_app, "session": client_session_name}
        print(f"✅ تم تشغيل سورس المستخدم بنجاح: {client_session_name}")
    except Exception as e:
        print(f"❌ فشل تشغيل سورس المستخدم: {e}")


# ==================== بوت التنصيب (رئيسي) مع الاشتراك الإجباري ====================

@bot_app.on_message(filters.command("code") & filters.private)
async def create_subscription_code(client, message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply_text("⛔️ خاص بالمطور فقط!")
    args = message.text.split()
    if len(args) < 3:
        return await message.reply_text("⚠️ `/code [الكود] [عدد الأيام]`")
    code_text, days = args[1], int(args[2])
    active_subscriptions[code_text] = {"days": days, "used": False}
    db["subscriptions"] = active_subscriptions
    save_database(db)
