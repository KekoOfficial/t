# telegram_bot/tiktok.py
import os
import subprocess
from datetime import datetime

os.makedirs("downloads/video", exist_ok=True)

# ---------------- DESCARGA DIRECTA TIKTOK ----------------
async def descargar_tiktok(user_id, url):
    """
    Descarga un video de TikTok directo sin botones.
    user_id: ID del usuario para separar archivos
    url: enlace del TikTok
    """
    archivo_mp4 = f"downloads/video/{user_id}.mp4"
    comando = (
        f'yt-dlp -f mp4 --concurrent-fragments 10 '
        f'-o "{archivo_mp4}" "{url}"'
    )

    try:
        subprocess.run(comando, shell=True, check=True)
        if os.path.exists(archivo_mp4):
            return archivo_mp4
        else:
            raise Exception("❌ No se encontró el archivo después de la descarga")
    except Exception as e:
        raise Exception(f"❌ Error descargando TikTok: {e}")