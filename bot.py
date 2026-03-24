import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram_bot.downloader import procesar_link, botones_handler

TOKEN = os.getenv("TOKEN")

async def start(update, context):
    await update.message.reply_text(
        "💀 KHASAM BOT Ultimate 24/7\n"
        "Envía links de YouTube/TikTok y elige MP3 o MP4.\n"
        "🎵 YouTube → MP3 con portada\n"
        "🎬 TikTok → MP4\n"
        "📝 Cola, progreso real y VIP!"
    )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_link))
app.add_handler(CallbackQueryHandler(botones_handler))
app.run_polling()