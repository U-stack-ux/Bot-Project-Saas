import discord
from discord.ext import commands
import requests
import os
import asyncio
from bot.temperature_control import UltraTemperatureView, ProTemperatureView

# --- FUNÇÃO 1: Construção do Embed de Telemetria ---
def build_telemetry_embed(plano, plataforma, rigs, intervalo):
    limite = 2 if plano == "FREE" else (10 if plano == "PRO" else 9999)
    rigs_permitidas = rigs[:limite]
    
    embed = discord.Embed(
        title=f"💻 Painel Real ({plataforma})",
        description=f"Plano: **{plano}** | Atualizando a cada **{int(intervalo)}s**.",
        color=0x00ffff
    )
    
    for r in rigs_permitidas:
        embed.add_field(
            name=f"⚙️ {r.get('nome', 'Worker')}",
            value=f"Status: `{r.get('status', 'N/A')}` | Temp: `{r.get('temperatura', 0)}°C`",
            inline=False
        )
        
    if len(rigs) > limite:
        embed.add_field(name="🔒 Limite de Plano", value=f"Você tem {len(rigs)-limite} máquinas ocultas.")
        
    return embed

# --- FUNÇÃO 2: Lógica de Busca na API Backend ---
async def fetch_backend_data(url, discord_id):
    try:
        resp = requests.get(f"{url}/internal/check-plan?discord_id={discord_id}")
        return resp.json() if resp.status_code == 200 else None
    except:
        return None

# ========================================================
# VIEW DO PAINEL DE CONTROLO DE RIGS
# ========================================================
class RigSelectorView(discord.ui.View):
    def __init__(self, plano_atual):
        super().__init__(timeout=None)
        self.plano = plano_atual

    @discord.ui.button(label="🌡️ Termostato Inteligente", style=discord.ButtonStyle.blurple, row=0)
    async def btn_thermostat_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.plano == "ULTRA":
            view_termostato = UltraTemperatureView(current_min=30, current_max=95)
            embed = discord.Embed(
                title="🤖 [PROTEÇÃO ULTRA] - Termostato Inteligente",
                description="Define a temperatura para ligar/desligar a tua rig automaticamente (de 5 em 5 graus).",
                color=0xff00ff
            )
        elif self.plano == "PRO":
            view_termostato = ProTemperatureView(current_max=95)
            embed = discord.Embed(
                title="🌡️ [PROTEÇÃO PRO] - Limite de Segurança",
                description="Define o limite máximo de temperatura para o corte automático da rig com defeito.",
                color=0x00aaff
            )
        else:
            await interaction.response.send_message(
                "❌ O Termostato Inteligente é exclusivo para assinantes **PRO** e **ULTRA**. Faz o upgrade!",
                ephemeral=True
            )
            return

        await interaction.response.send_message(embed=embed, view=view_termostato, ephemeral=True)

# --- A CLASSE PRINCIPAL ORGANIZADA ---
class RigSelector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backend_url = os.getenv('BACKEND_URL')
        self.active_tasks = {}

    @commands.hybrid_command(name="painel")
    async def painel(self, ctx):
        await ctx.defer(ephemeral=True)
        data = await fetch_backend_data(self.backend_url, str(ctx.author.id))
        
        if not data or not data.get("has_plan"):
            return await ctx.followup.send("❌ Sem plano ativo.", ephemeral=True)
        
        plano_cliente = data.get("plano", "FREE")
        
        embed_painel = build_telemetry_embed(
            plano_cliente, 
            data.get("plataforma", "HIVEOS"), 
            data.get("rigs", []), 
            60
        )
        
        view_botoes = RigSelectorView(plano_atual=plano_cliente)
        msg = await ctx.followup.send(embed=embed_painel, view=view_botoes, ephemeral=True)
        
        self.start_live_updater(ctx.author, msg)

    def start_live_updater(self, user, message):
        discord_id = str(user.id)
        if discord_id in self.active_tasks:
            self.active_tasks[discord_id].cancel()
        self.active_tasks[discord_id] = self.bot.loop.create_task(self.live_updater_loop(user, message))

    async def live_updater_loop(self, user, message):
        while not self.bot.is_closed():
            data = await fetch_backend_data(self.backend_url, str(user.id))
            if not data or not data.get("has_plan"): 
                break
            
            plano_cliente = data.get("plano", "FREE")
            embed_painel = build_telemetry_embed(
                plano_cliente,
                data.get("plataforma", "HIVEOS"),
                data.get("rigs", []),
                60
            )
            
            view_botoes = RigSelectorView(plano_atual=plano_cliente)
            
            await message.edit(content="", embed=embed_painel, view=view_botoes)
            await asyncio.sleep(float(data.get("check_interval", 60)))

async def setup(bot):
    await bot.add_cog(RigSelector(bot))
