from discord.ui import View, Button
from discord import ButtonStyle, Interaction
from discord_tools.embeds import genshinCharacterEmbed, genshinWeaponEmbed

class CharWeaponView(View):
    """_summary_: Abstract Class that contains the common functionality for the CharacterView and WeaponView"""

    def __init__ (self, character, weapon):
        self.character = character
        self.weapon = weapon
        super().__init__()
        self.add_buttons()

    def add_buttons():
        """_summary_: Adds buttons to the view
        """
        pass


class WeaponView(CharWeaponView):        

    def add_buttons(self):
        button = Button(label=f'Weapon: {self.weapon["name"]}', style=ButtonStyle.primary, custom_id="weapon")
        button.callback = self.get_weapon
        self.add_item(button)

    async def get_weapon(self, interaction: Interaction):
        embed = genshinWeaponEmbed(self.weapon)
        await interaction.response.edit_message(embed=embed, view=CharacterView(self.character, self.weapon))


class CharacterView(CharWeaponView):
    
    def add_buttons(self):
        button = Button(label=f'Character: {self.character["name"]}', style=ButtonStyle.primary, custom_id="weapon")
        button.callback = self.get_character
        self.add_item(button)

    async def get_character(self, interaction: Interaction):
        embed = genshinCharacterEmbed(self.character)
        await interaction.response.edit_message(embed=embed, view=WeaponView(self.character, self.weapon))