import discord
from discord.ext import commands
import time
from collections import defaultdict

class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_history = defaultdict(list)
        self.punished_users = {} # ID: tempo_de_liberacao
        self.ADMIN_ID = 82782882 # ID configurado

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        # Ignora se for o próprio Admin
        if interaction.user.id == self.ADMIN_ID or not interaction.command:
            return
        
        user_id = interaction.user.id
        now = time.time()

        # 1. Checa se o usuário está castigado
        if user_id in self.punished_users:
            if now < self.punished_users[user_id]:
                await interaction.response.send_message("🚫 Você está em castigo por abuso de comandos. Tente novamente em 1 hora.", ephemeral=True)
                return
            else:
                del self.punished_users[user_id]

        # 2. Lógica de detecção: 5 comandos em 30 segundos
        self.user_history[user_id].append(now)
        self.user_history[user_id] = [t for t in self.user_history[user_id] if now - t < 30]

        if len(self.user_history[user_id]) > 5:
            self.punished_users[user_id] = now + 3600 # 1 hora de castigo
            
            # Avisa o usuário
            await interaction.response.send_message(f"⚠️ Você tentou o comando '{interaction.command.name}' várias vezes e está castigado por 1 hora.", ephemeral=True)
            
            # 3. Dedura para você no DM
            try:
                admin = await self.bot.fetch_user(self.ADMIN_ID)
                embed = discord.Embed(title="🚨 Alerta de Abuso", description=f"O usuário {interaction.user.mention} está abusando do comando `/{interaction.command.name}`.", color=discord.Color.red())
                embed.add_field(name="Ação", value="Castigo automático de 1h aplicado.", inline=False)
                await admin.send(embed=embed)
            except:
                pass # Se não conseguir enviar DM, o castigo já foi aplicado

async def setup(bot):
    await bot.add_cog(AntiSpam(bot))
