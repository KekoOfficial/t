from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from dotenv import load_dotenv
import os

from telegram_bot.downloader import procesar_link, botones_handler
from telegram_log.logger import registrar
from telegram_menu.menu import start

load_dotenv()
TOKEN = os.getenv("TOKEN")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, registrar))
    app.add_handler(CallbackQueryHandler(botones_handler))

    print("🔥 BOT CORE ACTIVO")
    app.run_polling()

if __name__ == "__main__":
    main()