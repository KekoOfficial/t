import os
import json
from datetime import datetime

os.makedirs("telegram_log/logs", exist_ok=True)

LOG_FILES = {
    "mensaje": "telegram_log/logs/mensajes.json",
    "enlace": "telegram_log/logs/enlaces.json",
    "descarga": "telegram_log/logs/descargas.json",
    "accion": "telegram_log/logs/acciones.json"
}

# Inicializar archivos si no existen
for f in LOG_FILES.values():
    if not os.path.exists(f):
        with open(f, "w") as file:
            json.dump([], file, indent=2)

def guardar_log(tipo, usuario, contenido):
    archivo = LOG_FILES.get(tipo, LOG_FILES["mensaje"])
    logs = []
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            logs = json.load(f)
    logs.append({
        "usuario": usuario,
        "contenido": contenido,
        "fecha": str(datetime.now())
    })
    with open(archivo, "w") as f:
        json.dump(logs, f, indent=2)