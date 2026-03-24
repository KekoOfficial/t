import os
import json
from datetime import datetime
import asyncio
from telegram_bot.downloader import procesar_link

# Carpeta de logs
LOG_PATH = "telegram_log/logs"
os.makedirs(LOG_PATH, exist_ok=True)

# Lock para evitar conflictos en async
lock = asyncio.Lock()

def obtener_archivo(tipo):
    """Genera un archivo de log diario según tipo de mensaje."""
    fecha_archivo = datetime.now().strftime("%Y-%m-%d")
    archivo = f"{LOG_PATH}/{tipo}_{fecha_archivo}.json"
    if not os.path.exists(archivo):
        with open(archivo, "w") as f:
            json.dump([], f)
    return archivo

async def guardar(tipo, msg, contenido):
    """Guarda la información del mensaje en el JSON correspondiente."""
    archivo = obtener_archivo(tipo)
    resumen = contenido if isinstance(contenido, str) else str(contenido)
    resumen = resumen[:50] + "..." if len(resumen) > 50 else resumen

    log_entry = {
        "user": getattr(msg.from_user, "username", "unknown"),
        "user_id": getattr(msg.from_user, "id", None),
        "chat_id": msg.chat.id,
        "chat_type": msg.chat.type,
        "message_id": msg.message_id,
        "contenido": resumen,
        "tipo_completo": tipo,
        "fecha": str(datetime.now())
    }

    async with lock:
        with open(archivo, "r") as f:
            data = json.load(f)
        data.append(log_entry)
        with open(archivo, "w") as f:
            json.dump(data, f, indent=2)

async def registrar(update, context):
    """Función principal para registrar mensajes."""
    msg = update.message

    if not msg:
        return

    # Detecta links
    if msg.text and "http" in msg.text:
        try:
            await procesar_link(update, context)
        except Exception as e:
            await guardar("errores", msg, f"Error procesando link: {str(e)}")
        await guardar("links", msg, msg.text)
        return

    # Detecta media
    tipo = "otros"
    contenido = "media"

    if msg.photo:
        tipo = "foto"
        contenido = msg.photo[-1].file_id  # Última resolución
    elif msg.video:
        tipo = "video"
        contenido = msg.video.file_id
    elif msg.audio:
        tipo = "audio"
        contenido = msg.audio.file_id
    elif msg.document:
        tipo = "documento"
        contenido = msg.document.file_name
    elif msg.text:
        tipo = "texto"
        contenido = msg.text

    await guardar(tipo, msg, contenido)