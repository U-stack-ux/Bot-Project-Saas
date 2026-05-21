import discord
from discord.ext import commands
import requests
import os
import asyncio

UI_STRINGS = {
    'pt-br': {
        'welcome': "Bem-vindo ao UpscoreSaaS",
        'desc': "Otimize sua mineração com IA em tempo real.",
        'legal': "⚠️ **AVISO LEGAL:** Não nos responsabilizamos por instabilidades ou erros de dados vindos diretamente das APIs de terceiros (HiveOS/NiceHash).",
        'btn_free': "🚀 Teste Grátis",
        'btn_paid': "💎 Planos Pagos",
        'btn_accept': "🤝 Aceitar Termos e Continuar",
        'modal_title': "Cadastro de API de Mineração",
        'modal_plat': "Plataforma (hiveos ou nicehash)",
        'modal_token': "Insira seu Token / API Key",
        'success': "✅ Conta configurada com sucesso!"
    },
    'es-es': {
        'welcome': "Bienvenido a UpscoreSaaS",
        'desc': "Otimize su minería con IA en tiempo real.",
        'legal': "⚠️ **AVISO LEGAL:** No nos responsabilizamos por fallas o demoras provenientes de las APIs de terceros (HiveOS/NiceHash).",
        'btn_free': "🚀 Prueba Gratis",
        'btn_paid': "💎 Planes Pagos",
        'btn_accept': "🤝 Aceptar Términos y Continuar",
        'modal_title': "Registro de API de Minería",
        'modal_plat': "Plataforma (hiveos o nicehash)",
        'modal_token': "Inserte su Token / API Key",
        'success': "✅ ¡Cuenta configurada con éxito!"
    },
    'en-us': {
        'welcome': "Welcome to UpscoreSaaS",
        'desc': "Optimize your mining with real-time AI.",
        'legal': "⚠️ **LEGAL DISCLAIMER:** We are not responsible for outages or telemetry errors from third-party APIs (HiveOS/NiceHash).",
        'btn_free': "🚀 Free Trial",
        'btn_paid': "💎 Paid Plans",
        'btn_accept': "🤝 Accept Terms & Continue",
        'modal_title': "Mining API Registration",
        'modal_plat': "Platform (hiveos or nicehash)",
        'modal_token': "Enter your Token / API Key",
        'success': "✅ Account configured successfully!"
    }
}

# ---------------------------------------------------------------------------
# JANELA POP-UP (MODAL) PARA COLETAR OS DADOS SEM DIGITAR COMANDO
# ---------------------------------------------------------------------------
class RegistrationModal(discord.ui.Modal):
    def __init__(self, lang, plano_escolhido):
        texts = UI_STRINGS[lang]
        super().__init__(title=texts['modal_title'])
        self.lang = lang
        self.plano = plano_escolhido
        self.backend_url = os.Getenv('BACKEND_URL')

        self.plataforma = discord.ui.TextInput(
            Label=texts['modal_plat'],
            Placeholder="hiveos / nicehash",
            Min_length=6,
            Max_length=8,
            Required=True
        )
        self.token = discord.ui.TextInput(
            Label=texts['modal_token'],
            Style=discord.TextStyle.long,
            Placeholder="Cole aqui seu Token de Acesso...",
            Required=True
        )
        self.add_item(self.plataforma)
        self.add_item(self.token)

    Async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        plat = self.plataforma.value.strip().lower()
        token_val = self.token.value.strip()
        discord_id = str(interaction.user.id)

        If plat not in ['hiveos', 'nicehash']:
            await interaction.followup.send("❌ Plataforma inválida! Use apenas 'hiveos' ou 'nicehash'.", ephemeral=True)
            Return

        # Envia diretamente para o banco de dados através do Go backend
        Try:
            Payload = {
                "discord_id": discord_id,
                "plano_escolhido": self.plano,
                "plataforma": plat,
                "api_token": token_val
            }
            Resp = requests.post(f"{self.backend_url}/users/set-plan", json=payload)
            
            If resp.status_code == 200:
                # Chama o Termo de Consentimento automático após o cadastro
                Requests.post(f"{self.backend_url}/user/accept-disclaimer", json={"discord_id": discord_id})
                
                Await interaction.followup.send(UI_STRINGS[self.lang]['success'], ephemeral=True)
                
                # CHAMA O PAINEL DE RIGS DIRETAMENTE POR AQUI (FLUXO CONTÍNUO)
                Await self.trigger_live_panel(interaction.user, discord_id)
            Else:
                Await interaction.followup.send("❌ Erro interno do servidor Go ao processar o plano.", ephemeral=True)
        Except Exception as e:
            Await interaction.followup.send(f"❌ Erro de conexão com o backend: {e}", ephemeral=True)

    Async def trigger_live_panel(self, user, discord_id):
        """Inicia a telemetria com os botões de rigs automaticamente após o cadastro"""
        Try:
            Resp = requests.get(f"{self.backend_url}/internal/check-plan?discord_id={discord_id}")
            If resp.status_code == 200:
                Data = resp.json()
                Rigs_reais = data.get("rigs", [])
                
                # Importa dinamicamente a view que você tem no rig_selector.py
                From rig_selector import RigSelectorView, RigSelector
                
                # Envia o seletor das rigs por botões
                Dm_msg = await user.send("📋 Cadastro finalizado! Clique no botão abaixo para ativar a telemetria ao vivo:")
                
                # Pega a referência da Cog para gerenciar o loop
                Client_bot = user.mutual_guilds[0].me.bot if user.mutual_guilds else None
                If client_bot:
                    Cog = client_bot.get_cog("RigSelector")
                    If cog:
                        View = RigSelectorView(rigs_reais, cog, user.id)
                        Await dm_msg.edit(content="📋 Escolha a sua forma de monitoramento por botões:", view=view)
        Except Exception as e:
            Print(f"Erro ao disparar painel automático: {e}")

