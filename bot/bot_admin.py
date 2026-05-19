# Adicione isso ao seu bot.py existente ou crie um novo arquivo de comandos
import discord
import requests
import os

YOUR_ADMIN_ID = 82782882 # <-- SEU ID DO DISCORD AQUI
BACKEND_URL = os.getenv("BACKEND_URL")

@bot.tree.command(name="adm_delete", description="[ADMIN] Deletar usuário do banco de dados")
@app_commands.describe(user_id="O ID do Discord do usuário que deseja remover")
async def adm_delete(interaction: discord.Interaction, user_id: str):
    # Verificação de Segurança: Apenas VOCÊ pode usar
    if interaction.user.id != YOUR_ADMIN_ID:
        await interaction.response.send_message("❌ Você não tem permissão para usar este comando.", ephemeral=True)
        return

    # Confirmação antes de deletar
    class ConfirmDelete(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=30)
        
        @discord.ui.button(label="Confirmar Exclusão", style=discord.ButtonStyle.danger)
        async def confirm(self, i: discord.Interaction, button: discord.ui.Button):
            try:
                # Chamada para a nova rota de exclusão no Go
                resp = requests.delete(f"{BACKEND_URL}/admin/delete?id={user_id}")
                if resp.status_code == 200:
                    await i.response.send_message(f"✅ Usuário `{user_id}` removido com sucesso do banco de dados.", ephemeral=True)
                else:
                    await i.response.send_message("❌ Erro ao deletar no backend.", ephemeral=True)
            except:
                await i.response.send_message("📡 Erro de conexão com o servidor Go.", ephemeral=True)
            self.stop()

    await interaction.response.send_message(f"⚠️ Tem certeza que deseja deletar os dados do usuário `{user_id}`? Esta ação é irreversível.", view=ConfirmDelete(), ephemeral=True)
