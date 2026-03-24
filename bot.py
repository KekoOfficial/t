import os import json import subprocess from datetime import datetime from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes from dotenv import load_dotenv

---------------- Cargar variables ----------------

load_dotenv() TOKEN = os.getenv("TOKEN") MI_CHAT_ID = int(os.getenv("MI_CHAT_ID"))

---------------- Crear carpetas -----------------

os.makedirs("downloads/audio", exist_ok=True) os.makedirs("downloads/video", exist_ok=True) os.makedirs("logs", exist_ok=True)

---------------- Logs ----------------

LOG_FILES = { "texto": "logs/texto.json", "foto": "logs/fotos.json", "video": "logs/videos.json", "sticker": "logs/stickers.json", "documento": "logs/documentos.json", "link": "logs/links.json" }

for f in LOG_FILES.values(): if not os.path.exists(f): with open(f, "w") as temp: json.dump([], temp)

---------------- Guardar logs ----------------

def guardar_log(tipo, message, contenido): archivo = LOG_FILES.get(tipo, LOG_FILES["texto"]) logs = [] if os.path.exists(archivo): with open(archivo, "r") as f: logs = json.load(f) logs.append({ "chat_id": message.chat_id, "usuario": message.from_user.username, "contenido": contenido, "timestamp": str(datetime.now()) }) with open(archivo, "w") as f: json.dump(logs, f, indent=2)

---------------- BOTONES ----------------

def botones(): return InlineKeyboardMarkup([ [ InlineKeyboardButton("🎵 MP3", callback_data="mp3"), InlineKeyboardButton("🎬 MP4", callback_data="mp4") ] ])

---------------- PROGRESO ----------------

async def progreso(msg): m = await msg.reply_text("⏳ 0%") for p in ["10%", "30%", "50%", "70%", "90%", "100%"]: await m.edit_text(f"⏳ Descargando {p}") return m

---------------- DESCARGAS ----------------

def descargar_mp3(url): archivo = "downloads/audio/audio.mp3" comando = f'yt-dlp -x --audio-format mp3 --embed-thumbnail --convert-thumbnails png -o "downloads/audio/audio.%(ext)s" "{url}"' subprocess.run(comando, shell=True) return archivo

def descargar_mp4(url): archivo = "downloads/video/video.mp4" comando = f'yt-dlp -f mp4 -o "{archivo}" "{url}"' subprocess.run(comando, shell=True) return archivo

---------------- METADATA ----------------

def obtener_metadata(url): try: result = subprocess.run(f'yt-dlp -j "{url}"', shell=True, capture_output=True, text=True) meta = json.loads(result.stdout) return meta.get("title", "KHASAM"), meta.get("thumbnail") except: return "KHASAM", None

---------------- LINK ----------------

async def procesar_link(update: Update, context: ContextTypes.DEFAULT_TYPE): msg = update.message url = msg.text

guardar_log("link", msg, url)
context.user_data['link'] = url

await msg.reply_text("🔥 Elige formato:", reply_markup=botones())

---------------- BOTON CLICK ----------------

async def botones_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.answer()

url = context.user_data.get('link')
if not url:
    await query.edit_message_text("❌ No hay link")
    return

await query.edit_message_text("⏳ Procesando...")

await progreso(query.message)

title, thumbnail = obtener_metadata(url)

if query.data == "mp3":
    archivo = descargar_mp3(url)
    thumb_path = "downloads/audio/audio.png"

    await query.message.reply_audio(
        audio=open(archivo, "rb"),
        title=title,
        thumbnail=open(thumb_path, "rb") if os.path.exists(thumb_path) else None
    )

elif query.data == "mp4":
    archivo = descargar_mp4(url)
    await query.message.reply_video(video=open(archivo, "rb"), caption=title)

if os.path.exists(archivo):
    os.remove(archivo)

await query.message.reply_text("✅ Descarga completa 💀")

---------------- REGISTRAR ----------------

async def registrar(update: Update, context: ContextTypes.DEFAULT_TYPE): msg = update.message

if msg.text and "http" in msg.text:
    await procesar_link(update, context)
    return

tipo = "Otro"
contenido = "Media"

if msg.text:
    tipo = "Texto"
    contenido = msg.text
elif msg.photo:
    tipo = "Foto"
    contenido = f"Foto {msg.photo[-1].width}x{msg.photo[-1].height}"
elif msg.video:
    tipo = "Video"
    contenido = f"Video {msg.video.duration}s"
elif msg.document:
    tipo = "Documento"
    contenido = msg.document.file_name
elif msg.sticker:
    tipo = "Sticker"
    contenido = msg.sticker.emoji

guardar_log(tipo, msg, contenido)

registro = f"📌 Usuario: {msg.from_user.username}\nTipo: {tipo}\nContenido: {contenido}"
await context.bot.send_message(chat_id=MI_CHAT_ID, text=registro)

---------------- START ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text( "💀 KHASAM BOT GOD MODE\n" "Envía link y elige:\n" "🎵 MP3\n🎬 MP4" )

---------------- MAIN ----------------

def main(): app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL, registrar))
app.add_handler(CallbackQueryHandler(botones_handler))

print("🔥 BOT ACTIVO")
app.run_polling()

if name == "main": main()