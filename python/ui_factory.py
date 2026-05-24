import discord
import config

class UI:
    @staticmethod
    def welcome_embed():
        embed = discord.Embed(
            title="⚡ Mining Guardian Elite",
            description="Sistema de monitoramento profissional para sua farm.",
            color=config.COLOR
        )
        return embed
