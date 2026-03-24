from telegram import Update
from telegram.ext import ContextTypes
from telegram_log.logger import LOG_FILES
import os

ADMIN_ID = 8295382991  # Tu user_id de Telegram

# Ver logs por tipo
async def ver_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Solo el admin puede usar este comando")
        return

    tipo = context.args[0] if context.args else "mensaje"
    archivo = LOG_FILES.get(tipo)
    if not archivo or not os.path.exists(archivo):
        await update.message.reply_text(f"❌ No hay logs de tipo {tipo}")
        return

    with open(archivo, "r") as f:
        contenido = f.read()

    # Enviar solo los primeros 4000 caracteres si es muy largo
    if len(contenido) > 4000:
        contenido = contenido[:4000] + "\n... (truncado)"
    await update.message.reply_text(f"📄 Logs ({tipo}):\n<pre>{contenido}</pre>", parse_mode="HTML")

# Limpiar logs
async def limpiar_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Solo el admin puede usar este comando")
        return

    tipo = context.args[0] if context.args else "mensaje"
    archivo = LOG_FILES.get(tipo)
    if not archivo:
        await update.message.reply_text(f"❌ Tipo de log inválido: {tipo}")
        return

    with open(archivo, "w") as f:
        f.write("[]")
    await update.message.reply_text(f"✅ Logs de {tipo} limpiados")