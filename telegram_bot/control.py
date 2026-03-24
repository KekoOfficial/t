# control.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def botones():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎵 MP3", callback_data="mp3"),
         InlineKeyboardButton("🎬 MP4", callback_data="mp4")]
    ])

async def start_command(update, context):
    await update.message.reply_text(
        "💀 KHASAM BOT Ultimate 24/7\n"
        "Envía links de YouTube/TikTok y elige MP3 o MP4.\n"
        "🎵 YouTube → MP3 con portada\n"
        "🎬 TikTok → MP4\n"
        "📝 Cola, progreso real y VIP!"
    )