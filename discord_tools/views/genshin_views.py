#pylint: disable=arguments-differ, no-method-argument, too-many-function-args
from discord.ui import View, Button, Select
from discord import ButtonStyle, Interaction, SelectOption
from discord_tools.embeds import genshin_character_embed, genshin_weapon_embed


class CharWeaponView(View):
    """_summary_: Abstract Class that contains the common functionality for the CharacterView and WeaponView"""

    def __init__(self, character, weapon):
        self.character = character
        self.weapon = weapon
        super().__init__()
        self.add_buttons()

    def add_buttons():
        """_summary_: Adds buttons to the view
        """


class WeaponView(CharWeaponView):

    def add_buttons(self):
        button = Button(label=f'Weapon: {self.weapon.name}', style=ButtonStyle.primary, custom_id="weapon")
        button.callback = self.get_weapon
        self.add_item(button)

    async def get_weapon(self, interaction: Interaction):
        embed = genshin_weapon_embed(self.weapon)
        await interaction.response.edit_message(embed=embed, view=CharacterView(self.character, self.weapon))


class CharacterView(CharWeaponView):

    def add_buttons(self):
        button = Button(label=f'Character: {self.character.name}', style=ButtonStyle.primary, custom_id="weapon")
        button.callback = self.get_character
        self.add_item(button)

    async def get_character(self, interaction: Interaction):
        embed = genshin_character_embed(self.character)
        await interaction.response.edit_message(embed=embed, view=WeaponView(self.character, self.weapon))


class AllCharactersView(View):

    def __init__(self, characters):
        super().__init__()

        self.characters = characters
        self.characters.sort(key=lambda x: x.name)
        self.per_page = 23
        self.current_page = 0
        self.options = []

        self.update_options()

    def update_options(self):
        start_idx = self.current_page * self.per_page
        end_idx = (self.current_page + 1) * self.per_page

        self.options = [SelectOption(label=character.name) for character in self.characters[start_idx:end_idx]]

        more_option = SelectOption(label="More...")

        if len(self.characters) > end_idx or self.current_page > 0:
            self.options.append(more_option)

        select = Select(placeholder="Select a character",
                        options=self.options, custom_id="character_select")
        select.callback = self.get_character
        self.clear_items()
        self.add_item(select)

    async def get_character(self, interaction: Interaction):
        if interaction.data["values"][0] == "More...":
            self.current_page += 1
            if self.current_page * self.per_page >= len(self.characters):
                # If it's the last page, reset to the first page
                self.current_page = 0
            self.update_options()
            await interaction.response.edit_message(view=self)
        else:
            char = None
            for char in self.characters:
                if char.name == interaction.data["values"][0]:
                    character = char
                    break
            embed = genshin_character_embed(character)
            await interaction.response.edit_message(embed=embed, view=self)
