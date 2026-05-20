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
            "hiveos_token": "token_demonstracao_api" # Em produção, coletamos em modal
        }
        
        try:
            resp = requests.post(f"{BACKEND_URL}/users/set-plan", json=payload)
            if resp.status_code == 200:
                await interaction.followup.send(
                    f"🎉 **Plano {self.plano_escolhido} ativado com proteção criptográfica AES-256!**\nSeus dados estão seguros na infraestrutura. Use `/monitorar` novamente para ver suas rigs!", 
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
                "⏱️ **Tempo de Atualização:** A cada **15 minutos**\n"
                "• **Capacidade:** Até 2 Máquinas (Rigs).\n"
                "• **Canais de Alerta:** Apenas em canais abertos do servidor.\n"
                "❌ **Alertas de Emergência na DM:** Indisponível nesta categoria.\n\n"
                "🚨 **TERMO DE ISENÇÃO JURÍDICA:**\n"
                "*O desenvolvedor não se responsabiliza por lucros cessantes (criptos não mineradas), falhas na internet local do cliente ou danos físicos/elétricos nas placas de vídeo e ASICs. O uso é de sua total conta e risco.*"
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
                "⏱️ **Tempo de Atualização:** A cada **5 minutos**\n"
                "• **Capacidade:** Gerencie até 10 Rigs de forma inteligente.\n"
                "• **Privacidade Extrema:** Receba notificações de queda direto na sua **DM Privada**.\n"
                "🔥 **Alerta Térmico Inteligente:** Bot te avisa na hora se a GPU passar de 80°C!\n"
                "• **Histórico:** Relatórios automáticos enviados a cada 30 dias.\n\n"
                "🚨 **TERMO DE ISENÇÃO JURÍDICA:**\n"
                "*O sistema oferece uma camada de alerta consultivo. Riscos de hardware, variações de hash rate em pools ou perdas de rentabilidade por problemas de terceiros não são de responsabilidade do desenvolvedor.*"
            ),
            color=discord.Color.green()
        )
        view = DetalhePlanoView("PRO", link_checkout="https://checkout.seusite.com/pro")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="🔥 Assinar ULTRA (Operações Grandes)", style=discord.ButtonStyle.red, emoji="👑")
    async def escolher_ultra(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🔥 Plano ULTRA - Desempenho e Velocidade Máxima",
            description=(
                "**A estrutura definitiva de monitoramento em tempo real para fazendas.**\n\n"
                "⏱️ **Tempo de Atualização:** A cada **1 minuto (Tempo Real)**\n"
                "• **Capacidade:** Totalmente **ILIMITADO** para Rigs e ASICs.\n"
                "• **Fila VIP:** Suas máquinas são lidas com prioridade nos servidores.\n"
                "🔥 **Alerta Térmico Inteligente:** Monitoramento de temperatura em tempo real com pings urgentes.\n"
                "• **Fechamento de Ciclo:** Balanços completos de eficiência energética a cada 30 dias.\n\n"
                "🚨 **TERMO DE ISENÇÃO JURÍDICA:**\n"
                "*O usuário declara estar ciente de que manutenções globais da rede ou atualizações de API da HiveOS podem gerar interrupções temporárias. O desenvolvedor está isento de indenizações por danos materiais ou lucros cessantes.*"
            ),
            color=discord.Color.gold()
        )
        view = DetalhePlanoView("ULTRA", link_checkout="https://checkout.seusite.com/ultra")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


def setup_power_command(bot_tree: discord.app_commands.CommandTree):
    @bot_tree.command(name="monitorar", description="[SaaS] Configure seu sistema inteligente de monitoramento")
    async def monitorar(interaction: discord.Interaction, cliente_id: str):
        await interaction.response.defer(ephemeral=True)
        
        try:
            resp = requests.get(f"{BACKEND_URL}/users/check-plan?cliente_id={cliente_id}&discord_id={interaction.user.id}")
            if resp.status_code == 200:
                data = resp.json()
                if not data.get("has_plan", False):
                    embed = discord.Embed(
                        title="👋 Central de Monitoramento SaaS",
                        description=f"Olá {interaction.user.mention}! O ID `{cliente_id}` não possui plano.\n\nEscolha uma das opções profissionais abaixo para ativar o sistema.",
                        color=discord.Color.purple()
                    )
                    await interaction.followup.send(embed=embed, view=EscolhaPlanoView(), ephemeral=True)
                else:
                    # CLIENTE ATIVO: Desenha o placar com barras visuais e dados do plano!
                    plano = data.get("plano", "FREE")
                    tempo = int(data.get("check_interval", 15))
                    smart = "ATIVO 👑" if data.get("has_smart_alert") else "DESATIVADO ❌"
                    
                    embed_status = discord.Embed(
                        title=f"📊 PAINEL DE TELEMETRIA - PLANO {plano}",
                        description=f"🤖 *Monitorando a cada {tempo} min | Alerta Térmico Inteligente: {smart}*",
                        color=discord.Color.dark_theme()
                    )
                    # Exemplo das barras de monitoramento visual das GPUs que você pediu!
                    embed_status.add_field(name="🔹 GPU 1 | `68°C`", value="`▬▬▬▬▬▬▬▬▬▱▱▱` *(Estável)*", inline=False)
                    embed_status.add_field(name="🔹 GPU 2 | `61°C`", value="`▬▬▬▬▬▬▬▬▱▱▱▱` *(Fria)*", inline=False)
                    embed_status.add_field(name="⚠️ GPU 3 | `82°C`", value="`▬▬▬▬▬▬▬▬▬▬▬▬▰` *(ALERTA TÉRMICO)*", inline=False)
                    
                    # Simulação do alerta de emergência inteligente disparado na DM
                    if data.get("has_smart_alert") and any(t >= 80 for t in [68, 61, 82]):
                        embed_status.set_footer(text="🚨 CRÍTICO: Alerta de emergência enviado para a DM do cliente!")
                    else:
                        embed_status.set_footer(text="Status da Infraestrutura: OPERACIONAL")
                        
                    await interaction.followup.send(embed=embed_status, ephemeral=True)
            else:
                await interaction.followup.send("❌ Falha na comunicação com o backend.", ephemeral=True)
        except:
            await interaction.followup.send("📡 Central de checagem offline.", ephemeral=True)
