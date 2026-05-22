import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os
from dotenv import load_dotenv
import requests

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
BACKEND_URL = os.getenv('BACKEND_URL')

# Configuração do Flask para manter o Render feliz
app = Flask('')

@app.route('/')
def home():
    return "Bot Online", 200

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# Configuração do Bot com todos os privilégios ativos
class UpScoreBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.all())

    async def setup_hook(self):
        # CARREGAMENTO DAS EXTENSÕES MODULARES
        await self.load_extension("welcome")
        await self.load_extension("ia_commands")
        await self.load_extension("anti_spam")
        await self.load_extension("registration")
        await self.tree.sync()

bot = UpScoreBot()

# Injeta o comando power isolado
# setup_power_command(bot.tree)

@bot.tree.command(name="setup", description="Configurar conta e plano")
async def setup(interaction: discord.Interaction):
    # Aqui chamamos o fluxo de boas-vindas do welcome.py
    from welcome import MainView, UI_STRINGS
    lang = str(interaction.locale).lower()
    lang = lang if lang in UI_STRINGS else 'en-us'
    embed = discord.Embed(
        title=UI_STRINGS[lang]['welcome'],
        description=UI_STRINGS[lang]['desc'],
        color=0x00ffff
    )
    await interaction.response.send_message(embed=embed, view=MainView(interaction.locale), ephemeral=True)

@bot.tree.command(name="logs", description="Ver histórico de proteção")
async def logs(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    lang = str(interaction.locale).lower()
    # Lógica de logs com o backend...
    await interaction.followup.send("Painel de logs em desenvolvimento ou integração.", ephemeral=True)

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
