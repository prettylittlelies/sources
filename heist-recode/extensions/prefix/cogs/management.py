from discord.ext import commands
from discord import Embed
from data.config import CONFIG
from system.classes.permissions import Permissions

class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="lock",
        description="Lock the current channel by disabling send messages permission",
        brief="Lock the channel",
        help="Prevents everyone from sending messages in the current channel",
        usage="",
        example=",lock",
        perms=["manage_channels"]
    )
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.check(Permissions.is_blacklisted)
    async def lock(self, ctx):
        """Lock the current channel by disabling send messages permission"""
        default_role = ctx.guild.default_role
            
        current_perms = ctx.channel.permissions_for(default_role)
        if not current_perms.send_messages:
            return await ctx.warning("This channel is already locked")

        await ctx.channel.set_permissions(
            default_role,
            send_messages=False,
            reason=f"Channel locked by {ctx.author}"
        )
            
        await ctx.success("Channel has been locked successfully")

    @commands.command(
        name="unlock",
        description="Unlock the current channel by enabling send messages permission",
        brief="Unlock the channel",
        help="Allows everyone to send messages in the current channel",
        usage="",
        example=",unlock",
        perms=["manage_channels"]
    )
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.check(Permissions.is_blacklisted)
    async def unlock(self, ctx):
        """Unlock the current channel by enabling send messages permission"""
        default_role = ctx.guild.default_role
            
        current_perms = ctx.channel.permissions_for(default_role)
        if current_perms.send_messages:
            return await ctx.warning("This channel is already unlocked")

        await ctx.channel.set_permissions(
            default_role,
            send_messages=True,
            reason=f"Channel unlocked by {ctx.author}"
        )
            
        await ctx.success("Channel has been unlocked successfully")

async def setup(bot):
    await bot.add_cog(Management(bot))