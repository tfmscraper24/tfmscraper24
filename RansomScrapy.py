import sqlite3
from bs4 import BeautifulSoup
import requests
import socks
import socket
import os
import logging
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.request import HTTPXRequest
from telegram.error import NetworkError

# Configurar el proxy SOCKS5 de Tor
socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
socket.socket = socks.socksocket

# Obtener la ruta al escritorio
desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
db_path = os.path.join(desktop_path, 'companies.db')

# Configuración del logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Función para verificar la conexión SOCKS5
def check_socks5_proxy():
    try:
        proxies = {
            'http': 'socks5h://localhost:9050',
            'https': 'socks5h://localhost:9050'
        }
        response = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=20)
        if response.status_code == 200:
            print("El proxy SOCKS5 está funcionando correctamente.")
            return True
        else:
            print("Error en la conexión a través del proxy SOCKS5.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error al verificar el proxy SOCKS5: {e}")
        return False

# Función para iniciar el bot
async def start(update: Update, context: CallbackContext) -> None:
    """Envía un mensaje cuando se emite el comando /start."""
    user = update.effective_user
    await update.message.reply_markdown_v2(
        fr'Hola {user.mention_markdown_v2()}\! Envía el nombre de una empresa para buscar su información\.',
        reply_markup=ForceReply(selective=True),
    )

# Función para manejar los mensajes de texto
async def search(update: Update, context: CallbackContext) -> None:
    """Busca en la base de datos la empresa que el usuario solicita."""
    user_input = update.message.text
    info = get_company_info(user_input)
    await update.message.reply_text(info)

# Función para buscar la información de la empresa en la base de datos
def get_company_info(company_name):
    """Busca en la base de datos y devuelve información sobre la empresa."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT title, revenue, data_volume, data_description FROM companies WHERE title LIKE ?", ('%' + company_name + '%',))
    result = cursor.fetchone()
    conn.close()
    if result:
        return f"Empresa: {result[0]}\nRevenue: {result[1]}\nData Volume: {result[2]}\nDescription: {result[3]}"
    else:
        return "Empresa no encontrada."

def main():
    """Inicia el bot."""
    if not check_socks5_proxy():
        print("El proxy SOCKS5 no está funcionando. Verifica la configuración de Tor.")
        return

    # Configurar el cliente HTTPX con el proxy
    request = HTTPXRequest(
        proxy="socks5://localhost:9050",
        connect_timeout=60.0,  # Aumentar el tiempo de espera de conexión
        read_timeout=60.0     # Aumentar el tiempo de espera de lectura
    )

    # Crea el Application y pásale el token de tu bot.
    application = Application.builder().token("YOUR_TELEGRAM_BOT_TOKEN_HERE").request(request).build()

    # Diferentes command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))

    # Inicia el Bot
    try:
        application.run_polling()
    except NetworkError as e:
        logger.error(f"Error de red: {e}. Verifique la conexión y el proxy SOCKS5.")
    except Exception as e:
        logger.error(f"Se produjo un error inesperado: {e}")

if __name__ == "__main__":
    main()
