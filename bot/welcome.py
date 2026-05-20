import discord
from discord.ext import commands
import requests
import os

UI_STRINGS = {
    'pt-br': {
        'welcome': "Bem-vindo ao UpscoreSaaS",
        'desc': "⚠️ **AVISO LEGAL:** Não nos responsabilizamos por instabilidades ou erros de dados vindos diretamente das APIs de terceiros (HiveOS/NiceHash).",
        'btn_free': "Teste Grátis",
        'btn_paid': "Planos Pagos",
        'btn_accept': "Aceitar Termos e Ativar"
    },
    'es-es': {
        'welcome': "Bienvenido a UpscoreSaaS",
        'desc': "⚠️ **AVISO LEGAL:** No nos responsabilizamos por fallas o demoras provenientes de las APIs de terceros (HiveOS/NiceHash).",
        'btn_free': "Prueba Gratis",
        'btn_paid': "Planes Pagos",
        'btn_accept': "Aceptar Términos y Activar"
    },
    'en-us': {
        'welcome': "Welcome to UpscoreSaaS",
        'desc': "⚠️ **LEGAL DISCLAIMER:** We are not responsible for outages or telemetry errors from third-party APIs (HiveOS/NiceHash).",
        'btn_free': "Free Trial",
        'btn_paid': "Paid Plans",
        'btn_accept': "Accept Terms & Activate"
    }
}

class MainView(discord.ui.View):
    def __init__(self, locale, discord_id):
        super().__init__(timeout=None)
        self.discord_id = discord_id
        self.backend_url = os.getenv('BACKEND_URL')
        self.lang = locale if locale in UI_STRINGS else 'en-us'
        self.texts = UI_STRINGS[self.lang]
        
        # Criação dinâmica baseada no seu print original
        self.add_item(discord.ui.Button(label=self.texts['btn_free'], style=discord.ButtonStyle.green, custom_id="btn_free"))
        self.add_item(discord.ui.Button(label=self.texts['btn_paid'], style=discord.ButtonStyle.blurple, custom_id="btn_paid"))
        
        # Botão de aceitação obrigatória adicionado com segurança
        btn_law = discord.ui.Button(label=self.texts['btn_accept'], style=discord.ButtonStyle.danger, custom_id="btn_law_accept")
        btn_law.callback = self.accept_law_callback
        self.add_item(btn_law)

    async def accept_law_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            resp = requests.post(f"{self.backend_url}/user/accept-disclaimer", json={"discord_id": str(self.discord_id)})
            if resp.status_code == 200:
                await interaction.followup.send("✅ Proteção jurídica validada! Seu monitoramento está ativo.", ephemeral=True)
            else:
                await interaction.followup.send("❌ Erro ao salvar confirmação no servidor.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Falha de conexão: {e}", ephemeral=True)

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        locale = str(member.locale).lower()
        lang = locale if locale in UI_STRINGS else 'en-us'
        
        embed = discord.Embed(
            title=UI_STRINGS[lang]['welcome'], 
            description=f"Otimize sua mineração com IA.\n\n{UI_STRINGS[lang]['desc']}", 
            color=0x00ffff
        )
        await member.send(embed=embed, view=MainView(locale, member.id))

async def setup(bot):
    await bot.add_cog(Welcome(bot))
