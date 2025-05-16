import functools
from typing import Callable, Optional, TypeVar, Any, Union, cast
import discord
from discord.ext import commands
from discord import app_commands

T = TypeVar('T', bound=Callable[..., Any])

def premium(func: T) -> T:
    """
    A decorator that checks if a user has premium status before running the command.
    Works with both prefix and hybrid commands.
    """
    @functools.wraps(func)
    async def wrapper(self, ctx, *args, **kwargs):
        if isinstance(ctx, discord.Interaction):
            user_id = ctx.user.id
            is_premium = await self.bot.db.check_donor(user_id)
            warning_emoji = await self.bot.emojis.get('warning', '⚠️')
            
            if not is_premium:
                if not ctx.response.is_done():
                    await ctx.response.defer(ephemeral=True)
                await ctx.followup.send(
                    embed=discord.Embed(
                        description=f"{warning_emoji} {ctx.author}: This command requires premium, join [**our server**](https://discord.gg/heistbot) for more informations!",
                        color=0xf9c62b
                    ),
                    ephemeral=True
                )
                return
        else:
            user_id = ctx.author.id
            is_premium = await self.bot.db.check_donor(user_id)
            
            if not is_premium:
                return await ctx.warning(
                    "This command requires premium, join [**our server**](https://discord.gg/heistbot) for more informations!",
                    ephemeral=True
                )
        
        return await func(self, ctx, *args, **kwargs)
    
    if hasattr(func, '__app_command__'):
        original_check = func.__app_command__._checks.pop() if func.__app_command__._checks else None
        
        async def premium_check_app_command(interaction: discord.Interaction) -> bool:
            is_premium = await interaction.client.db.check_donor(interaction.user.id)
            
            if not is_premium:
                warning_emoji = await interaction.client.emojis.get('warning', '⚠️')
                embed = discord.Embed(
                    description=f"{warning_emoji} {interaction.user.mention}: This command requires premium, join [**our server**](https://discord.gg/heistbot) for more informations!",
                    color=0xf9c62b
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return False
                
            if original_check:
                return await original_check(interaction)
            return True
            
        func.__app_command__.add_check(premium_check_app_command)
    
    return cast(T, wrapper)

def requires_perms(**perms):
    """
    A decorator that checks if a user has the required permissions.
    Works with app_commands.
    """
    async def predicate(interaction: discord.Interaction) -> bool:
        for perm, value in perms.items():
            if not getattr(interaction.permissions, perm, False) == value:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        f"You need the `{perm.replace('_', ' ').title()}` permission to use this command.",
                        ephemeral=True
                    )
                return False
        return True
    
    return app_commands.check(predicate)