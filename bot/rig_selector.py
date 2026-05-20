import discord
from discord.ext import commands
import requests
import os
import asyncio

class RigSelectorView(discord.ui.View):
    def __init__(self, rigs_list, bot_cog, user_id):
        super().__init__(timeout=180) # O menu expira em 3 minutos por segurança
        self.rigs_list = rigs_list
        self.bot_cog = bot_cog
        self.user_id = user_id

        # Botão para cada Rig dinâmica vinda da API
        for idx, rig in enumerate(self.rigs_list):
            nome_rig = rig.get('nome', rig.get('name', f"Rig-{idx+1}"))
            self.add_item(discord.ui.Button(
                label=nome_rig, 
                style=discord.ButtonStyle.secondary, 
                custom_id=f"rig_{idx}"
            ))

        # Botão especial para a farm completa
        self.add_item(discord.ui.Button(
            label="Monitorar TODAS", 
            style=discord.ButtonStyle.danger, 
            custom_id="all_rigs"
        ))

    @discord.ui.button(label="Confirmar e Ativar", style=discord.ButtonStyle.primary, row=4)
    async def confirm_monitoring(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        # Envia a mensagem base que será editada continuamente na DM
        try:
            dm_msg = await interaction.user.send("⏳ Iniciando painel dinâmico de telemetria...")
            await interaction.followup.send("✅ Monitoramento ativado! Verifique sua DM.", ephemeral=True)
            
            # Inicia o loop em segundo plano para este usuário específico
            self.bot_cog.start_live_updater(interaction.user, dm_msg)
        except discord.Forbidden:
            await interaction.followup.send("❌ Não consegui enviar DM. Ative as mensagens diretas nas configurações de privacidade do servidor.", ephemeral=True)

class RigSelector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backend_url = os.getenv('BACKEND_URL')
        self.active_tasks = {}

    @commands.hybrid_command(name="painel", description="Abre a seleção de Rigs e ativa o monitoramento em tempo real")
    async def painel(self, ctx):
        await ctx.defer(ephemeral=True)
        discord_id = str(ctx.author.id)

        # Busca dados iniciais das Rigs reais do usuário no Go backend
        try:
            resp = requests.get(f"{self.backend_url}/internal/check-plan?discord_id={discord_id}")
            if resp.status_code != 200:
                await ctx.followup.send("❌ Erro ao conectar ao servidor backend.", ephemeral=True)
                return

            data = resp.json()
            if not data.get("has_plan"):
                await ctx.followup.send("❌ Você não possui um plano ativo ou ele expirou.", ephemeral=True)
                return

            rigs_reais = data.get("rigs", [])
            
            # Invoca a View que você estruturou passando a lista real de Rigs
            view = RigSelectorView(rigs_reais, self, ctx.author.id)
            await ctx.followup.send("📋 Escolha suas Rigs para gerar o painel na DM:", view=view, ephemeral=True)

        except Exception as e:
            await ctx.followup.send(f"❌ Erro de conexão: {e}", ephemeral=True)

    def start_live_updater(self, user, message):
        discord_id = str(user.id)
        if discord_id in self.active_tasks:
            self.active_tasks[discord_id].cancel()
        
        task = self.bot.loop.create_task(self.live_updater_loop(user, message))
        self.active_tasks[discord_id] = task

    async def live_updater_loop(self, user, message):
        """O motor que edita a mensagem por segundos/minutos baseado no plano do Go"""
        discord_id = str(user.id)
        
        while not self.bot.is_closed():
            try:
                resp = requests.get(f"{self.backend_url}/internal/check-plan?discord_id={discord_id}")
                if resp.status_code != 200:
                    await message.edit(content="⚠️ Falha ao atualizar telemetria. Tentando novamente...")
                    await asyncio.sleep(30)
                    continue

                data = resp.json()
                if not data.get("has_plan"):
                    await message.edit(content="❌ Monitoramento encerrado: Seu plano expirou.")
                    break

                plano = data.get("plano", "FREE")
                plataforma = data.get("plataforma", "HIVEOS").upper()
                intervalo = data.get("check_interval", 60) # Puxa os 10s, 30s ou 60s automáticos do seu Go
                rigs = data.get("rigs", [])

                embed = discord.Embed(
                    title=f"📊 Painel de Telemetria Real ({plataforma})",
                    description=f"Plano: **{plano}** | Atualizando automaticamente a cada **{int(intervalo)}s**",
                    color=0x00ffff
                )

                for r in rigs:
                    embed.add_field(
                        name=f"🧱 {r.get('nome', 'Worker')}",
                        value=f"Status: `{r.get('status', 'N/A')}`\nTemp: `{r.get('temperatura', 0)}°C`\nHashrate: `{r.get('hashrate', '0 MH/s')}`",
                        inline=False
                    )

                embed.set_footer(text="Dados coletados diretamente da API oficial.")
                
                # Edita a mensagem na DM do usuário dinamicamente
                await message.edit(content="", embed=embed)
                
                # Dorme o tempo exato definido pelo plano do cliente
                await asyncio.sleep(float(intervalo))

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Erro no loop de {discord_id}: {e}")
                await asyncio.sleep(10)

async def setup(bot):
    await bot.add_cog(RigSelector(bot))
