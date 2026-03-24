from dotenv import load_dotenv
import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from fron import start_command, botones_handler, registrar

# ---------------- CONFIG ----------------
load_dotenv()
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise Exception("❌ Debes definir tu TOKEN en las variables de entorno")

# ---------------- INICIALIZAR BOT ----------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CallbackQueryHandler(botones_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar))

print("💀 KHASAM BOT ACTIVADO")
app.run_polling()