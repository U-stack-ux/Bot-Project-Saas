import discord
import aiohttp
from config import BACKEND_URL

class RegistroModal(discord.ui.Modal, title="Vincular HiveOS"):
    farm_id = discord.ui.TextInput(label="Farm ID", placeholder="ID da sua Farm", required=True)
    token = discord.ui.TextInput(label="Token HiveOS", placeholder="Seu Personal Access Token", style=discord.TextStyle.long, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        payload = {
            "discord_id": str(interaction.user.id),
            "token": self.token.value,
            "farm_id": self.farm_id.value
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BACKEND_URL}/registrar", json=payload) as resp:
                if resp.status == 200:
                    await interaction.followup.send("✅ Conta vinculada com sucesso!", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Erro ao salvar dados no Backend.", ephemeral=True)

class BotaoRegistro(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Configurar HiveOS", style=discord.ButtonStyle.green, emoji="🔑")
    async def vincular(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RegistroModal())
