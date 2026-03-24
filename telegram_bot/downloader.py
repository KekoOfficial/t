# downloader.py
import os
import json
import subprocess
import asyncio
from .fragmento import FRAGMENTOS
from .barra import mostrar_progreso

os.makedirs("downloads/audio", exist_ok=True)
os.makedirs("downloads/video", exist_ok=True)

def obtener_metadata(url):
    """Obtiene título del video/audio"""
    try:
        result = subprocess.run(f'yt-dlp -j "{url}"', shell=True, capture_output=True, text=True)
        meta = json.loads(result.stdout)
        return meta.get("title", "KHASAM")
    except:
        return "KHASAM"

async def descargar_audio(user_id, url, msg):
    os.makedirs("downloads/audio", exist_ok=True)
    ruta_base = f"downloads/audio/{user_id}"
    ruta_mp3 = ruta_base + ".mp3"
    ruta_thumb = ruta_base + ".png"

    cmd = (
        f'yt-dlp -x --audio-format mp3 --embed-thumbnail '
        f'--convert-thumbnails png --concurrent-fragments {FRAGMENTOS} '
        f'-o "{ruta_base}.%(ext)s" "{url}" --no-overwrites'
    )
    await mostrar_progreso(cmd, msg)
    return ruta_mp3, ruta_thumb

async def descargar_video(user_id, url, msg):
    os.makedirs("downloads/video", exist_ok=True)
    ruta_base = f"downloads/video/{user_id}"
    ruta_mp4 = ruta_base + ".mp4"

    cmd = (
        f'yt-dlp -f mp4 --concurrent-fragments {FRAGMENTOS} '
        f'-o "{ruta_base}.%(ext)s" "{url}" --no-overwrites'
    )
    await mostrar_progreso(cmd, msg)
    return ruta_mp4