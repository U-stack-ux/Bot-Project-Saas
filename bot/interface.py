import discord
import aiohttp

class RigView(discord.ui.View):
    def __init__(self, user_id, plan):
        super().__init__()
        self.user_id = user_id
        self.plan = plan

    async def call_go(self, command, rig_id):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post("http://localhost:8080/api/cmd", json={"cmd": command, "rig": rig_id}, timeout=5) as resp:
                    return await resp.json()
            except:
                return {"error": "Serviço indisponível"}

    @discord.ui.button(label="Desligar Rig", style=discord.ButtonStyle.danger)
    async def btn_off(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Validação simples de plano antes de enviar ao Go
        if self.plan == "Free":
            await interaction.response.send_message("❌ Plano Free não permite esta ação.", ephemeral=True)
            return
        
        res = await self.call_go("shutdown", "rig123")
        await interaction.response.send_message(f"Resposta: {res}", ephemeral=True)
