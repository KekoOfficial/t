import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram_bot.downloader import descargar_audio, descargar_video, obtener_metadata
from telegram_bot.cola import agregar_a_cola, quitar_de_cola, estado_cola

# ---------------- CONFIG ----------------
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise Exception("❌ Debes definir tu TOKEN en las variables de entorno")
ADMIN_ID = 8295382991  # Tu user_id de Telegram
FRAGMENTOS = 10  # Para descargar más rápido

# ---------------- BOTONES ----------------
def botones():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎵 MP3", callback_data="mp3"),
         InlineKeyboardButton("🎬 MP4", callback_data="mp4")],
        [InlineKeyboardButton("🔼 Actualizar Bot", callback_data="actualizar")]
    ])

# ---------------- COMANDO /START ----------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💀 KHASAM BOT SYSTEM\n\n"
        "Envía un link:\n"
        "🎵 MP3\n🎬 MP4\n\n"
        "🔼 Sistema modular activo",
        reply_markup=botones()
    )

# ---------------- HANDLER BOTONES ----------------
async def botones_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    url = context.user_data.get("link")

    # BOTÓN ACTUALIZAR
    if query.data == "actualizar":
        if user_id != ADMIN_ID:
            await query.edit_message_text("❌ Solo el admin puede actualizar el bot")
            return
        await query.edit_message_text("🔼 Actualizando bot desde Git...")
        try:
            result = os.popen("git pull").read()
            await query.edit_message_text(f"✅ Actualización completa:\n<pre>{result}</pre>", parse_mode="HTML")
        except Exception as e:
            await query.edit_message_text(f"❌ Error al actualizar:\n{e}")
        return

    # BOTONES MP3 / MP4
    if not url:
        await query.edit_message_text("❌ No hay link guardado para descargar")
        return

    # Agregar a la cola
    pos = agregar_a_cola(user_id, url)
    await query.edit_message_text(f"💜 Añadido a la cola\n📊 Posición: {pos}\n⏱ Tiempo estimado: calculando...")

    # Descargar según el botón
    try:
        title = obtener_metadata(url)
        if query.data == "mp3":
            audio_path, thumb = await descargar_audio(user_id, url, query)
            await query.message.reply_audio(
                audio=open(audio_path, "rb"),
                title=title,
                thumbnail=open(thumb, "rb") if thumb else None
            )
        else:
            video_path = await descargar_video(user_id, url, query)
            await query.message.reply_video(video=open(video_path, "rb"), caption=title)
    except Exception as e:
        await query.message.reply_text(f"❌ Error en descarga: {e}")
    finally:
        quitar_de_cola(user_id)
        # Borrar archivos temporales
        for f in [f"downloads/audio/{user_id}.mp3", f"downloads/audio/{user_id}.png",
                  f"downloads/video/{user_id}.mp4"]:
            if os.path.exists(f):
                os.remove(f)
        await query.message.reply_text("✅ Descarga completa 💜")

# ---------------- HANDLER MENSAJES ----------------
async def registrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    # Detectar links
    if msg.text and "http" in msg.text:
        context.user_data['link'] = msg.text
        await msg.reply_text("🔥 Link detectado, elige formato:", reply_markup=botones())
        return
    await msg.reply_text("💀 Envía un link válido para descargar MP3 o MP4")

# ---------------- INICIALIZAR BOT ----------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CallbackQueryHandler(botones_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar))
app.run_polling()