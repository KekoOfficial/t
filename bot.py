# bot.py
import os
from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
)
from fron import start_command, botones_handler, registrar
from telegram_log.admin import ver_logs, limpiar_logs

# ---------------- CONFIG ----------------
load_dotenv()
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise Exception("❌ Debes definir tu TOKEN en las variables de entorno")

# ---------------- INICIALIZAR BOT ----------------
app = ApplicationBuilder().token(TOKEN).build()

# Handlers principales
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CallbackQueryHandler(botones_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar))

# Comandos de admin para logs
app.add_handler(CommandHandler("ver_logs", ver_logs))
app.add_handler(CommandHandler("limpiar_logs", limpiar_logs))

print("💀 KHASAM BOT ACTIVADO")
app.run_polling()