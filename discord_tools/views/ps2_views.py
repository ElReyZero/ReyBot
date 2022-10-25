from discord.ui import View, Button
from discord import ButtonStyle, Interaction, InteractionResponded

from discord_tools.embeds import get_ow_embed


class NextPrevButtonView(View):
    """_summary_: Abstract Class that contains the common functionality for the Views Using Next and Previous Buttons

    Args:
        View (_type_): _description_
    """

    def __init__(self, data):
        self.data = data
        super().__init__()
        self.add_buttons()

    def add_buttons(self):
        """_summary_: Adds buttons to the view
        """
        prev = Button(label="Prev", custom_id="prev", style=ButtonStyle.green)
        prev.callback = self.previous
        next = Button(label="Next", custom_id="next", style=ButtonStyle.green)
        next.callback = self.next
        self.add_item(prev)
        self.add_item(next)

    async def previous(self, interaction: Interaction):
        pass

    async def next(self, interaction: Interaction):
        pass


class OWView(NextPrevButtonView):

    def __init__(self, data, server, match=False):
        self.server = server
        self.match = match
        super().__init__(data)
        if len(self.data) > 5:
            self.half = len(self.data)//2
            self.pages = [self.data[:self.half], self.data[self.half:]]
            self.current_page = 1

    async def previous(self, interaction):
        try:
            if self.current_page > 1:
                self.current_page -= 1
                content = self.pages[self.current_page-1]
                embed = get_ow_embed(content, self.server, self.current_page, len(
                    self.pages), match=self.match)
                await interaction.response.edit_message(embed=embed)
            else:
                self.current_page = len(self.pages)
                content = self.pages[self.current_page-1]
                embed = get_ow_embed(content, self.server, self.current_page, len(
                    self.pages), match=self.match)
                await interaction.response.edit_message(embed=embed)
        except InteractionResponded:
            pass

    async def next(self, interaction):
        try:
            if self.current_page != len(self.pages):
                self.current_page += 1
                content = self.pages[self.current_page-1]
                embed = get_ow_embed(content, self.server, self.current_page, len(
                    self.pages), match=self.match)
                await interaction.response.edit_message(embed=embed)
            else:
                self.current_page = 1
                content = self.pages[self.current_page-1]
                embed = get_ow_embed(content, self.server, self.current_page, len(
                    self.pages), match=self.match)
                await interaction.response.edit_message(embed=embed)
        except InteractionResponded:
            pass
