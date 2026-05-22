import discord
from discord.ext import commands
import requests
import os
import asyncio

UI_STRINGS = {
    'pt-br': {
        'welcome': "👋 Bem-vindo ao UpscoreSaaS!",
        'desc': "Otimize sua mineração com IA em tempo real.",
        'legal': "**AVISO LEGAL:** Não nos responsabilizamos por instabilidades ou erros de dados vindos diretamente das APIs de terceiros.",
        'btn_free': "🌱 Teste Grátis",
        'btn_paid': "💎 Planos Pagos",
        'btn_accept': "✅ Aceitar Termos e Continuar",
        'modal_title': "Cadastro de API de Mineração",
        'modal_plat': "Plataforma (hiveos ou nicehash)",
        'modal_token': "Insira seu Token / API Key",
        'success': "✅ Conta configurada com sucesso!"
    },
    'es-es': {
        'welcome': "👋 ¡Bienvenido a UpscoreSaaS!",
        'desc': "Optimice su minería con IA en tiempo real.",
        'legal': "**AVISO LEGAL:** No nos responsabilizamos por fallas o demoras provenientes de las APIs de terceros.",
        'btn_free': "🌱 Prueba Gratis",
        'btn_paid': "💎 Planes Pagos",
        'btn_accept': "✅ Aceptar Términos y Continuar",
        'modal_title': "Registro de API de Minería",
        'modal_plat': "Plataforma (hiveos o nicehash)",
        'modal_token': "Inserte su Token / API Key",
        'success': "✅ ¡Cuenta configurada con éxito!"
    },
    'en-us': {
        'welcome': "👋 Welcome to UpscoreSaaS!",
        'desc': "Optimize your mining with real-time AI.",
        'legal': "**LEGAL DISCLAIMER:** We are not responsible for outages or telemetry errors from third-party APIs.",
        'btn_free': "🌱 Free Trial",
        'btn_paid': "💎 Paid Plans",
        'btn_accept': "✅ Accept Terms & Continue",
        'modal_title': "Mining API Registration",
        'modal_plat': "Platform (hiveos or nicehash)",
        'modal_token': "Enter your Token / API Key",
        'success': "✅ Account configured successfully!"
    }
}

# ==========================================
# VIEW 2: TELA DO ACORDO LEGAL
# ==========================================
class LegalDisclaimerView(discord.ui.View):
    def __init__(self, lang, plano_escolhido):
        super().__init__(timeout=None)
        self.lang = lang
        self.plano_escolhido = plano_escolhido
        self.textis = UI_STRINGS[lang]
        
        # LINK DO SEU BACKEND EM GO DO RENDER COLOQUE AQUI
        url_site = "https://bot-project-saas.onrender.com"
        
        btn = discord.ui.Button(
            label=self.textis['btn_accept'], 
            style=discord.ButtonStyle.link, 
            url=url_site
        )
        self.add_item(btn)

# ==========================================
# VIEW 1: TELA DE ENTRADA (ESCOLHA DE PLANOS)
# ==========================================
class MainView(discord.ui.View):
    def __init__(self, locale):
        super().__init__(timeout=None)
        self.lang = locale if locale in UI_STRINGS else 'en-us'
        self.textis = UI_STRINGS[self.lang]
        
        btn_free = discord.ui.Button(label=self.textis['btn_free'], style=discord.ButtonStyle.green, custom_id="flow_free")
        btn_free.callback = self.choose_free
        self.add_item(btn_free)
        
        btn_paid = discord.ui.Button(label=self.textis['btn_paid'], style=discord.ButtonStyle.blurple, custom_id="flow_paid")
        btn_paid.callback = self.choose_paid
        self.add_item(btn_paid)

    async def choose_free(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Termos de Uso - Teste Grátis", description=UI_STRINGS[self.lang]['legal'], color=0x00ff00)
        await interaction.response.send_message(embed=embed, view=LegalDisclaimerView(self.lang, "FREE"), ephemeral=True)

    async def choose_paid(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Termos de Uso - Assinatura VIP", description=UI_STRINGS[self.lang]['legal'], color=0xff00ff)
        await interaction.response.send_message(embed=embed, view=LegalDisclaimerView(self.lang, "ULTRA"), ephemeral=True)

# ==========================================================
# CLASSE DE SUPORTE APENAS PARA MANTER AS SUAS ROTAS VERDES VIVAS
# ==========================================================
class RegistrationModal(discord.ui.Modal):
    def __init__(self, lang, plano_escolhido):
        texts = UI_STRINGS[lang]
        super().__init__(title=texts['modal_title'])
        self.lang = lang
        self.plano_escolhido = plano_escolhido
        self.backend_url = os.getenv('BACKEND_URL')

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        plat = "web_flow"
        token_val = "web_token"
        discord_id = str(interaction.user.id)

        try:
            Payload = {
                "discord_id": discord_id,
                "plano_escolhido": self.plano_escolhido,
                "plataforma": plat,
                "api_token": token_val
            }
            Resp = requests.post(f"{self.backend_url}/users/set-plan", json=Payload)
            
            if Resp.status_code == 200:
                requests.post(f"{self.backend_url}/user/accept-disclaimer", json={"discord_id": discord_id})
                await interaction.followup.send(UI_STRINGS[self.lang]['success'], ephemeral=True)
                await self.trigger_live_panel(interaction.user, discord_id)
            else:
                await interaction.followup.send("❌ Erro interno do servidor Go ao processar o plano.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erro de conexão com o backend: {e}", ephemeral=True)

    async def trigger_live_panel(self, user, discord_id):
        """Inicia a telemetria com os botões de rigs automaticamente após o cadastro"""
        try:
            Resp = requests.get(f"{self.backend_url}/internal/check-plan?discord_id={discord_id}")
            if Resp.status_code == 200:
                data = Resp.json()
                rigs_reais = data.get("rigs", [])
                from rig_selector import RigSelectorView, RigSelector
                Dm_msg = await user.send("📝 Cadastro finalizado! Clique no botão abaixo para ativar a telemetria ao vivo:")
                client_bot = user.mutual_guilds[0].me.bot if user.mutual_guilds else None
                if client_bot:
                    Cog = client_bot.get_cog("RigSelector")
                    if Cog:
                        View = RigSelectorView(rigs_reais, Cog, user.id)
                        await Dm_msg.edit(content="🖥️ Escolha a sua forma de monitoramento por botões:", view=View)
        except Exception as e:
            print(f"Erro ao disparar painel automático: {e}")

# ==========================================
# COG PRINCIPAL DE BOAS-VINDAS
# ==========================================
class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        locale = str(member.locale).lower()
        lang = locale if locale in UI_STRINGS else 'en-us'
        
        embed = discord.Embed(
            title=UI_STRINGS[lang]['welcome'],
            description=UI_STRINGS[lang]['desc'],
            color=0x00ffff
        )
        try:
            await member.send(embed=embed, view=MainView(member.locale))
        except discord.Forbidden:
            print(f"Não pude mandar DM para o usuário {member.id}")

async def setup(bot):
    await bot.add_cog(Welcome(bot))
