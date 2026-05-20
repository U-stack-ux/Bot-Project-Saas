import discord
from discord.ext import commands
import requests
import os

class Registration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backend_url = os.getenv('BACKEND_URL')

    @commands.hybrid_command(name="cadastrar", description="Configure sua API e escolha seu plano")
    async def cadastrar(self, ctx, plataforma: str, token: str):
        await ctx.send("⚙️ Configurando sua conta no Upscore SaaS...", ephemeral=True)
        
        # Mapeamento para garantir que vai em minúsculo pro Go
        plat = plataforma.lower().strip()
        if plat not in ["hiveos", "nicehash"]:
            await ctx.send("❌ Plataforma inválida. Escolha entre 'hiveos' ou 'nicehash'.", ephemeral=True)
            return

        payload = {
            "discord_id": str(ctx.author.id),
            "plano_escolhido": "FREE",  # Define plano inicial como teste grátis
            "plataforma": plat,
            "api_token": token  # Enviando o nome genérico que configuramos no Go
        }
        
        try:
            resp = requests.post(f"{self.backend_url}/users/set-plan", json=payload)
            if resp.status_code == 200:
                await ctx.send(f"✅ Conta {plat.upper()} configurada com sucesso!", ephemeral=True)
            else:
                await ctx.send("❌ Falha na comunicação com o banco de dados. Tente novamente.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ Erro crítico: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Registration(bot))
