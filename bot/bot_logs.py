@bot.tree.command(name="logs", description="Ver histórico de proteção térmica da sua conta")
async def logs(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    
    try:
        resp = requests.get(f"{BACKEND_URL}/logs?id={interaction.user.id}")
        logs = resp.json()
        
        if not logs:
            await interaction.followup.send("📭 Nenhum log de atividade registrado até o momento.", ephemeral=True)
            return

        embed = discord.Embed(title="📜 Histórico de Proteção UpScore", color=0x3498db)
        
        for item in logs:
            icon = "🛑 STOP" if item['action'] == "STOP" else "✅ START"
            dt = item['timestamp'][:16].replace("T", " ")
            embed.add_field(
                name=f"{icon} | {item['rig_name']}",
                value=f"Motivo: `{item['details']}`\nData: `{dt}`",
                inline=False
            )
            
        await interaction.followup.send(embed=embed, ephemeral=True)
    except:
        await interaction.followup.send("❌ Erro ao buscar logs no servidor.", ephemeral=True)
