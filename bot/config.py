import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BACKEND_URL = "http://localhost:3000/api"
UPDATE_INTERVAL = 5
