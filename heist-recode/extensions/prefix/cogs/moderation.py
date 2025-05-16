import discord
import time
import asyncio
from discord.ext import commands
from discord import Embed
from data.config import CONFIG
from typing import Optional
import datetime
from system.classes.permissions import Permissions

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(
        name="botclear", 
        aliases=["bc", "botpurge", "bp"],
        description="Clear bot messages and command messages",
        brief="Clear bot and command messages",
        help="Delete bot messages and command messages from channel",
        usage="<amount>",
        example=",botclear 10",
        perms=["manage_messages"]
    )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.check(Permissions.is_blacklisted)
    async def botclear(self, ctx, amount: Optional[int] = 5):
        """Clear bot messages and command messages from the channel"""
        if not 1 <= amount <= 150:
            return await ctx.warning(f"Amount must be between 1 and 150")

        async def check(m):
            if m.author.bot:
                return True
            return any(m.content.startswith(prefix) for prefix in ctx.bot.command_prefix)

        to_delete = []
        async for message in ctx.channel.history(limit=amount + 1):
            if await check(message):
                to_delete.append(message)

        if len(to_delete) <= 1:
            return await ctx.warning(f"No bot/command messages found to delete")

        await ctx.channel.delete_messages(to_delete)
        
        await ctx.success(f"Successfully cleared `{len(to_delete) - 1}` bot/command messages", delete_after=5)

    @commands.command(
        name="selfpurge",
        aliases=["sp", "selfclear", "sc"],
        description="Clear your own messages from the channel",
        brief="Clear your messages",
        help="Delete your own messages from the channel",
        usage="<amount>",
        example=",selfpurge 10",
        perms=["manage_messages"]
    )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.check(Permissions.is_blacklisted)
    async def selfpurge(self, ctx, amount: Optional[int] = 5):
        """Clear your own messages from the channel"""
        if not 1 <= amount <= 150:
            return await ctx.warning(f"Amount must be between 1 and 150")

        def check(m):
            return m.author.id == ctx.author.id

        to_delete = []
        async for message in ctx.channel.history(limit=500):
            if (time.time() - message.created_at.timestamp()) > 14 * 24 * 60 * 60:
                continue
            if check(message):
                to_delete.append(message)
            if len(to_delete) >= amount:
                break

        if not to_delete:
            return await ctx.warning(f"No messages found to delete")

        await ctx.channel.delete_messages(to_delete)

        await ctx.success(f"Successfully cleared `{len(to_delete)}` of your messages")

    @commands.command(
        name="purge",
        aliases=["clear", "clean"],
        description="Purge messages from the channel",
        brief="Purge messages",
        help="Delete messages from the channel. Optionally, specify a user to purge their messages only.",
        usage="[user] <amount>",
        example=",purge @user 10",
        perms=["manage_messages"]
    )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.check(Permissions.is_blacklisted)
    async def purge(self, ctx, user: Optional[discord.Member] = None, amount: Optional[int] = 2):
        """Purge messages from the channel"""
        if not 2 <= amount <= 100:
            return await ctx.warning(f"Amount must be between 5 and 200")

        def check(m):
            if user:
                return m.author.id == user.id
            return True

        to_delete = []
        async for message in ctx.channel.history(limit=500):
            if len(to_delete) >= amount:
                break
            if check(message):
                to_delete.append(message)

        if not to_delete:
            return await ctx.warning(f"No messages found to delete")

        await ctx.channel.delete_messages(to_delete)

        await ctx.success(f"Successfully cleared `{len(to_delete)}` messages")

    @commands.command(
        name="nuke",
        description="Nuke the channel by deleting it and creating a new one with the same settings",
        brief="Nuke the channel",
        help="Duplicates the channel and deletes the old one. Requires Manage Channels permission.",
        usage="",
        example=",nuke",
        perms=["manage_channels"]
    )
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.check(Permissions.is_blacklisted)
    async def nuke(self, ctx):
        """Nuke the channel by duplicating it and deleting the old one"""
        position = ctx.channel.position
        new_channel = await ctx.channel.clone(reason=f"Nuked by {ctx.author}")
        await new_channel.edit(position=position)

        await new_channel.send(f"{ctx.author.mention}: This channel has been nuked!")

        await ctx.channel.delete(reason=f"Nuked by {ctx.author}")

    @commands.command(
        name="ban",
        description="Ban a user from the server",
        brief="Ban a user",
        help="Ban a user from the server with an optional reason",
        usage="<user> [reason]",
        example=",ban @user Breaking rules",
        perms=["ban_members"]
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.check(Permissions.is_blacklisted)
    async def ban(self, ctx, user: discord.Member, *, reason: Optional[str] = "No reason provided"):
        """Ban a user from the server"""
        if user.top_role.position >= ctx.author.top_role.position and ctx.author.id != ctx.guild.owner_id:
            return await ctx.warning("You cannot ban someone with a higher or equal role")
        
        await user.ban(reason=f"{reason} | Banned by {ctx.author}")
        await ctx.success(f"Successfully banned {user.mention} for: {reason}")
    
    @commands.command(
        name="unban",
        description="Unban a user from the server",
        brief="Unban a user",
        help="Unban a user from the server using their user ID or username#discriminator",
        usage="<user_id/username#discriminator>",
        example=",unban 123456789012345678",
        perms=["ban_members"]
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.check(Permissions.is_blacklisted)
    async def unban(self, ctx, user_id: str):
        """Unban a user from the server"""
        try:
            user_id = int(user_id)
            user = discord.Object(id=user_id)
            await ctx.guild.unban(user, reason=f"Unbanned by {ctx.author}")
            return await ctx.success(f"Successfully unbanned user with ID: {user_id}")
        except ValueError:
            banned_users = [entry async for entry in ctx.guild.bans()]
            for ban_entry in banned_users:
                if str(ban_entry.user) == user_id:
                    await ctx.guild.unban(ban_entry.user, reason=f"Unbanned by {ctx.author}")
                    return await ctx.success(f"Successfully unbanned {ban_entry.user}")
            
            return await ctx.warning(f"Could not find banned user: {user_id}")
    
    @commands.command(
        name="kick",
        description="Kick a user from the server",
        brief="Kick a user",
        help="Kick a user from the server with an optional reason",
        usage="<user> [reason]",
        example=",kick @user Breaking rules",
        perms=["kick_members"]
    )
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.check(Permissions.is_blacklisted)
    async def kick(self, ctx, user: discord.Member, *, reason: Optional[str] = "No reason provided"):
        """Kick a user from the server"""
        
        if user.top_role.position >= ctx.author.top_role.position and ctx.author.id != ctx.guild.owner_id:
            return await ctx.warning("You cannot kick someone with a higher or equal role")
        
        await user.kick(reason=f"{reason} | Kicked by {ctx.author}")
        await ctx.success(f"Successfully kicked {user.mention} for: {reason}")
    
    @commands.command(
        name="timeout",
        aliases=["mute"],
        description="Timeout a user for a specified duration",
        brief="Timeout a user",
        help="Timeout a user, preventing them from sending messages or joining voice channels",
        usage="<user> <duration> [reason]",
        example=",timeout @user 1h Spamming",
        perms=["moderate_members"]
    )
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    @commands.check(Permissions.is_blacklisted)
    async def timeout(self, ctx, user: discord.Member, duration: str, *, reason: Optional[str] = "No reason provided"):
        """Timeout a user for a specified duration"""
        if user.top_role.position >= ctx.author.top_role.position and ctx.author.id != ctx.guild.owner_id:
            return await ctx.warning("You cannot timeout someone with a higher or equal role")
        
        time_conversions = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400
        }
        
        amount = int(duration[:-1])
        unit = duration[-1].lower()
        
        if unit not in time_conversions:
            return await ctx.warning("Invalid duration format. Use s for seconds, m for minutes, h for hours, d for days")
        
        seconds = amount * time_conversions[unit]
        if seconds > 2419200:
            return await ctx.warning("Timeout duration cannot exceed 28 days")
            
        until = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)
        await user.timeout(until, reason=f"{reason} | Timed out by {ctx.author}")
        
        readable_time = duration
        await ctx.success(f"Successfully timed out {user.mention} for {readable_time} with reason: {reason}")

    @commands.command(
        name="untimeout",
        aliases=["unmute", "rt", "removetimeout"],
        description="Remove a timeout from a user",
        brief="Remove a user's timeout",
        help="Remove a timeout from a user, allowing them to send messages and join voice channels",
        usage="<user> [reason]",
        example=",untimeout @user",
        perms=["moderate_members"]
    )
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    @commands.check(Permissions.is_blacklisted)
    async def untimeout(self, ctx, user: discord.Member, *, reason: Optional[str] = "No reason provided"):
        """Remove a timeout from a user"""
        if user.top_role.position >= ctx.author.top_role.position and ctx.author.id != ctx.guild.owner_id:
            return await ctx.warning("You cannot remove a timeout from someone with a higher or equal role")
        
        if not user.is_timed_out():
            return await ctx.warning(f"{user.mention} is not timed out")
            
        await user.timeout(None, reason=f"{reason} | Timeout removed by {ctx.author}")
        await ctx.success(f"Successfully removed timeout from {user.mention}")
            
async def setup(bot):
    await bot.add_cog(Moderation(bot))