# ==========================================
# VIEW 2: TELA DO ACORDO LEGAL
# ==========================================
class LegalDisclaimerView(discord.ui.View):
    def __init__(self, lang, plano_escolhido):
        super().__init__(timeout=None)
        self.lang = lang
        self.plano_escolhido = plano_escolhido
        self.textis = UI_STRINGS[lang]
        
        # URL oficial do seu site hospedado no Render
        # Altere o texto abaixo pelo link real do seu app no Render
        url_site = "https://bot-project-saas.onrender.com"
        
        # Criando o botão do tipo LINK que abre o navegador automaticamente
        btn = discord.ui.Button(
            label=self.textis['btn_accept'], 
            style=discord.ButtonStyle.link, 
            url=url_site
        )
        self.add_item(btn)

# ---------------------------------------------------------------------------
# VIEW 1: TELA DE ENTRADA (ESCOLHA DE PLANOS)
# ---------------------------------------------------------------------------
class MainView(discord.ui.View):
    def __init__(self, locale):
        super().__init__(timeout=None)
        self.lang = locale if locale in UI_STRINGS else 'en-us'
        self.texts = UI_STRINGS[self.lang]
        
        Btn_free = discord.ui.Button(label=self.texts['btn_free'], style=discord.ButtonStyle.green, custom_id="flow_free")
        Btn_free.callback = self.choose_free
        self.add_item(btn_free)
        
        Btn_paid = discord.ui.Button(label=self.texts['btn_paid'], style=discord.ButtonStyle.blurple, custom_id="flow_paid")
        Btn_paid.callback = self.choose_paid
        self.add_item(btn_paid)

    Async def choose_free(self, interaction: discord.Interaction):
        Embed = discord.Embed(title="Termos de Uso - Teste Grátis", description=UI_STRINGS[self.lang]['legal'], color=0xff0000)
        Await interaction.response.send_message(embed=embed, view=LegalDisclaimerView(self.lang, "FREE"), ephemeral=True)

    Async def choose_paid(self, interaction: discord.Interaction):
        Embed = discord.Embed(title="Termos de Uso - Assinatura VIP", description=UI_STRINGS[self.lang]['legal'], color=0xff0000)
        Await interaction.response.send_message(embed=embed, view=LegalDisclaimerView(self.lang, "ULTRA"), ephemeral=True)

# ---------------------------------------------------------------------------
# COG PRINCIPAL DE BOAS-VINDAS
# ---------------------------------------------------------------------------
class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        Locale = str(member.locale).lower()
        Lang = locale if locale in UI_STRINGS else 'en-us'
        
        Embed = discord.Embed(
            Title=UI_STRINGS[lang]['welcome'], 
            Description=UI_STRINGS[lang]['desc'], 
            Color=0x00ffff
        )
        Try:
            Await member.send(embed=embed, view=MainView(locale))
        Except discord.Forbidden:
            Print(f"Não pude mandar DM para o usuário {member.id}")

async def setup(bot):
    Await bot.add_cog(Welcome(bot))

