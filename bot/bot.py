import os
import discord
from discord.ext import commands
import asyncio
import subprocess
import time
from flask import Flask
from threading import Thread

# Importações dos seus arquivos
import bot.config as config
import bot.alertas as alertas

# 1. Flask para o UptimeRobot (Mantém o serviço ativo)
app = Flask('')
@app.route('/')
def home():
    return "Bot e Backend Integrados: Online!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. Inicializador do Backend Go
def iniciar_backend_go():
    # Caminho do executável compilado (ajustado para a estrutura de pastas)
    caminho_bin = "./backend/server_bin"
    try:
        print("🚀 Iniciando Backend em Go (Processo Filho)...")
        # Inicia o binário do Go sem travar o Python
        subprocess.Popen([caminho_bin], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"❌ Erro crítico ao iniciar o backend em Go: {e}")

# 3. Configuração do Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado: {bot.user}")
    # Inicia a tarefa de monitoramento
    bot.loop.create_task(alertas.monitor_temperaturas(bot))

if __name__ == "__main__":
    # Inicia o Flask
    Thread(target=run_flask, daemon=True).start()
    
    # Inicia o Go
    iniciar_backend_go()
    
    # Inicia o Bot
    bot.run(config.TOKEN)
