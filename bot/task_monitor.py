import os
import discord
from discord.ext import tasks
import requests
import asyncio

BACKEND_URL = os.getenv('BACKEND_URL')

# ID do canal do Discord onde o placar fixo vai rodar (vamos configurar dinamicamente)
# Se você tiver um ID de canal específico, pode substituir aqui
CANAL_PLACAR_ID = None 
MENSAGEM_PLACAR_ID = None

@tasks.loop(minutes=5)
async def monitoramento_automatico_task(bot):
    global MENSAGEM_PLACAR_ID, CANAL_PLACAR_ID
    
    # Se ainda não foi configurado um canal, a tarefa espera o comando de ativação
    if not CANAL_PLACAR_ID:
        return

    canal = bot.get_channel(CANAL_PLACAR_ID)
    if not canal:
        return

    # 1. Busca os dados reais de monitoramento lá no seu Go (ou simulador temporário do Go)
    gpus_data = []
    try:
        # Quando tiver a rota real de telemetria no Go, mudamos para /metrics ou /status
        resp = requests.get(f"{BACKEND_URL}/")
        if resp.status_code == 200:
            # Dados de exemplo reais simulando o comportamento que o Go vai enviar
            gpus_data = [
                {"name": "GPU 1 ❄️", "temp": "68°C", "bar": "▬▬▬▬▬▬▬▬▬▱▱▱"},
                {"name": "GPU 2 ❄️", "temp": "61°C", "bar": "▬▬▬▬▬▬▬▬▱▱▱▱"},
                {"name": "GPU 3 ❄️", "temp": "69°C", "bar": "▬▬▬▬▬▬▬▬▬▱▱▱"}
            ]
    except:
        # Se o backend falhar, avisa no painel para você saber na hora
        gpus_data = [{"name": "⚠️ Erro de Conexão", "temp": "API OFF", "bar": "❌"}]

    # 2. Monta o visual moderno do Placar (Embed)
    embed = discord.Embed(
        title="📊 PAINEL DE MONITORAMENTO SUCESSO (SaaS)",
        description="*Atualizado automaticamente a cada 5 minutos de forma ilimitada.*\n",
        color=discord.Color.dark_theme()
    )
    
    for gpu in gpus_data:
        embed.add_field(
            name=f"🔹 {gpu['name']} | `{gpu['temp']}`",
            value=f"`{gpu['bar']}`",
            inline=False
        )
        
    embed.set_footer(text="Status da Infraestrutura: ONLINE | Upscore SaaS")

    # 3. Gerencia o envio ou a edição da mensagem fixa
    try:
        if MENSAGEM_PLACAR_ID is None:
            # Primeira vez: envia a mensagem e salva o ID dela
            msg = await canal.send(embed=embed)
            MENSAGEM_PLACAR_ID = msg.id
        else:
            # Vezes seguintes: apenas edita a mensagem existente sem poluir o chat
            msg = await canal.fetch_message(MENSAGEM_PLACAR_ID)
            await msg.edit(embed=embed)
    except Exception as e:
        # Se alguém deletar a mensagem manualmente, ele recria na próxima volta
        MENSAGEM_PLACAR_ID = None

def iniciar_monitor(bot, canal_id):
    global CANAL_PLACAR_ID
    CANAL_PLACAR_ID = int(canal_id)
    if not monitoramento_automatico_task.is_running():
        monitoramento_automatico_task.start(bot)
