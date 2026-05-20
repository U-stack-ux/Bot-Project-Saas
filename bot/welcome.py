import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 📥 EVENTO: Executado automaticamente quando um novo membro entra no servidor
    @commands.Cog.listener()
    async def on_member_join(self, member):
        # 1. Envia uma mensagem de boas-vindas diretamente na DM do usuário
        try:
            embed_dm = discord.Embed(
                title=f"👋 Bem-vindo ao Upscore SaaS, {member.name}!",
                description="O ecossistema definitivo para monitoramento inteligente de mineração cripto. 🚀",
                color=discord.Color.green()
            )
            embed_dm.add_field(
                name="🤖 Como começar?", 
                value="Vá até um canal de comandos no servidor e digite `/monitorar` para ativar a sua telemetria.", 
                inline=False
            )
            embed_dm.add_field(
                name="🛡️ Segurança Total", 
                value="Nossa estrutura conta com proteção anti-block e criptografia AES-256 para os seus tokens.", 
                inline=False
            )
            embed_dm.set_footer(text="Upscore SaaS • Inteligência Preditiva para Mineradores")
            
            await member.send(embed=embed_dm)
        except discord.Forbidden:
            print(f"⚠️ Não foi possível enviar DM para {member.name} (DMs desativadas pelo usuário).")

        # 2. Envia em um canal público de boas-vindas (Opcional)
        # 💡 Dica: Substitua o ID abaixo pelo ID real do canal de texto do seu Discord
        WELCOME_CHANNEL_ID = 123456789012345678  
        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        
        if channel:
            embed_pub = discord.Embed(
                title="✨ Novo minerador na área!",
                description=f"Seja muito bem-vindo ao time, {member.mention}! Que seu hash rate seja alto e suas temperaturas baixas. 💎🔥",
                color=discord.Color.blue()
            )
            embed_pub.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed_pub)

# Função obrigatória para o seu bot carregar este arquivo como uma extensão
async def setup(bot):
    await bot.add_cog(Welcome(bot))
