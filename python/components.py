import discord
from ui_modals import TermsModal

class WelcomeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(self.PlanSelect())

    class PlanSelect(discord.ui.Select):
        def __init__(self):
            options = [
                discord.SelectOption(label="Plano Free", value="free", emoji="🥉"),
                discord.SelectOption(label="Plano Pro", value="pro", emoji="🥈"),
                discord.SelectOption(label="Plano Ultra", value="ultra", emoji="🥇")
            ]
            super().__init__(placeholder="Selecione seu plano...", options=options)

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.send_modal(TermsModal())
