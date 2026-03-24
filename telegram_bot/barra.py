# barra.py
import subprocess
import asyncio

async def mostrar_progreso(cmd, msg):
    proceso = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    for linea in proceso.stdout:
        if "%" in linea and "ETA" in linea:
            try:
                porcentaje = linea.split("%")[0].split()[-1]
                await msg.edit_text(f"📊 {porcentaje}% descargado 💜")
            except:
                pass
    proceso.wait()