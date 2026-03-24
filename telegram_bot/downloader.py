import subprocess
import os
import json
import asyncio
from collections import deque
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# -------- COLA GLOBAL --------
cola = deque()
estado_cola = []
en_proceso = False
VIP_USERS = [123456789]  # 👑 Pon aquí tus IDs VIP

# -------- CARPETAS --------
os.makedirs("downloads/audio", exist_ok=True)
os.makedirs("downloads/video", exist_ok=True)

# -------- BOTONES --------
def botones():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎵 MP3", callback_data="mp3"),
         InlineKeyboardButton("🎬 MP4", callback_data="mp4")]
    ])

# -------- TIEMPO ESTIMADO --------
def estimar_tiempo(posicion):
    base = 15  # segundos aprox por descarga con fragmentos 10
    return posicion * base

# -------- METADATA --------
def obtener_metadata(url):
    try:
        result = subprocess.run(
            f'yt-dlp -j "{url}"',
            shell=True,
            capture_output=True,
            text=True
        )
        meta = json.loads(result.stdout)
        return meta.get("title", "KHASAM")
    except:
        return "KHASAM"

# -------- PROGRESO REAL --------
async def descargar_con_progreso(cmd, msg):
    proceso = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    for linea in proceso.stdout:
        if "%" in linea and "ETA" in linea:
            try:
                porcentaje = linea.split("%")[0].split()[-1]
                await msg.edit_text(f"📊 {porcentaje}% descargado...")
            except:
                pass
    proceso.wait()

# -------- COLA VISUAL --------
def ver_cola():
    texto = "🧾 COLA ACTUAL:\n\n"
    for i, user in enumerate(estado_cola, start=1):
        texto += f"{i}. {user}\n"
    return texto if estado_cola else "🧾 Cola vacía"

# -------- PROCESAR COLA --------
async def procesar_cola(context):
    global en_proceso
    if en_proceso or not cola:
        return

    en_proceso = True
    query, formato, user_id, username, url = cola.popleft()
    estado_cola.pop(0)

    msg = await query.message.reply_text("💜 Iniciando descarga...")

    title = obtener_metadata(url)

    try:
        if formato == "mp3":
            ruta = f"downloads/audio/{user_id}.mp3"
            cmd = (
                f'yt-dlp -x --audio-format mp3 --embed-thumbnail '
                f'--convert-thumbnails png --concurrent-fragments 10 --fixup never '
                f'-o "downloads/audio/{user_id}.%(ext)s" "{url}"'
            )
            await descargar_con_progreso(cmd, msg)
            thumb = f"downloads/audio/{user_id}.png"

            # Esperar archivo
            for _ in range(15):
                if os.path.exists(ruta):
                    break
                await asyncio.sleep(1)
            else:
                await query.message.reply_text("❌ Error: No se pudo descargar el audio")
                en_proceso = False
                if cola:
                    await procesar_cola(context)
                return

            await query.message.reply_audio(
                audio=open(ruta, "rb"),
                title=title,
                thumbnail=open(thumb, "rb") if os.path.exists(thumb) else None
            )

        else:
            ruta = f"downloads/video/{user_id}.mp4"
            cmd = (
                f'yt-dlp -f mp4 --concurrent-fragments 10 --fixup never '
                f'-o "{ruta}" "{url}"'
            )
            await descargar_con_progreso(cmd, msg)

            # Esperar archivo
            for _ in range(15):
                if os.path.exists(ruta):
                    break
                await asyncio.sleep(1)
            else:
                await query.message.reply_text("❌ Error: No se pudo descargar el video")
                en_proceso = False
                if cola:
                    await procesar_cola(context)
                return

            await query.message.reply_video(
                video=open(ruta, "rb"),
                caption=title
            )

        if os.path.exists(ruta):
            os.remove(ruta)

    except Exception as e:
        await query.message.reply_text(f"❌ Error: {e}")

    await query.message.reply_text("✅ Descarga completa 💜")

    en_proceso = False
    if cola:
        await procesar_cola(context)

# -------- BOTON HANDLER --------
async def botones_handler(update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    username = query.from_user.username or "User"
    url = context.user_data.get("link")

    if not url:
        await query.edit_message_text("❌ No hay link")
        return

    # PRIORIDAD VIP
    if user_id in VIP_USERS:
        cola.appendleft((query, query.data, user_id, username, url))
        estado_cola.insert(0, username + " 👑VIP")
        posicion = 1
    else:
        cola.append((query, query.data, user_id, username, url))
        estado_cola.append(username)
        posicion = len(cola)

    tiempo = estimar_tiempo(posicion)
    await query.edit_message_text(
        f"💜 Añadido a la cola\n"
        f"📊 Posición: {posicion}\n"
        f"⏱ Tiempo estimado: {tiempo}s\n\n"
        f"{ver_cola()}"
    )

    await procesar_cola(context)