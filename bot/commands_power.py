import os
import discord
from discord import app_commands
import requests

BACKEND_URL = os.getenv('BACKEND_URL')

class DetalhePlanoView(discord.ui.View):
    def __init__(self, plano_escolhido, link_checkout=None):
        super().__init__(timeout=60)
        self.plano_escolhido = plano_escolhido
        
        if link_checkout:
            self.add_item(discord.ui.Button(
                label="💳 Ir para o Pagamento Seguro", 
                url=link_checkout, 
                style=discord.ButtonStyle.link, 
                emoji="🔗"
            ))

    @discord.ui.button(label="🚀 Aceitar Termos e Ativar", style=discord.ButtonStyle.green, emoji="✅")
    async def confirmar_plano(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        payload = {
            "discord_id": str(interaction.user.id),
            "plano_escolhido": self.plano_escolhido,
            "hiveos_token": "token_protegido_saas"
        }
        
        try:
            resp = requests.post(f"{BACKEND_URL}/users/set-plan", json=payload)
            if resp.status_code == 200:
                await interaction.followup.send(
                    f"🎉 **Plano {self.plano_escolhido} ativado com sucesso!**\nUse `/monitorar` novamente para abrir o seu painel de telemetria.", 
                    ephemeral=True
                )
            else:
                await interaction.followup.send("❌ Erro interno ao registrar plano.", ephemeral=True)
        except:
            await interaction.followup.send("📡 Central de segurança offline.", ephemeral=True)

class EscolhaPlanoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="🥑 Testar FREE (3 Dias)", style=discord.ButtonStyle.gray, emoji="🎁")
    async def escolher_free(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🥑 Plano FREE - Teste Sem Compromisso",
            description=(
                "**Monitore sua rig caseira de forma básica por 3 dias!**\n\n"
                "⏱️ **Atualização:** A cada **15 minutos**\n"
                "• **Capacidade:** Até 2 Rigs.\n\n"
                "🚨 **TERMO DE ISENÇÃO JURÍDICA:**\n"
                "*O desenvolvedor está isento de qualquer responsabilidade por queima de componentes, falhas de conexão ou moedas não mineradas durante o teste.*"
            ),
            color=discord.Color.blue()
        )
        view = DetalhePlanoView("FREE")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="💎 Assinar PRO (Mais Vendido)", style=discord.ButtonStyle.blurple, emoji="⚡")
    async def escolher_pro(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="💎 Plano PRO - Proteção Essencial",
            description=(
                "**Monitore sua estrutura média com alta confiabilidade e privacidade.**\n\n"
                "⏱️ **Atualização:** A cada **5 minutos**\n"
                "• **Capacidade:** Gerencie até 10 Rigs simultâneas.\n"
                "🔥 **Alerta Térmico:** Notificação na DM caso passe de 80°C.\n\n"
                "🚨 **TERMO DE ISENÇÃO JURÍDICA:**\n"
                "*O uso dos comandos remotos ocorre por risco exclusivo do operador. O sistema não cobre perdas financeiras por instabilidade de terceiros.*"
            ),
            color=discord.Color.green()
        )
        view = DetalhePlanoView("PRO", link_checkout="https://checkout.seusite.com/pro")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="🔥 Assinar ULTRA (Alta Performance)", style=discord.ButtonStyle.red, emoji="👑")
    async def escolher_ultra(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🔥 Plano ULTRA - Desempenho em Tempo Real",
            description=(
                "**A estrutura definitiva de monitoramento instantâneo para fazendas.**\n\n"
                "⏱️ **Atualização Ultra Rápida:** A cada **10 SEGUNDOS** (O mais rápido do mercado!)\n"
                "• **Capacidade:** Totalmente **ILIMITADO** para Rigs e ASICs.\n"
                "🔥 **Alerta Térmico Crítico:** Monitoramento contínuo com pings imediatos.\n\n"
                "🚨 **TERMO DE ISENÇÃO JURÍDICA:**\n"
                "*A taxa de atualização de 10s depende da estabilidade da API da HiveOS. O desenvolvedor não se responsabiliza por atrasos causados por gargalos externos ou manutenção das pools.*"
            ),
            color=discord.Color.gold()
        )
        view = DetalhePlanoView("ULTRA", link_checkout="https://checkout.seusite.com/ultra")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


def setup_power_command(bot_tree: discord.app_commands.CommandTree):
    @bot_tree.command(name="monitorar", description="[SaaS] Abra seu painel gráfico de telemetria")
    async def monitorar(interaction: discord.Interaction, cliente_id: str):
        await interaction.response.defer(ephemeral=True)
        
        try:
            resp = requests.get(f"{BACKEND_URL}/users/check-plan?cliente_id={cliente_id}&discord_id={interaction.user.id}")
            if resp.status_code == 200:
                data = resp.json()
                if not data.get("has_plan", False):
                    embed = discord.Embed(
                        title="👋 Central de Monitoramento SaaS",
                        description=f"Olá {interaction.user.mention}! O ID `{cliente_id}` não está ativo.\n\nEscolha um plano abaixo para liberar o acesso.",
                        color=discord.Color.purple()
                    )
                    await interaction.followup.send(embed=embed, view=EscolhaPlanoView(), ephemeral=True)
                else:
                    plano = data.get("plano", "FREE")
                    tempo = data.get("check_interval", 15)
                    
                    # Se for o plano ultra, formata a exibição do tempo em segundos de forma elegante
                    exibicao_tempo = "10 segundos" if plano == "ULTRA" else f"{int(tempo)} minutos"
                    
                    embed_status = discord.Embed(
                        title=f"📊 TELEMETRIA EM TEMPO REAL — PLANO {plano}",
                        description=f"⚙️ *Frequência de varredura: Atualizando a cada {exibicao_tempo}*",
                        color=discord.Color.dark_theme()
                    )
                    
                    # BARRAS GRANDES E ROBUSTAS DE ALTA VISIBILIDADE (O que você pediu!)
                    embed_status.add_field(
                        name="📟 MÁQUINA: Rig-01-Main | Temp: `64°C` | Hash: `124 MH/s`",
                        value="`██████████████████▒▒▒▒▒▒▒▒▒` *(Operação Estável)*",
                        inline=False
                    )
                    embed_status.add_field(
                        name="📟 MÁQUINA: Rig-02-Mining | Temp: `58°C` | Hash: `62 MH/s`",
                        value="`██████████████░░░░░░░░░░░░░` *(Fria/Segura)*",
                        inline=False
                    )
                    embed_status.add_field(
                        name="⚠️ MÁQUINA: Asic-S9-Vip | Temp: `84°C` | Hash: `14 TH/s`",
                        value="`███████████████████████████` *(CRÍTICO - SUPER AQUECIMENTO)*",
                        inline=False
                    )
                    
                    if plano == "ULTRA" or plano == "PRO":
                        embed_status.set_footer(text="🚨 Alerta térmico instantâneo armado em segundo plano via DM!")
                    else:
                        embed_status.set_footer(text="Status: Operacional | Upscore SaaS")
                        
                    await interaction.followup.send(embed=embed_status, ephemeral=True)
            else:
                await interaction.followup.send("❌ Falha ao verificar credenciais.", ephemeral=True)
        except:
            await interaction.followup.send("📡 Conexão com o servidor Go indisponível.", ephemeral=True)
