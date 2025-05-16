import discord
from discord import Embed
from data.config import CONFIG
from typing import Any, Optional, Union
from discord.ext.commands import Context

async def warning(ctx: Context, text: str, *args: Any, **kwargs: Any) -> discord.Message:
    """Display a warning message with an emoji and formatted text."""
    emoji = await ctx.bot.emojis.get('warning', "<:warning:1367925777550803054>")
    color = CONFIG['embed_colors']['error']
    embed = Embed(color=color, description=f"{emoji} {ctx.author.mention}: {text}")
    
    if footer := kwargs.pop("footer", None):
        if isinstance(footer, tuple):
            embed.set_footer(text=footer[0], icon_url=footer[1])
        else:
            embed.set_footer(text=footer)
            
    if author := kwargs.pop("author", None):
        if isinstance(author, tuple):
            embed.set_author(name=author[0], icon_url=author[1])
        else:
            embed.set_author(name=author)
            
    delete_after = kwargs.get("delete_after")
    
    if kwargs.get("return_embed", False) is True:
        return embed
        
    return await ctx.send(
        embed=embed,
        delete_after=delete_after,
        view=kwargs.pop("view", None),
        **kwargs,
    )

async def success(ctx: Context, text: str, *args: Any, **kwargs: Any) -> discord.Message:
    """Display a success message with an emoji and formatted text."""
    emoji = await ctx.bot.emojis.get('success', "<:success:1367925770395320380>")
    color = CONFIG['embed_colors']['success']
    embed = Embed(color=color, description=f"{emoji} {ctx.author.mention}: {text}")
    
    if footer := kwargs.pop("footer", None):
        if isinstance(footer, tuple):
            embed.set_footer(text=footer[0], icon_url=footer[1])
        else:
            embed.set_footer(text=footer)
            
    if author := kwargs.pop("author", None):
        if isinstance(author, tuple):
            embed.set_author(name=author[0], icon_url=author[1])
        else:
            embed.set_author(name=author)
            
    delete_after = kwargs.get("delete_after")
    
    if kwargs.get("return_embed", False) is True:
        return embed
        
    return await ctx.send(
        embed=embed,
        delete_after=delete_after,
        view=kwargs.pop("view", None),
        **kwargs,
    )