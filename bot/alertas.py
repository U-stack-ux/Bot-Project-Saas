import discord
from discord.ext import commands, tasks
import requests
import os

class Alertas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backend_url = os.getenv('BACKEND_URL')
        self.monitor_temp.start()

    def cog_unload(self):
        self.monitor_temp.cancel()

    @tasks.loop(minutes=2)
    async def monitor_temp(self):
        try:
            # 1. Consulta o novo endpoint que preparamos no Go
            resp = requests.get(f"{self.backend_url}/internal/get-active-users")
            if resp.status_code != 200: 
                return
            
            users = resp.json() 
            
            for user_data in users:
                # 2. Varre as rigs dos usuários com plano ULTRA que o Go retornou
                if user_data.get("plano") == "ULTRA":
                    for rig in user_data.get("rigs", []):
                        temp = rig.get("temperatura", 0)
                        
                        # 3. Se a temperatura ultrapassar o limite crítico de 75°C, dispara
                        if temp > 75: 
                            await self.enviar_alerta_dm(user_data["discord_id"], rig)
                            
        except Exception as e:
            print(f"Erro no monitor de temperatura: {e}")

    async def enviar_alerta_dm(self, discord_id, rig):
        user = self.bot.get_user(int(discord_id))
        if user:
            embed = discord.Embed(
                title="⚠️ Alerta de Temperatura Crítica",
                description=f"A sua Rig **{rig['nome']}** atingiu **{rig['temperatura']}°C**! Recomendamos verificação imediata para evitar danos ao hardware.",
                color=0xff0000
            )
            try:
                await user.send(embed=embed)
            except:
                pass # Evita travar o bot caso o usuário tenha fechado as DMs

async def setup(bot):
    await bot.add_cog(Alertas(bot))
