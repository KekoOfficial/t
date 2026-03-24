from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
import os
import subprocess

# ID del admin (tú)
ADMIN_ID = 8295382991  # <- reemplaza con tu user_id de Telegram

# ----------------- Botones -----------------
def botones():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 MP3", callback_data="mp3"),
            InlineKeyboardButton("🎬 MP4", callback_data="mp4")
        ],
        [
            InlineKeyboardButton("⚡ Actualizar Bot", callback_data="actualizar")
        ]
    ])

# ----------------- Comando /start -----------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💀 KHASAM BOT SYSTEM\n\n"
        "Envía un link:\n"
        "🎵 MP3\n🎬 MP4\n\n"
        "⚡ Sistema modular activo",
        reply_markup=botones()
    )

# ----------------- Handler del botón Actualizar -----------------
async def botones_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Solo admin puede actualizar
    if query.data == "actualizar":
        if user_id != ADMIN_ID:
            await query.edit_message_text("❌ Solo el admin puede actualizar el bot")
            return

        await query.edit_message_text("⚡ Actualizando bot desde Git...")
        try:
            # Ejecutar git pull desde Termux
            result = subprocess.run(
                ["git", "pull"],
                capture_output=True, text=True, shell=True
            )
            salida = result.stdout + "\n" + result.stderr
            await query.edit_message_text(f"✅ Actualización completa:\n<pre>{salida}</pre>", parse_mode="HTML")
        except Exception as e:
            await query.edit_message_text(f"❌ Error al actualizar:\n{e}")

    else:
        # Aquí puedes manejar otros botones como mp3/mp4
        await query.edit_message_text(f"Botón presionado: {query.data}")