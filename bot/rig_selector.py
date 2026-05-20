import discord

class RigSelectorView(discord.ui.View):
    def __init__(self, rigs_list):
        super().__init__(timeout=180) # O menu expira em 3 minutos por segurança
        self.rigs_list = rigs_list

        # Botões para cada Rig
        for rig in rigs_list:
            self.add_item(discord.ui.Button(label=rig['name'], custom_id=f"rig_{rig['id']}"))
            
        # Botão especial para farm completa
        self.add_item(discord.ui.Button(label="Monitorar TODAS", style=discord.ButtonStyle.danger, custom_id="all_rigs"))

    @discord.ui.button(label="Aceitar Termos e Ativar", style=discord.ButtonStyle.primary, row=4)
    async def confirm_monitoring(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Aqui o bot envia o comando pro seu backend Go
        await interaction.response.send_message("✅ Termos aceitos. Monitoramento ativado!", ephemeral=True)
