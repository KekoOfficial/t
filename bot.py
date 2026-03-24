from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram_bot.control import start_command, botones_handler, registrar
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise Exception("❌ Debes definir tu TOKEN en las variables de entorno")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CallbackQueryHandler(botones_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar))
app.run_polling()