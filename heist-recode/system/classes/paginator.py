import asyncio
from inspect import iscoroutinefunction as iscoro
from inspect import isfunction as isfunc
from io import BytesIO

import discord
from discord import File

class Paginator(discord.ui.View):
    """
    A paginator for Discord embeds with interactive navigation buttons.
    """
    def __init__(
        self,
        bot,
        embeds,
        destination,
        *,
        timeout=180,
        invoker=None,
        attachments=None,
        files=None,
        error_emoji="⚠️",
        error_color="d6bcd0"
    ):
        """
        Initialize a new paginator.
        
        Parameters
        -----------
        bot: :class:`Bot`
            The bot object
        embeds: :class:`list`
            The embeds that will be paginated
        destination: :class:`discord.abc.Messageable`
            The channel the pagination message will be sent to
        timeout: Optional[:class:`float`]
            The number of seconds to wait before timing out.
        invoker: Optional[:class:`int`]
            The user ID who can interact with the paginator
        attachments: Optional[:class:`list`]
            List of attachments to display with each page
        error_emoji: Optional[:class:`str`]
            The emoji to use for error messages
        error_color: Optional[:class:`str`]
            The hexadecimal color to use for error messages
        """
        super().__init__(timeout=timeout)
        
        self.bot = bot
        self.embeds = embeds
        self.destination = destination
        self.page = 0
        self.message = None
        self.invoker = invoker
        self.attachments = attachments
        self.files = files
        self.emoji = error_emoji
        self.color = int(error_color, 16) if isinstance(error_color, str) else error_color
        
    async def on_timeout(self):
        """Handle timeout by removing all buttons except persistent link buttons."""
        if self.message:
            for item in self.children:
                if isinstance(item, LinkButton) and item.persist:
                    continue
                item.disabled = True
                
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass
            
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if the user is allowed to interact with the paginator."""
        if self.invoker is None:
            return True
            
        if interaction.user.id != self.invoker:
            embed = discord.Embed(
                description=f"{self.emoji} {interaction.user.mention}: **You aren't the author of this embed**!",
                color=self.color
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
            
        return True
        
    async def start(self):
        """Start the paginator by sending the initial message."""
        if not self.embeds:
            raise ValueError("No embeds to paginate")
            
        current = self.embeds[self.page]
        
        if isinstance(current, discord.Embed):
            if self.files:
                self.message = await self.destination.send(embed=current, files=self.files, view=self)
            elif self.attachments and self.page < len(self.attachments):
                file = self.attachments[self.page]
                self.message = await self.destination.send(embed=current, file=file, view=self)
            else:
                self.message = await self.destination.send(embed=current, view=self)
                
        elif isinstance(current, str):
            if self.attachments and self.page < len(self.attachments):
                file = self.attachments[self.page]
                self.message = await self.destination.send(content=current, file=file, view=self)
            else:
                self.message = await self.destination.send(content=current, view=self)
                
        elif isinstance(current, dict):
            kwargs = current.copy()
            
            if "files" in kwargs or "attachments" in kwargs:
                files_key = "files" if "files" in kwargs else "attachments"
                files_data = kwargs.pop(files_key, [])
                
                files = []
                for file_dict in files_data:
                    if isinstance(file_dict, dict) and "data" in file_dict and "filename" in file_dict:
                        files.append(File(fp=BytesIO(file_dict["data"]), filename=file_dict["filename"]))
                
                if files:
                    kwargs["files"] = files
            
            kwargs["view"] = self
            self.message = await self.destination.send(**kwargs)
            
        elif isinstance(current, tuple):
            content = None
            embed = None
            
            for item in current:
                if isinstance(item, str):
                    content = item
                elif isinstance(item, discord.Embed):
                    embed = item
            
            if self.attachments and self.page < len(self.attachments):
                file = self.attachments[self.page]
                self.message = await self.destination.send(content=content, embed=embed, file=file, view=self)
            else:
                self.message = await self.destination.send(content=content, embed=embed, view=self)
        
    async def edit_page(self, interaction):
        """Edit the message to show the current page."""
        current = self.embeds[self.page]
        
        for child in self.children:
            if isinstance(child, ShowPageButton):
                child.label = f"{self.page + 1}/{len(self.embeds)}"
        
        if isinstance(current, discord.Embed):
            if self.attachments and self.page < len(self.attachments):
                file = self.attachments[self.page]
                await interaction.message.edit(embed=current, attachments=[file], view=self)
            else:
                await interaction.message.edit(embed=current, attachments=[], view=self)
                
        elif isinstance(current, str):
            if self.attachments and self.page < len(self.attachments):
                file = self.attachments[self.page]
                await interaction.message.edit(content=current, embed=None, attachments=[file], view=self)
            else:
                await interaction.message.edit(content=current, embed=None, attachments=[], view=self)
                
        elif isinstance(current, dict):
            kwargs = current.copy()
            
            if "files" in kwargs or "attachments" in kwargs:
                files_key = "files" if "files" in kwargs else "attachments"
                files_data = kwargs.pop(files_key, [])
                
                files = []
                for file_dict in files_data:
                    if isinstance(file_dict, dict) and "data" in file_dict and "filename" in file_dict:
                        files.append(File(fp=BytesIO(file_dict["data"]), filename=file_dict["filename"]))
                
                if files:
                    kwargs["attachments"] = files
                else:
                    kwargs["attachments"] = []
            else:
                kwargs["attachments"] = []
            
            kwargs["view"] = self
            await interaction.message.edit(**kwargs)
            
        elif isinstance(current, tuple):
            content = None
            embed = None
            
            for item in current:
                if isinstance(item, str):
                    content = item
                elif isinstance(item, discord.Embed):
                    embed = item
            
            if self.attachments and self.page < len(self.attachments):
                file = self.attachments[self.page]
                await interaction.message.edit(content=content, embed=embed, attachments=[file], view=self)
            else:
                await interaction.message.edit(content=content, embed=embed, attachments=[], view=self)
    
    def add_button(
        self,
        action,
        *,
        label=None,
        emoji=None,
        style=discord.ButtonStyle.grey,
        row=None
    ):
        """Add a navigation button to the paginator."""
        action = action.strip().lower()
        
        if action == "first":
            self.add_item(FirstPageButton(label, emoji, style, row))
        elif action in ["back", "prev", "previous"]:
            self.add_item(PrevPageButton(label, emoji, style, row))
        elif action in ["page", "show"]:
            self.add_item(ShowPageButton(f"1/{len(self.embeds)}" if label is None else label, emoji, style, row))
        elif action == "next":
            self.add_item(NextPageButton(label, emoji, style, row))
        elif action == "last":
            self.add_item(LastPageButton(label, emoji, style, row))
        elif action == "goto":
            self.add_item(GotoPageButton(label or "Go to", emoji, style, row))
        elif action == "delete":
            self.add_item(DeleteButton(label, emoji, style, row))
        elif action == "end":
            self.add_item(EndButton(label, emoji, style, row))
        elif action == "lock":
            self.add_item(LockButton(label, emoji, style, row))
    
    def add_custom_button(
        self,
        callback,
        *,
        label=None,
        emoji=None,
        style=discord.ButtonStyle.grey,
        row=None,
        disabled=False,
        custom_id=None
    ):
        """
        Add a custom button with a user-defined callback function.
        
        Parameters
        -----------
        callback: Callable
            The coroutine function to call when the button is clicked
        label: Optional[:class:`str`]
            The label for the button
        emoji: Optional[:class:`str` or :class:`discord.Emoji`]
            The emoji for the button
        style: Optional[:class:`discord.ButtonStyle`]
            The style of the button
        row: Optional[:class:`int`]
            The row to place the button on
        disabled: Optional[:class:`bool`]
            Whether the button should be disabled
        custom_id: Optional[:class:`str`]
            The custom ID for the button
        """
        self.add_item(CustomButton(callback, label, emoji, style, row, disabled, custom_id))
    
    def add_link_button(
        self,
        url,
        *,
        label=None,
        emoji=None,
        row=None,
        persist=True,
        disabled=False
    ):
        """
        Add a link button that redirects to a URL.
        
        Parameters
        -----------
        url: :class:`str`
            The URL to redirect to
        label: Optional[:class:`str`]
            The label for the button
        emoji: Optional[:class:`str` or :class:`discord.Emoji`]
            The emoji for the button
        row: Optional[:class:`int`]
            The row to place the button on
        persist: Optional[:class:`bool`]
            If True, the button will not be disabled on timeout
        disabled: Optional[:class:`bool`]
            Whether the button should be disabled initially
        """
        self.add_item(LinkButton(url, label, emoji, row, persist, disabled))
    
    def default_pagination(self):
        """Add a default set of navigation buttons."""
        self.add_button("first", label="«")
        self.add_button("back", label="‹")
        self.add_button("page")
        self.add_button("next", label="›")
        self.add_button("last", label="»")
        self.add_button("delete", label="✖")

class FirstPageButton(discord.ui.Button):
    """Button to go to the first page."""
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)
        
    async def callback(self, interaction):
        await interaction.response.defer()
        view = self.view
        view.page = 0
        await view.edit_page(interaction)


class PrevPageButton(discord.ui.Button):
    """Button to go to the previous page."""
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)
        
    async def callback(self, interaction):
        await interaction.response.defer()
        view = self.view
        view.page = (view.page - 1) % len(view.embeds)
        await view.edit_page(interaction)


class NextPageButton(discord.ui.Button):
    """Button to go to the next page."""
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)
        
    async def callback(self, interaction):
        await interaction.response.defer()
        view = self.view
        view.page = (view.page + 1) % len(view.embeds)
        await view.edit_page(interaction)


class LastPageButton(discord.ui.Button):
    """Button to go to the last page."""
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)
        
    async def callback(self, interaction):
        await interaction.response.defer()
        view = self.view
        view.page = len(view.embeds) - 1
        await view.edit_page(interaction)


class ShowPageButton(discord.ui.Button):
    """Button that displays the current page number (non-interactive)."""
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, disabled=True, row=row)


class GotoPageButton(discord.ui.Button):
    """Button to open a modal to go to a specific page."""
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)
        
    async def callback(self, interaction):
        await interaction.response.send_modal(GotoModal(self))


class DeleteButton(discord.ui.Button):
    """Button to delete the paginator message."""
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)
        
    async def callback(self, interaction):
        view = self.view
        await interaction.message.delete()
        view.stop()


class EndButton(discord.ui.Button):
    """Button to end the pagination and disable all buttons."""
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)
        
    async def callback(self, interaction):
        await interaction.response.defer()
        view = self.view
        
        for child in view.children:
            child.disabled = True
            
        await view.edit_page(interaction)
        view.stop()


class LockButton(discord.ui.Button):
    """Button to remove all buttons from the message."""
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)


class CustomButton(discord.ui.Button):
    """Button with a custom callback function."""
    def __init__(self, callback, label, emoji, style, row, disabled, custom_id):
        super().__init__(
            label=label, 
            emoji=emoji, 
            style=style, 
            row=row, 
            disabled=disabled,
            custom_id=custom_id
        )
        self.custom_callback = callback
        
    async def callback(self, interaction):
        await self.custom_callback(interaction, self.view)


class LinkButton(discord.ui.Button):
    """Button that redirects to a URL and optionally persists after timeout."""
    def __init__(self, url, label, emoji, row, persist, disabled=False):
        super().__init__(
            label=label,
            emoji=emoji,
            style=discord.ButtonStyle.link,
            url=url,
            row=row,
            disabled=disabled
        )
        self.persist = persist
        
    def should_disable_on_timeout(self):
        return not self.persist

class GotoModal(discord.ui.Modal, title="Go to Page"):
    """Modal for entering a page number to navigate to."""
    def __init__(self, button):
        super().__init__()
        self.button = button
        
        self.page_input = discord.ui.TextInput(
            label="Page Number",
            placeholder=f"Enter a number (1-{len(self.button.view.embeds)})",
            required=True,
            min_length=1,
            max_length=5
        )
        self.add_item(self.page_input)
        
    async def on_submit(self, interaction):
        try:
            view = self.button.view
            page_num = int(self.page_input.value)
            
            if 1 <= page_num <= len(view.embeds):
                view.page = page_num - 1
                await view.edit_page(interaction)
            else:
                await interaction.response.send_message(
                    f"Invalid page number. Please enter a number between 1 and {len(view.embeds)}.",
                    ephemeral=True
                )
        except ValueError:
            await interaction.response.send_message(
                "Please enter a valid number.",
                ephemeral=True
            )

def embed_creator(
    text,
    num,
    *,
    title="",
    prefix="",
    suffix="",
    color=None,
    colour=None
):
    """
    A helper function which creates a list of embeds from a long text.
    
    Parameters
    -----------
    text: :class:`str`
        The text to paginate
    num: :class:`int`
        The maximum number of characters per page
    title: Optional[:class:`str`]
        The title for all embeds
    prefix: Optional[:class:`str`]
        Text to add before each chunk
    suffix: Optional[:class:`str`]
        Text to add after each chunk
    color/colour: Optional[:class:`int`]
        The color for all embeds
    
    Returns
    --------
    List[:class:`discord.Embed`]
        The list of embeds created
    """
    if color is not None and colour is not None:
        raise ValueError("Cannot specify both color and colour")
        
    final_color = color if color is not None else colour
    
    return [
        discord.Embed(
            title=title,
            description=prefix + text[i:i+num] + suffix,
            color=final_color
        )
        for i in range(0, len(text), num)
    ]