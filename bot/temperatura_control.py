import discord

# ========================================================
# PAINEL DE TEMPERATURA INTELLIGENT - VERSÃO ULTRA e PRO
# ========================================================

class UltraTemperatureView(discord.ui.View):
    def __init__(self, current_min=30, current_max=95):
        super().__init__(timeout=None)
        self.min_temp = current_min
        self.max_temp = current_max
        self.update_buttons()

    def update_buttons(self):
        """Atualiza o texto dos visores digitais no meio das setas"""
        # Limpa os itens antigos para renderizar os novos valores atualizados
        self.clear_items()

        # --- LINHA DO MÍNIMO ---
        btn_min_down = discord.ui.Button(label="⬅️ Min", style=discord.ButtonStyle.blurple, row=0)
        btn_min_down.callback = self.decrease_min
        
        btn_min_val = discord.ui.Button(label=f" {self.min_temp}°C ", style=discord.ButtonStyle.secondary, disabled=True, row=0)
        
        btn_min_up = discord.ui.Button(label="Min ➡️", style=discord.ButtonStyle.blurple, row=0)
        btn_min_up.callback = self.increase_min

        # --- LINHA DO MÁXIMO ---
        btn_max_down = discord.ui.Button(label="⬅️ Max", style=discord.ButtonStyle.danger, row=1)
        btn_max_down.callback = self.decrease_max
        
        btn_max_val = discord.ui.Button(label=f" {self.max_temp}°C ", style=discord.ButtonStyle.secondary, disabled=True, row=1)
        
        btn_max_up = discord.ui.Button(label="Max ➡️", style=discord.ButtonStyle.danger, row=1)
        btn_max_up.callback = self.increase_max

        # --- BOTÃO SALVAR (LINHA 2) ---
        btn_save = discord.ui.Button(label="💾 Salvar e Ativar Proteção", style=discord.ButtonStyle.green, row=2)
        btn_save.callback = self.save_config

        # Adiciona todos os componentes na ordem certa
        self.add_item(btn_min_down)
        self.add_item(btn_min_val)
        self.add_item(btn_min_up)
        
        self.add_item(btn_max_down)
        self.add_item(btn_max_val)
        self.add_item(btn_max_up)
        
        self.add_item(btn_save)

    async def decrease_min(self, interaction: discord.Interaction):
        if self.min_temp > 0: # Limite mínimo físico para não ficar negativo
            self.min_temp -= 5
        self.update_buttons()
        await interaction.response.edit_message(view=self)

    async def increase_min(self, interaction: discord.Interaction):
        if self.min_temp < self.max_temp - 5: # Impede o mínimo de passar ou encostar no máximo
            self.min_temp += 5
        self.update_buttons()
        await interaction.response.edit_message(view=self)

    async def decrease_max(self, interaction: discord.Interaction):
        if self.max_temp > self.min_temp + 5: # Impede o máximo de ficar menor que o mínimo
            self.max_temp -= 5
        self.update_buttons()
        await interaction.response.edit_message(view=self)

    async def increase_max(self, interaction: discord.Interaction):
        if self.max_temp < 110: # Limite máximo seguro para as GPUs
            self.max_temp += 5
        self.update_buttons()
        await interaction.response.edit_message(view=self)

    async def save_config(self, interaction: discord.Interaction):
        # Aqui no futuro faremos o envio para o seu backend no Render
        await interaction.response.send_message(
            f"✅ **Configuração ULTRA Ativada!**\nSua rig desligará em {self.max_temp}°C e só voltará a ligar ao atingir {self.min_temp}°C.", 
            ephemeral=True
        )


class ProTemperatureView(discord.ui.View):
    """Versão do plano PRO: Apenas define o limite máximo de corte"""
    def __init__(self, current_max=95):
        super().__init__(timeout=None)
        self.max_temp = current_max
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()

        btn_max_down = discord.ui.Button(label="⬅️ Max", style=discord.ButtonStyle.danger, row=0)
        btn_max_down.callback = self.decrease_max
        
        btn_max_val = discord.ui.Button(label=f" {self.max_temp}°C ", style=discord.ButtonStyle.secondary, disabled=True, row=0)
        
        btn_max_up = discord.ui.Button(label="Max ➡️", style=discord.ButtonStyle.danger, row=0)
        btn_max_up.callback = self.increase_max

        btn_save = discord.ui.Button(label="💾 Salvar Limite", style=discord.ButtonStyle.green, row=1)
        btn_save.callback = self.save_config

        self.add_item(btn_max_down)
        self.add_item(btn_max_val)
        self.add_item(btn_max_up)
        self.add_item(btn_save)

    async def decrease_max(self, interaction: discord.Interaction):
        if self.max_temp > 40:
            self.max_temp -= 5
        self.update_buttons()
        await interaction.response.edit_message(view=self)

    async def increase_max(self, interaction: discord.Interaction):
        if self.max_temp < 110:
            self.max_temp += 5
        self.update_buttons()
        await interaction.response.edit_message(view=self)

    async def save_config(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"✅ **Configuração PRO Ativada!**\nSua rig será desligada caso atinja {self.max_temp}°C.", 
            ephemeral=True
        )
