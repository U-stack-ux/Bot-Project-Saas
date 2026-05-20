import discord
from discord.ext import commands
import requests # Certifique-se de ter instalado: pip install requests

class IACommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="diagnostico", description="Obtenha um diagnóstico técnico da sua Rig com IA")
    async def diagnostico(self, ctx):
        await ctx.send("🤖 Consultando a inteligência artificial do Upscore SaaS...", ephemeral=True)
        
        # 💡 Aqui o Python conversa com o seu servidor Go que está rodando no Render
        # Substitua 'SEU_URL_DO_RENDER' pelo link real do seu backend em Go
        backend_url = "https://seu-backend-go.onrender.com/ia/analisar" 
        
        try:
            # Envia o ID do Discord para o Go identificar quem é o cliente
            payload = {"discord_id": str(ctx.author.id)}
            response = requests.post(backend_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                analise = data.get("diagnostico", "Nenhuma análise disponível no momento.")
                
                embed = discord.Embed(
                    title="🧠 Diagnóstico Técnico IA",
                    description=analise,
                    color=discord.Color.purple()
                )
                embed.set_footer(text="Upscore SaaS • Tecnologia Preditiva")
                await ctx.send(embed=embed)
            else:
                await ctx.send("⚠️ Não consegui conectar com o servidor central. Tente novamente em instantes.")
                
        except Exception as e:
            await ctx.send(f"❌ Erro ao processar o diagnóstico: {str(e)}")

async def setup(bot):
    await bot.add_cog(IACommands(bot))
