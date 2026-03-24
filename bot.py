import os
import json
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("TOKEN")
MI_CHAT_ID = int(os.getenv("MI_CHAT_ID"))

# Crear carpetas si no existen
os.makedirs("downloads/audio", exist_ok=True)
os.makedirs("downloads/video", exist_ok=True)
os.makedirs("logs", exist_ok=True)

LOG_FILE = "logs/mensajes.json"

# Guardar mensaje en log
def guardar_log(message):
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    logs.append({
        "chat_id": message.chat_id,
        "usuario": message.from_user.username,
        "tipo": message.effective_attachment.__class__.__name__ if message.effective_attachment else "Texto",
        "contenido": message.text if message.text else "Archivo/Sticker",
        "timestamp": str(datetime.now())
    })
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

# Barra de progreso simulada
async def progreso(update, archivo):
    msg = await update.message.reply_text("⏳ 0%")
    for p in ["10%", "30%", "50%", "70%", "90%", "100%"]:
        await msg.edit_text(f"⏳ Descargando {p}")
    return msg

# Procesar link
async def procesar_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    guardar_log(update.message)

    msg = await progreso(update, url)

    # Detectar tipo
    if "tiktok.com" in url:
        archivo = f"downloads/video/video.mp4"
        comando = f'yt-dlp -f mp4 --concurrent-fragments 10 -o "{archivo}" "{url}"'
    else:
        archivo = f"downloads/audio/audio.mp3"
        comando = f'yt-dlp -x --audio-format mp3 --embed-thumbnail --concurrent-fragments 10 -o "{archivo}" "{url}"'

    # Extraer metadata
    metadata_cmd = f'yt-dlp -j "{url}"'
    result = subprocess.run(metadata_cmd, shell=True, capture_output=True, text=True)
    try:
        meta = json.loads(result.stdout)
        title = meta.get("title", "KHASAM Download")
        thumbnail = meta.get("thumbnail")
    except:
        title = "KHASAM Download"
        thumbnail = None

    # Descargar
    subprocess.run(comando, shell=True)

    # Enviar al usuario original
    if archivo.endswith(".mp3"):
        await update.message.reply_audio(
            audio=open(archivo, "rb"),
            title=title,
            thumb=open(archivo, "rb") if thumbnail else None
        )
    else:
        await update.message.reply_video(video=open(archivo, "rb"), caption=title)

    os.remove(archivo)
    await update.message.reply_text("✅ Descarga completa 💀")

    # Enviar registro a ti
    registro = f"📌 Usuario: {update.message.from_user.username}\nTipo: Link\nContenido: {url}"
    await context.bot.send_message(chat_id=MI_CHAT_ID, text=registro)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💀 KHASAM BOT Ultimate\n"
        "Envía un link:\n"
        "🎵 YouTube → MP3 con portada\n"
        "🎬 TikTok → MP4\n"
        "⚡ Barra de descarga + máximo fragmento"
    )

# Inicializar bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL, procesar_link))

app.run_polling()