import discord

class NotificationManager:
    def __init__(self):
        # Dicionário para rastrear a última mensagem enviada para cada usuário
        # Estrutura: {user_id: message_object}
        self.last_messages = {}

    async def update_status(self, user, embed, is_emergency=False):
        """
        Atualiza o status na DM do usuário.
        - Se is_emergency=False: Edita a mensagem existente (não apita).
        - Se is_emergency=True: Envia uma nova mensagem (apita).
        """
        user_id = user.id
        
        # Se for emergência ou não houver mensagem anterior, enviamos uma nova
        if is_emergency or user_id not in self.last_messages:
            # Envia nova e armazena a referência
            new_msg = await user.send(embed=embed)
            self.last_messages[user_id] = new_msg
        else:
            # Apenas edita a mensagem anterior (silencioso)
            try:
                msg = self.last_messages[user_id]
                await msg.edit(embed=embed)
            except discord.NotFound:
                # Se a mensagem foi deletada pelo usuário, enviamos uma nova
                new_msg = await user.send(embed=embed)
                self.last_messages[user_id] = new_msg

