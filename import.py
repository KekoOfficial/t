import os
import subprocess
import json

ADMIN_ID = 8295382991

# ---------------- COLA ----------------
estado_cola = []

def agregar_a_cola(user_id, url):
    estado_cola.append({"user_id": user_id, "url": url})
    return len(estado_cola)

def quitar_de_cola(user_id):
    global estado_cola
    estado_cola = [x for x in estado_cola if x["user_id"] != user_id]

# ---------------- DESCARGAS ----------------
async def descargar_audio(user_id, url):
    os.makedirs("downloads/audio", exist_ok=True)
    audio_path = f"downloads/audio/{user_id}.mp3"
    thumb_path = f"downloads/audio/{user_id}.png"
    cmd = f'yt-dlp -x --audio-format mp3 --embed-thumbnail --convert-thumbnails png -o "{audio_path}" "{url}"'
    subprocess.run(cmd, shell=True)
    return audio_path, thumb_path if os.path.exists(thumb_path) else None

async def descargar_video(user_id, url):
    os.makedirs("downloads/video", exist_ok=True)
    video_path = f"downloads/video/{user_id}.mp4"
    cmd = f'yt-dlp -f mp4 -o "{video_path}" "{url}"'
    subprocess.run(cmd, shell=True)
    return video_path

def obtener_metadata(url):
    try:
        result = subprocess.run(f'yt-dlp -j "{url}"', shell=True, capture_output=True, text=True)
        meta = json.loads(result.stdout)
        return meta.get("title", "KHASAM Download")
    except:
        return "KHASAM Download"