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
    try:
        result = subprocess.run(f'yt-dlp -j "{url}"', shell=True, capture_output=True, text=True)
        meta = json.loads(result.stdout)
        return meta.get("title", "KHASAM")
    except:
        return "KHASAM"

async def descargar_audio(user_id, url, msg):
    ruta = f"downloads/audio/{user_id}.mp3"
    cmd = (
        f'yt-dlp -x --audio-format mp3 --embed-thumbnail '
        f'--convert-thumbnails png --concurrent-fragments {FRAGMENTOS} --fixup never '
        f'-o "downloads/audio/{user_id}.%(ext)s" "{url}"'
    )
    await mostrar_progreso(cmd, msg)
    return ruta, f"downloads/audio/{user_id}.png"

async def descargar_video(user_id, url, msg):
    ruta = f"downloads/video/{user_id}.mp4"
    cmd = (
        f'yt-dlp -f mp4 --concurrent-fragments {FRAGMENTOS} --fixup never '
        f'-o "{ruta}" "{url}"'
    )
    await mostrar_progreso(cmd, msg)
    return ruta