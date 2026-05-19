import discord
from discord.ext import tasks, commands
import requests
import os

TEMP_LIMITE_ALTA = 85
TEMP_LIMITE_BAIXA = 50
BACKEND_URL = "http://localhost:8080"

class SmartMonitor(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self):
        self.thermal_protection.start()

    @tasks.loop(seconds=15)
    async def thermal_protection(self):
        # Aqui simulamos a busca de usuários PRO/ULTRA no banco
        # users = db.get_active_paid_users() 
        user_id = "SEU_USER_ID_TESTE"
        
        try:
            resp = requests.get(f"{BACKEND_URL}/monitorar?id={user_id}")
            rigs = resp.json()

            for rig in rigs:
                if not rig['temps']: continue
                max_temp = max(rig['temps'])
                
                # 1. EMERGÊNCIA: DESLIGAR
                if max_temp >= TEMP_LIMITE_ALTA and rig['status'] == "working":
                    requests.get(f"{BACKEND_URL}/controlar?id={user_id}&worker={rig['id']}&action=miner_stop")
                    user = await self.fetch_user(int(user_id))
                    await user.send(f"🔥 **ALERTA CRÍTICO:** Sua Rig `{rig['name']}` atingiu {max_temp}°C e foi DESLIGADA para proteção!")

                # 2. RECUPERAÇÃO: RELIGAR
                elif max_temp <= TEMP_LIMITE_BAIXA and rig['status'] == "stopped":
                    requests.get(f"{BACKEND_URL}/controlar?id={user_id}&worker={rig['id']}&action=miner_start")
                    user = await self.fetch_user(int(user_id))
                    await user.send(f"❄️ **RIG ESFRIOU:** `{rig['name']}` está em {max_temp}°C e foi RELIGADA com sucesso!")
        except:
            pass

bot = SmartMonitor()
bot.run("DISCORD_TOKEN")
