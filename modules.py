# modules.py
import os
import subprocess
import json
from datetime import datetime

# ---------------- CONFIG ----------------
FRAGMENTOS = 10  # Número de fragmentos para descargas rápidas
os.makedirs("downloads/audio", exist_ok=True)
os.makedirs("downloads/video", exist_ok=True)

# ---------------- COLA DE USUARIOS ----------------
estado_cola = []  # Lista de dicts: {"user_id": ..., "url": ...}

def agregar_a_cola(user_id, url):
    estado_cola.append({"user_id": user_id, "url": url, "inicio": datetime.now().timestamp()})
    return len(estado_cola)

def quitar_de_cola(user_id):
    global estado_cola
    estado_cola = [u for u in estado_cola if u["user_id"] != user_id]

def posicion_en_cola(user_id):
    for i, u in enumerate(estado_cola):
        if u["user_id"] == user_id:
            return i + 1
    return None

# ---------------- DESCARGAS ----------------
async def descargar_audio(user_id, url, query=None):
    archivo_mp3 = f"downloads/audio/{user_id}.mp3"
    archivo_thumb = f"downloads/audio/{user_id}.png"

    comando = (
        f'yt-dlp -x --audio-format mp3 --embed-thumbnail --convert-thumbnails png '
        f'--concurrent-fragments {FRAGMENTOS} -o "{archivo_mp3}" "{url}"'
    )
    try:
        subprocess.run(comando, shell=True, check=True)
        # Convertir thumbnail a png si existe
        thumb_original = archivo_mp3.replace(".mp3", ".webp")
        if os.path.exists(thumb_original):
            os.rename(thumb_original, archivo_thumb)
        else:
            archivo_thumb = None
        return archivo_mp3, archivo_thumb
    except Exception as e:
        raise Exception(f"❌ No se pudo descargar el audio: {e}")

async def descargar_video(user_id, url, query=None):
    archivo_mp4 = f"downloads/video/{user_id}.mp4"

    comando = (
        f'yt-dlp -f mp4 --concurrent-fragments {FRAGMENTOS} '
        f'-o "{archivo_mp4}" "{url}"'
    )
    try:
        subprocess.run(comando, shell=True, check=True)
        return archivo_mp4
    except Exception as e:
        raise Exception(f"❌ No se pudo descargar el video: {e}")

# ---------------- METADATA ----------------
def obtener_metadata(url):
    try:
        result = subprocess.run(f'yt-dlp -j "{url}"', shell=True, capture_output=True, text=True)
        meta = json.loads(result.stdout)
        return meta.get("title", "KHASAM Download")
    except:
        return "KHASAM Download"

# ---------------- ADMIN ----------------
ADMIN_ID = 8295382991  # Reemplaza con tu user_id