import os
import asyncio
from threading import Thread
from flask import Flask
import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
from commands_power import setup_power_command

# TRUQUE DO FLASK PARA LIBERAR A PORTA NO RENDER
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Python Online!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_flask).start()
# -----------------------------------------------

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
BACKEND_URL = os.getenv('BACKEND_URL')

# Configuração do Administrador (ID ou Username)
YOUR_ID = '82782882'

def is_admin(interaction: discord.Interaction) -> bool:
    user_id_str = str(interaction.user.id)
    user_name = interaction.user.name
    return user_id_str == YOUR_ID or YOUR_ID in user_name

STRINGS = {
    'pt-br': {
        "welcome": "👋 Upscore ULTRA Ativado!.",
        "thermal": "🛡️ Proteção Térmica Individual Ativa.",
        "recovery": "⚙️ Autocura: Religamento automático ativo.",
        "log_cmd": "🔍 Use /logs para auditar minhas ações.",
        "not_found": "🚫 Nenhum log registrado.",
        "del_ok": "✅ Usuário (user) removido com sucesso!",
        "access_denied": "❌ Acesso negado."
    },
    'en-us': {
        "welcome": "👋 Upscore ULTRA Activated!.",
        "thermal": "🛡️ Individual Thermal Protection Active.",
        "recovery": "⚙️ Auto-healing: Automatic restart active.",
        "log_cmd": "🔍 Use /logs to audit my actions.",
        "not_found": "🚫 No logs recorded.",
        "del_ok": "✅ User (user) successfully removed!",
        "access_denied": "❌ Access denied."
    }
}

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
setup_power_command(bot.tree)

@bot.tree.command(name="setup", description="Configurar conta e plano")
async def setup(interaction: discord.Interaction):
    lang = str(interaction.locale).lower()
    text = STRINGS.get(lang, STRINGS['en-us'])
    
    embed = discord.Embed(title=text['welcome'], color=0x00ffff)
    embed.add_field(name="Thermal", value="Check: 10s", inline=False)
    embed.add_field(name="Info", value=text['log_cmd'], inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="logs", description="Ver histórico de proteção")
async def logs(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    lang = str(interaction.locale).lower()
    text = STRINGS.get(lang, STRINGS['en-us'])
    
    try:
        resp = requests.get(f"{BACKEND_URL}/logs?id={interaction.user.id}")
        data = resp.json()
        if not data:
            await interaction.followup.send(text['not_found'], ephemeral=True)
            return
        
        embed = discord.Embed(title="🔍 Logs", color=0xffa500)
        for item in data:
            status = "🛑 STOP" if item['action'] == "STOP" else "✅ START"
            embed.add_field(name=status, value=f"{item['rig_name']} | {item['details']}", inline=False)
        await interaction.followup.send(embed=embed, ephemeral=True)
    except:
        await interaction.followup.send("❌ Error Backend", ephemeral=True)

@bot.tree.command(name="ade_delete", description="REMOVIR Usuário marcando @")
async def ade_delete(interaction: discord.Interaction, usuario: discord.User):
    lang = str(interaction.locale).lower()
    text = STRINGS.get(lang, STRINGS['en-us'])
    
    if not is_admin(interaction):
        await interaction.response.send_message(text['access_denied'], ephemeral=True)
        return
    
    try:
        resp = requests.delete(f"{BACKEND_URL}/admin/delete/user_id={usuario.id}")
        if resp.status_code == 200:
            await interaction.response.send_message(text['del_ok'].replace("(user)", usuario.mention), ephemeral=True)
        else:
            await interaction.response.send_message("❌ Error Server", ephemeral=True)
    except:
        await interaction.response.send_message("❌ Offline", ephemeral=True)

if __name__ == "__main__":
    bot.run(TOKEN)
