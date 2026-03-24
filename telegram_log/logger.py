import os
import json
from datetime import datetime
from telegram_bot.downloader import procesar_link

LOG_PATH = "telegram_log/logs"
os.makedirs(LOG_PATH, exist_ok=True)

def guardar(tipo, msg, contenido):
    archivo = f"{LOG_PATH}/{tipo}.json"

    if not os.path.exists(archivo):
        with open(archivo, "w") as f:
            json.dump([], f)

    with open(archivo, "r") as f:
        data = json.load(f)

    data.append({
        "user": msg.from_user.username,
        "contenido": contenido,
        "fecha": str(datetime.now())
    })

    with open(archivo, "w") as f:
        json.dump(data, f, indent=2)

async def registrar(update, context):
    msg = update.message

    if msg.text and "http" in msg.text:
        await procesar_link(update, context)
        guardar("links", msg, msg.text)
        return

    tipo = "otros"
    contenido = "media"

    if msg.text:
        tipo = "texto"
        contenido = msg.text

    guardar(tipo, msg, contenido)