import discord
from discord.ext import commands
import requests
import os
import asyncio

# --- FUNÇÃO 1: Construção do Embed de Telemetria ---
def build_telemetry_embed(plano, plataforma, rigs, intervalo):
    limite = 2 if plano == "FREE" else (10 if plano == "PRO" else 9999)
    rigs_permitidas = rigs[:limite]
    
    embed = discord.Embed(
        title=f"📊 Painel Real ({plataforma})", 
        description=f"Plano: **{plano}** | Atualizando a cada **{int(intervalo)}s**", 
        color=0x00ffff
    )
    
    for r in rigs_permitidas:
        embed.add_field(
            name=f"🧱 {r.get('nome', 'Worker')}", 
            value=f"Status: `{r.get('status', 'N/A')}` | Temp: `{r.get('temperatura', 0)}°C`", 
            inline=False
        )
        
    if len(rigs) > limite:
        embed.add_field(name="🔒 Limite de Plano", value=f"Você tem {len(rigs)-limite} máquinas ocultas. Faça upgrade!", inline=False)
    return embed

# --- FUNÇÃO 2: Lógica de Busca na API Backend ---
async def fetch_backend_data(url, discord_id):
    try:
        resp = requests.get(f"{url}/internal/check-plan?discord_id={discord_id}")
        return resp.json() if resp.status_code == 200 else None
    except:
        return None

# --- A CLASSE PRINCIPAL ORGANIZADA ---
class RigSelector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backend_url = os.getenv('BACKEND_URL')
        self.active_tasks = {}

    @commands.hybrid_command(name="painel")
    async def painel(self, ctx):
        # Aqui entra a chamada para a View que você já tem
        await ctx.defer(ephemeral=True)
        data = await fetch_backend_data(self.backend_url, str(ctx.author.id))
        if not data or not data.get("has_plan"):
            return await ctx.followup.send("❌ Sem plano ativo.", ephemeral=True)
        
        # ... (código da view que você já possui) ...
        await ctx.followup.send("📋 Painel carregado.", ephemeral=True)

    def start_live_updater(self, user, message):
        discord_id = str(user.id)
        if discord_id in self.active_tasks: self.active_tasks[discord_id].cancel()
        self.active_tasks[discord_id] = self.bot.loop.create_task(self.live_updater_loop(user, message))

    async def live_updater_loop(self, user, message):
        while not self.bot.is_closed():
            data = await fetch_backend_data(self.backend_url, str(user.id))
            if not data or not data.get("has_plan"): break
            
            embed = build_telemetry_embed(
                data.get("plano", "FREE"), 
                data.get("plataforma", "HIVEOS"), 
                data.get("rigs", []), 
                data.get("check_interval", 60)
            )
            
            await message.edit(content="", embed=embed)
            await asyncio.sleep(float(data.get("check_interval", 60)))

async def setup(bot):
    await bot.add_cog(RigSelector(bot))
