import subprocess
from discord.ext import tasks

@tasks.loop(seconds=35)
async def executar_motor_go():
    try:
        # "../motor" diz para o script subir uma pasta e executar o binário que acabamos de compilar
        subprocess.run(["../motor"], check=True)
    except Exception as e:
        print(f"[TASK MANAGER] Alerta ao rodar motor Go: {e}")

def iniciar_tasks(bot):
    executar_motor_go.start()
