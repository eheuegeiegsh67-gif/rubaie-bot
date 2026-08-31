import asyncio
import datetime
from datetime import datetime, timezone, timedelta
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeNumberInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.raw import functions

# ==================== الإعدادات الأساسية ====================
API_ID = 3818356
API_HASH = "7d3d3b9379c6840a72c983865c8d927d"
BOT_TOKEN = "8648735860:AAHIXbAq8by99wYWb1ZpkkWtDguX-lghBkA"
OWNER_ID = 7989509412
OWNER_USERNAME = "Al_Rubaie15"

# تحديد التوقيت المحلي لمدينة بغداد (العراق)
Baghdad_TZ = timezone(timedelta(hours=3))

# تهيئة البوت
app = Client(
    "rubaie_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command(["start", "help"]) & filters.private)
async def start_command(client, message):
    user_name = message.from_user.first_name
    await message.reply_text(
        f"أهلاً بك يا {user_name} في سورس الربيعي المتكامل 🛠\n"
        f"المطور: @{OWNER_USERNAME}\n\n"
        "البوت يعمل الآن بكامل الكفاءة وجاهز لتلقي الأوامر."
    )

# أمر صنع الكروبات التلقائي
@app.on_message(filters.command(["create_groups", "صنع_كروبات"]) & filters.private)
async def create_groups_handler(client, message):
    try:
        # تحديد العدد (افتراضياً 50 أو حسب طلب المستخدم)
        args = message.text.split()
        count = int(args[1]) if len(args) > 1 and args[1].isdigit() else 50
        
        status_msg = await message.reply_text(f"جاري إنشاء {count} مجموعة والانسحاب منها تلقائياً...")
        
        created = 0
        for i in range(1, count + 1):
            try:
                # إنشاء الكروب
                group_title = f"كروب مؤقت #{i}"
                chat = await client.create_supergroup(group_title)
                
                # الحصول على رابط الدعوة
                invite_link = await client.export_chat_invite_link(chat.id)
                
                # إرسال الرابط للمستخدم
                await message.reply_text(f"تم إنشاء: {group_title}\nالرابط: {invite_link}")
                
                # مغادرة الكروب فوراً
                await client.leave_chat(chat.id)
                created += 1
                await asyncio.sleep(1)
            except Exception as e:
                continue
                
        await status_msg.edit_text(f"تم الانتهاء بنجاح! تم إنشاء ومغادرة {created} كروب.")
    except Exception as e:
        await message.reply_text(fحدث خطأ أثناء التنفيذ: `{e}`)

if __name__ == "__main__":
    print(f"🚀 [سورس الربيعي المتكامل للمطور @{OWNER_USERNAME}] يعمل الآن...")
    app.run()
