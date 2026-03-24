import os
import json
import subprocess
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# ---------------- Cargar variables ----------------
load_dotenv()
TOKEN = os.getenv("TOKEN")
MI_CHAT_ID = int(os.getenv("MI_CHAT_ID"))

# ---------------- Crear carpetas -----------------
os.makedirs("downloads/audio", exist_ok=True)
os.makedirs("downloads/video", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Archivos de log por tipo
LOG_FILES = {
    "texto": "logs/texto.json",
    "foto": "logs/fotos.json",
    "video": "logs/videos.json",
    "sticker": "logs/stickers.json",
    "documento": "logs/documentos.json",
    "link": "logs/links.json"
}

# Inicializar logs vacíos si no existen
for f in LOG_FILES.values():
    if not os.path.exists(f):
        with open(f, "w") as temp:
            json.dump([], temp)

# ---------------- Guardar logs -------------------
def guardar_log(tipo, message, contenido):
    archivo = LOG_FILES.get(tipo, LOG_FILES["texto"])
    logs = []
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            logs = json.load(f)
    logs.append({
        "chat_id": message.chat_id,
        "usuario": message.from_user.username,
        "contenido": contenido,
        "timestamp": str(datetime.now())
    })
    with open(archivo, "w") as f:
        json.dump(logs, f, indent=2)

# ---------------- Barra de progreso ----------------
async def progreso(update, archivo):
    msg = await update.message.reply_text("⏳ 0%")
    for p in ["10%", "30%", "50%", "70%", "90%", "100%"]:
        await msg.edit_text(f"⏳ Descargando {p}")
    return msg

# ---------------- Procesar links ------------------
async def procesar_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    url = msg.text
    guardar_log("link", msg, url)
    await update.message.reply_text("🔥 Detecté link, procesando...")

    # Barra de progreso simulada
    await progreso(update, url)

    if "tiktok.com" in url:
        archivo = f"downloads/video/video.mp4"
        comando = f'yt-dlp -f mp4 --concurrent-fragments 10 -o "{archivo}" "{url}"'
    else:
        archivo = f"downloads/audio/audio.mp3"
        comando = f'yt-dlp -x --audio-format mp3 --embed-thumbnail --concurrent-fragments 10 -o "{archivo}" "{url}"'

    # Metadata
    metadata_cmd = f'yt-dlp -j "{url}"'
    result = subprocess.run(metadata_cmd, shell=True, capture_output=True, text=True)
    try:
        meta = json.loads(result.stdout)
        title = meta.get("title", "KHASAM Download")
        thumbnail = meta.get("thumbnail")
    except:
        title = "KHASAM Download"
        thumbnail = None

    subprocess.run(comando, shell=True)

    # Enviar archivo
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
    registro = f"📌 Usuario: {msg.from_user.username}\nTipo: Link\nContenido: {url}"
    await context.bot.send_message(chat_id=MI_CHAT_ID, text=registro)

# ---------------- Registrar todo ------------------
async def registrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    # Detectar links primero
    if msg.text and "http" in msg.text:
        await procesar_link(update, context)
        return

    tipo = "Otro"
    contenido = "Archivo/Media"

    if msg.text:
        tipo = "Texto"
        contenido = msg.text
        guardar_log(tipo, msg, contenido)
    elif msg.photo:
        tipo = "Foto"
        contenido = f"Foto con {len(msg.photo)} resoluciones, mayor resolución: {msg.photo[-1].width}x{msg.photo[-1].height}"
        guardar_log(tipo, msg, contenido)
    elif msg.video:
        tipo = "Video"
        contenido = f"Video: {msg.video.file_name if msg.video.file_name else 'Sin nombre'}, duración {msg.video.duration}s, {msg.video.width}x{msg.video.height}"
        guardar_log(tipo, msg, contenido)
    elif msg.document:
        tipo = "Documento"
        contenido = f"Archivo: {msg.document.file_name}, tamaño {msg.document.file_size} bytes"
        guardar_log(tipo, msg, contenido)
    elif msg.sticker:
        tipo = "Sticker"
        contenido = f"Sticker: {msg.sticker.emoji} ({msg.sticker.set_name})"
        guardar_log(tipo, msg, contenido)

    # Enviar registro a ti
    registro = f"📌 Usuario: {msg.from_user.username} ({msg.from_user.id})\nTipo: {tipo}\nContenido: {contenido}"
    await context.bot.send_message(chat_id=MI_CHAT_ID, text=registro)

# ---------------- Comando /start -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💀 KHASAM BOT Ultimate 24/7\n"
        "Envía links de YouTube/TikTok o cualquier mensaje y se registrará.\n"
        "🎵 YouTube → MP3 con portada\n"
        "🎬 TikTok → MP4\n"
        "📝 Todos los mensajes se registran y se envían a Khasam"
    )

# ---------------- Inicializar bot ----------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL, registrar))
app.run_polling()