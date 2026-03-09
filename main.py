import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 1. Cargar el Token de forma segura desde el archivo .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# 2. Definir las funciones asíncronas (Comandos)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde al comando /start"""
    await update.message.reply_text("¡Hola! Soy tu bot financiero. El sistema está en línea. 🟢")

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando de prueba para verificar latencia"""
    await update.message.reply_text("¡Pong! Te escucho perfectamente.")

# 3. Función principal que orquesta todo
def main():
    if not TOKEN:
        print("❌ ERROR: No se ha encontrado el TELEGRAM_TOKEN en el archivo .env")
        return

    print("Iniciando el bot...")
    
    # Construir la aplicación con tu Token
    app = Application.builder().token(TOKEN).build()

    # Conectar los comandos de Telegram con tus funciones de Python
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("ping", ping_command))

    # Dejar el bot "escuchando" indefinidamente
    print("Bot en línea. Presiona Ctrl+C para detenerlo.")
    app.run_polling()

if __name__ == '__main__':
    main()