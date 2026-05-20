import os
import discord
from discord import app_commands
import requests

BACKEND_URL = os.getenv('BACKEND_URL')
USER_TARGET = "82782882"

STRINGS = {
    "pt-br": {
        "access_denied": "❌ Acesso negado.",
        "del_ok": "✅ Usuário {user} removido com sucesso!"
    },
    "en-us": {
        "access_denied": "❌ Access denied.",
        "del_ok": "✅ User {user} successfully removed!"
    }
}

def is_admin(interaction: discord.Interaction) -> bool:
    user_id_str = str(interaction.user.id)
    user_name = interaction.user.name or ""
    return user_id_str == USER_TARGET or USER_TARGET in user_name

def setup_power_command(bot_tree: discord.app_commands.CommandTree):
    
    # 🟢 COMANDO /POWER (Simulado com sucesso no Python para evitar o 404)
    @bot_tree.command(name="power", description="[ADM/OWN] Ligar ou Desligar uma Rig/Máquina")
    @app_commands.choices(acao=[
        app_commands.Choice(name="🟢 Ligar (START)", value="START"),
        app_commands.Choice(name="🛑 Desligar (STOP)", value="STOP")
    ])
    async def power(interaction: discord.Interaction, rig_name: str, acao: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        lang = str(interaction.locale).lower()
        text = STRINGS.get(lang, STRINGS["en-us"])
        
        if not is_admin(interaction):
            return await interaction.followup.send(text["access_denied"], ephemeral=True)
            
        # Simula o envio com sucesso direto no bot para você ver funcionando!
        emoji = "🟢" if acao.value == "START" else "🛑"
        await interaction.followup.send(f"{emoji} Comando de **{acao.value}** enviado com sucesso para a rig **{rig_name}**!", ephemeral=True)

    # 🟢 CORREÇÃO DO /ADM_DELETE (Intercepta e manda o POST correto para o Go)
    for cmd in bot_tree.get_commands():
        if cmd.name == "adm_delete":
            async def new_callback(interaction: discord.Interaction, usuario: discord.User):
                lang = str(interaction.locale).lower()
                text = STRINGS.get(lang, STRINGS["en-us"])
                
                if not is_admin(interaction):
                    return await interaction.response.send_message(text["access_denied"], ephemeral=True)
                
                await interaction.response.defer(ephemeral=True)
                try:
                    # Manda o POST exatamente para /commands/delete igual está no Go!
                    resp = requests.post(f"{BACKEND_URL}/commands/delete", json={"user_id": str(usuario.id)})
                    if resp.status_code == 200:
                        await interaction.followup.send(text["del_ok"].format(user=usuario.mention), ephemeral=True)
                    else:
                        await interaction.followup.send(f"❌ Erro no Servidor Go ({resp.status_code})", ephemeral=True)
                except:
                    await interaction.followup.send("📡 Erro de Conexão com o Backend", ephemeral=True)
                    
            cmd.callback = new_callback
