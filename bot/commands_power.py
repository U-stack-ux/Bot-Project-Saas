import os
import discord
from discord import app_commands
import requests

BACKEND_URL = os.getenv('BACKEND_URL')
USER_TARGET = "82782882"

STRINGS = {
    "pt-br": {"access_denied": "❌ Acesso negado."},
    "en-us": {"access_denied": "❌ Access denied."}
}

def is_admin(interaction: discord.Interaction) -> bool:
    """Função centralizada que aceita o ID numérico ou o seu Username do Discord"""
    user_id_str = str(interaction.user.id)
    user_name = interaction.user.name or ""
    # Se o ID bater ou se o seu username 'upscore82782882' tiver o número, libera
    return user_id_str == USER_TARGET or USER_TARGET in user_name

def setup_power_command(bot_tree: discord.app_commands.CommandTree):
    """Injeta o comando /power e corrige o comando /adm_delete por fora"""
    
    # --- O SUPER GATO ---
    # Pegamos o comando 'adm_delete' que já existe no bot.py e alteramos a checagem dele por aqui!
    existing_adm_cmd = bot_tree.get_command("adm_delete")
    if existing_adm_cmd:
        @existing_adm_cmd.error
        async def fallback_error(interaction, error):
            pass # Ignora erros padrões
            
    # ---------------------

    @bot_tree.command(name="power", description="[ADM/OWN] Ligar ou Desligar uma Rig/Máquina")
    @app_commands.choices(acao=[
        app_commands.Choice(name="🟢 Ligar (START)", value="START"),
        app_commands.Choice(name="🛑 Desligar (STOP)", value="STOP")
    ])
    async def power(interaction: discord.Interaction, rig_name: str, acao: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        lang = str(interaction.locale).lower()
        text = STRINGS.get(lang, STRINGS["en-us"])
        
        # Usa a nova checagem inteligente
        if not is_admin(interaction):
            return await interaction.followup.send(text["access_denied"], ephemeral=True)
            
        try:
            payload = {
                "user_id": str(interaction.user.id),
                "rig_name": rig_name,
                "action": acao.value,
                "details": f"Comando executado via Discord por {interaction.user.name}"
            }
            
            resp = requests.post(f"{BACKEND_URL}/admin/power", json=payload)
            
            if resp.status_code in [200, 201]:
                emoji = "🟢" if acao.value == "START" else "🛑"
                await interaction.followup.send(f"{emoji} Comando de **{acao.value}** enviado para a rig **{rig_name}**!", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ O servidor Go respondeu com erro ({resp.status_code}).", ephemeral=True)
                
        except Exception:
            await interaction.followup.send("📡 Erro de conexão: O backend Go parece estar offline.", ephemeral=True)

    # Cria uma cópia modificada do adm_delete original injetando o bypass de Admin
    # Assim, tanto faz o que está escrito no bot.py, esse arquivo aqui passa por cima!
    for cmd in bot_tree.get_commands():
        if cmd.name == "adm_delete":
            old_callback = cmd.callback
            async def new_callback(interaction: discord.Interaction, usuario: discord.User):
                if not is_admin(interaction):
                    lang = str(interaction.locale).lower()
                    text = STRINGS.get(lang, STRINGS["en-us"])
                    return await interaction.response.send_message(text["access_denied"], ephemeral=True)
                await old_callback(interaction, usuario)
            cmd.callback = new_callback
