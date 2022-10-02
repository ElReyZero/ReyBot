from discord.ui import View, Button, Select
from discord import ButtonStyle, Interaction, SelectOption
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

class AllCharactersView(View):

    def __init__(self, characters, extra_options=[]):
        super().__init__()
        self.characters = characters
        self.characters.sort(key=lambda x: x["name"])
        self.options = list()
        for character in characters:
            self.options.append(SelectOption(label=character["name"]))

        moreOption = SelectOption(label="More...")
        if len(extra_options) > 0 and len(extra_options) != 24:
            self.extra_options = self.options[:24]
            self.options=extra_options
            if moreOption not in self.extra_options:
                self.options.append(moreOption)
        elif len(self.options) > 25:
            self.extra_options = self.options[24:]
            self.options = self.options[:24]
            if moreOption not in self.options:
                self.options.append(moreOption)
                
        select = Select(placeholder="Select a character", options=self.options, custom_id="character_select")
        select.callback = self.get_character
        self.add_item(select)

    async def get_character(self, interaction: Interaction):
        if interaction.data["values"][0] == "More...":
            select = Select(placeholder="Select a character", options=self.extra_options, custom_id="character_select")
            select.callback = self.get_character
            await interaction.response.edit_message(view=AllCharactersView(self.characters, extra_options=self.extra_options))
            return
        for character in self.characters:
            if character["name"] == interaction.data["values"][0]:
                break
        embed = genshinCharacterEmbed(character)
        await interaction.response.edit_message(embed=embed, view=AllCharactersView(self.characters))

