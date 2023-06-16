import discord
from discord import ui
from discord.ext import menus


class DiscordPages(ui.View, menus.MenuPages):
    """
    Extends the menus extension to make a useful paginator
    for our multi-page embeds.

    Rapptz has not updated the extension library in sometime
    so may need to incorporate more code from that lib in
    future to support this
    """

    def __init__(self, source, timeout=60, auto_footer=False, message=None):
        super().__init__(timeout=timeout)
        self._source = source
        self.auto_footer = auto_footer
        self.current_page = 0
        self.ctx = None
        self.message = message
        if self.message:
            self.followup = True
        else:
            self.followup = False

    async def start(self, ctx, *, channel=None, wait=False):
        await self._source._prepare_once()
        self.ctx = ctx
        self.message = await self.send_initial_message(ctx, ctx.channel)

    async def show_page(self, page_number):
        page = await self._source.get_page(page_number)
        self.current_page = page_number
        kwargs = await self._get_kwargs_from_page(page)
        if not self.followup:
            self.message = await self.ctx.original_response()
        await self.message.edit(**kwargs)

    async def send_initial_message(self, ctx, channel):
        """|coro|

        The default implementation of :meth:`Menu.send_initial_message`
        for the interactive pagination session.

        This implementation shows the first page of the source.
        """
        self.ctx = ctx
        page = await self._source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        if self.followup:
            return await self.ctx.followup.send(**kwargs, wait=True)
        else:
            return await self.ctx.response.send_message(**kwargs)

    async def _get_kwargs_from_page(self, page):
        """This method calls ListPageSource.format_page class"""
        value = await super()._get_kwargs_from_page(page)
        if "view" not in value:
            value.update({"view": self})
        return value

    async def interaction_check(self, interaction):
        """Only allow the user that invokes the command to be able to use the interaction"""
        return interaction.user == self.ctx.user

    @ui.button(emoji="⏮️", style=discord.ButtonStyle.grey)
    async def first_page(self, interaction, button):
        await interaction.response.defer()
        await self.show_page(0)

    @ui.button(emoji="⏪", style=discord.ButtonStyle.grey)
    async def before_page(self, interaction, button):
        await interaction.response.defer()
        await self.show_checked_page(self.current_page - 1)

    @ui.button(emoji="🛑", style=discord.ButtonStyle.grey)
    async def stop_page(self, interaction, button):
        await interaction.response.defer()
        self.stop()

    @ui.button(emoji="⏩", style=discord.ButtonStyle.grey)
    async def next_page(self, interaction, button):
        await interaction.response.defer()
        await self.show_checked_page(self.current_page + 1)

    @ui.button(emoji="⏭️", style=discord.ButtonStyle.grey)
    async def last_page(self, interaction, button):
        await interaction.response.defer()
        await self.show_page(self._source.get_max_pages() - 1)
