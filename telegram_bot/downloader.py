# downloader.py
import os
import subprocess
import json
import glob
import asyncio
from .fragmento import FRAGMENTOS
from .barra import mostrar_progreso

# Crear carpetas si no existen
os.makedirs("downloads/audio", exist_ok=True)
os.makedirs("downloads/video", exist_ok=True)

# ----------------- FUNCIONES -----------------

def obtener_metadata(url: str) -> str:
    """Obtiene título del video/audio"""
    try:
        result = subprocess.run(
            f'yt-dlp -j "{url}"', shell=True, capture_output=True, text=True
        )
        meta = json.loads(result.stdout)
        return meta.get("title", "KHASAM Download")
    except Exception:
        return "KHASAM Download"

async def descargar_audio(user_id: int, url: str, msg) -> tuple[str, str]:
    """Descarga MP3 con thumb y fragmentos, devuelve ruta de audio y thumb"""
    os.makedirs("downloads/audio", exist_ok=True)
    base = f"downloads/audio/{user_id}"
    
    # Comando yt-dlp con fragmentos 10
    cmd = (
        f'yt-dlp -x --audio-format mp3 --embed-thumbnail --convert-thumbnails png '
        f'--concurrent-fragments {FRAGMENTOS} '
        f'-o "{base}.%(ext)s" "{url}" --no-overwrites'
    )
    
    # Mostrar barra de progreso mientras descarga
    await mostrar_progreso(cmd, msg)

    # Encontrar archivos finales
    mp3_files = glob.glob(f"downloads/audio/{user_id}*.mp3")
    png_files = glob.glob(f"downloads/audio/{user_id}*.png")
    if not mp3_files:
        raise Exception("❌ No se pudo descargar el audio")
    
    mp3 = mp3_files[0]
    thumb = png_files[0] if png_files else None
    return mp3, thumb

async def descargar_video(user_id: int, url: str, msg) -> str:
    """Descarga video MP4 con fragmentos 10, devuelve ruta del archivo"""
    os.makedirs("downloads/video", exist_ok=True)
    base = f"downloads/video/{user_id}"

    # Comando yt-dlp con fragmentos
    cmd = (
        f'yt-dlp -f mp4 --concurrent-fragments {FRAGMENTOS} '
        f'-o "{base}.%(ext)s" "{url}" --no-overwrites'
    )
    
    # Mostrar barra de progreso
    await mostrar_progreso(cmd, msg)

    # Buscar archivo final
    mp4_files = glob.glob(f"downloads/video/{user_id}*.mp4")
    if not mp4_files:
        raise Exception("❌ No se pudo descargar el video MP4, revisa el enlace")
    return mp4_files[0]