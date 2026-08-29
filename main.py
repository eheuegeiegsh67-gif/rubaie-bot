import asyncio
from pyrogram import Client, filters, idle

BOT_TOKEN = "8648735860:AAHIXbAq8by99wYWb1ZpkkWtDguX-lghBkA"
API_ID = 38183563
API_HASH = "7d3d3b379c6840a72c983865c8d927d"

app = Client(
    "rubaie_test_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    print(f"تم استقبال أمر /start من المستخدم: {message.from_user.id}")
    await message.reply_text("هلا بيك يا غالي! البوت يشتغل بوضوح واستجابة تامة 🚀")

async def main():
    print("جاري تشغيل بوت التجربة...")
    await app.start()
    print("البوت متصل الآن بنجاح ويستمع للأوامر!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
