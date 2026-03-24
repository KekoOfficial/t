# bot.py
import os
import asyncio
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram import Update
from telegram.ext import ContextTypes

# ---------------- CARGAR VARIABLES DE ENTORNO ----------------
load_dotenv()
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise Exception("❌ Debes definir tu TOKEN en las variables de entorno (.env)")

# ---------------- IMPORTAR MÓDULOS DEL BOT ----------------
from telegram_bot.control import start_command, botones
from telegram_bot.downloader import descargar_audio, descargar_video, obtener_metadata
from telegram_bot.cola import agregar_a_cola, quitar_de_cola, estado_cola, ver_cola, en_proceso

# ---------------- HANDLER: Procesar link ----------------
async def procesar_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detecta links y muestra botones MP3/MP4"""
    url = update.message.text
    context.user_data['link'] = url
    await update.message.reply_text("💜 Elige formato:", reply_markup=botones())

# ---------------- HANDLER: Botones ----------------
async def botones_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestiona la elección de MP3/MP4 y añade a la cola"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    username = query.from_user.username or "User"
    url = context.user_data.get("link")

    if not url:
        await query.edit_message_text("❌ No hay link")
        return

    formato = query.data
    # Agregar a la cola y obtener posición
    posicion = agregar_a_cola(user_id, username, query, url, formato)

    await query.edit_message_text(
        f"💜 Añadido a la cola\n"
        f"📊 Posición: {posicion}\n"
        f"⏱ Tiempo estimado: {posicion*15}s\n\n"
        f"🧾 Cola actual:\n{ver_cola()}"
    )

    # Procesar cola si no hay descargas en curso
    await procesar_cola(context)

# ---------------- FUNCION: Procesar cola ----------------
async def procesar_cola(context: ContextTypes.DEFAULT_TYPE):
    """Procesa la cola de usuarios y descarga los archivos"""
    global en_proceso
    if en_proceso or not estado_cola:
        return

    en_proceso = True
    query, formato, user_id, username, url = quitar_de_cola()
    msg = await query.message.reply_text("💜 Iniciando descarga...")
    title = obtener_metadata(url)

    try:
        if formato == "mp3":
            ruta, thumb = await descargar_audio(user_id, url, msg)
            await query.message.reply_audio(
                audio=open(ruta, "rb"),
                title=title,
                thumbnail=open(thumb, "rb") if os.path.exists(thumb) else None
            )
        else:
            ruta = await descargar_video(user_id, url, msg)
            await query.message.reply_video(
                video=open(ruta, "rb"),
                caption=title
            )

        # Eliminar archivos temporales
        if os.path.exists(ruta):
            os.remove(ruta)
        if formato == "mp3" and os.path.exists(thumb):
            os.remove(thumb)

    except Exception as e:
        await query.message.reply_text(f"❌ Error en descarga: {e}")

    await query.message.reply_text("✅ Descarga completa 💜")
    en_proceso = False

    # Continuar con siguiente usuario si hay más en cola
    if estado_cola:
        await procesar_cola(context)

# ---------------- INICIALIZAR BOT ----------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_link))
app.add_handler(CallbackQueryHandler(botones_handler))

print("💀 KHASAM BOT corriendo...")
app.run_polling()