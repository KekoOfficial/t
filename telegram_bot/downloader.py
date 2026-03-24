import subprocess
import os
import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def botones():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 MP3", callback_data="mp3"),
            InlineKeyboardButton("🎬 MP4", callback_data="mp4")
        ]
    ])

def descargar_mp3(url):
    subprocess.run(
        f'yt-dlp -x --audio-format mp3 --embed-thumbnail --convert-thumbnails png -o "downloads/audio/audio.%(ext)s" "{url}"',
        shell=True
    )
    return "downloads/audio/audio.mp3"

def descargar_mp4(url):
    subprocess.run(
        f'yt-dlp -f mp4 -o "downloads/video/video.mp4" "{url}"',
        shell=True
    )
    return "downloads/video/video.mp4"

def obtener_metadata(url):
    try:
        result = subprocess.run(f'yt-dlp -j "{url}"', shell=True, capture_output=True, text=True)
        meta = json.loads(result.stdout)
        return meta.get("title", "KHASAM")
    except:
        return "KHASAM"

# -------- HANDLERS --------

async def procesar_link(update, context):
    url = update.message.text
    context.user_data['link'] = url

    await update.message.reply_text("🔥 Elige formato:", reply_markup=botones())

async def botones_handler(update, context):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("link")
    if not url:
        await query.edit_message_text("❌ No hay link")
        return

    await query.edit_message_text("⏳ Descargando...")

    title = obtener_metadata(url)

    if query.data == "mp3":
        archivo = descargar_mp3(url)
        thumb = "downloads/audio/audio.png"

        await query.message.reply_audio(
            audio=open(archivo, "rb"),
            title=title,
            thumbnail=open(thumb, "rb") if os.path.exists(thumb) else None
        )

    else:
        archivo = descargar_mp4(url)

        await query.message.reply_video(
            video=open(archivo, "rb"),
            caption=title
        )

    if os.path.exists(archivo):
        os.remove(archivo)

    await query.message.reply_text("✅ Descarga completa 💀")