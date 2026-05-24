import discord
from discord.ext import commands
import config
from components import WelcomeView
from ui_factory import UI
# 1. Importe o seu novo gerenciador de notificações
from notification_logic import NotificationManager 

class MiningBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        # 2. Inicialize o gerenciador aqui para ele ficar acessível
        self.notifier = NotificationManager() 

    async def setup_hook(self):
        self.add_view(WelcomeView())
        print("✅ Sistema pronto.")

    async def on_ready(self):
        print(f"Logged as {self.user}")

bot = MiningBot()

@bot.command()
async def start(ctx):
    await ctx.send(embed=UI.welcome_embed(), view=WelcomeView())

bot.run(config.TOKEN)
