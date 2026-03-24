from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram_bot.downloader import descargar_audio, descargar_video, obtener_metadata
from telegram_bot.cola import agregar_a_cola, quitar_de_cola

ADMIN_ID = 8295382991  # tu user_id

def botones():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎵 MP3", callback_data="mp3"),
         InlineKeyboardButton("🎬 MP4", callback_data="mp4")],
        [InlineKeyboardButton("🔼 Actualizar Bot", callback_data="actualizar")]
    ])

async def start_command(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💀 KHASAM BOT SYSTEM\nEnvía un link:\n🎵 MP3\n🎬 MP4\n🔼 Sistema modular activo",
        reply_markup=botones()
    )

async def botones_handler(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    url = context.user_data.get("link")

    if query.data == "actualizar":
        if user_id != ADMIN_ID:
            await query.edit_message_text("❌ Solo el admin puede actualizar el bot")
            return
        await query.edit_message_text("🔼 Actualizando bot desde Git...")
        import os
        result = os.popen("git pull").read()
        await query.edit_message_text(f"✅ Actualización completa:\n<pre>{result}</pre>", parse_mode="HTML")
        return

    if not url:
        await query.edit_message_text("❌ No hay link guardado")
        return

    pos = agregar_a_cola(user_id, url)
    await query.edit_message_text(f"💜 Añadido a la cola\n📊 Posición: {pos}")

    try:
        title = obtener_metadata(url)
        if query.data == "mp3":
            audio_path, thumb = await descargar_audio(user_id, url, query)
            await query.message.reply_audio(audio=open(audio_path, "rb"), title=title, thumbnail=open(thumb, "rb") if thumb else None)
        else:
            video_path = await descargar_video(user_id, url, query)
            await query.message.reply_video(video=open(video_path, "rb"), caption=title)
    finally:
        from telegram_bot.cola import quitar_de_cola
        quitar_de_cola(user_id)