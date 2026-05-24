import discord

class TermsModal(discord.ui.Modal, title='Aceite de Termos - SaaS'):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.TextInput(
            label="Digite 'CONCORDO' para iniciar",
            style=discord.TextStyle.short,
            required=True
        ))

    async def on_submit(self, interaction: discord.Interaction):
        # Aqui o backend será chamado via request para salvar o aceite
        await interaction.response.send_message("✅ Acesso liberado ao painel.", ephemeral=True)
