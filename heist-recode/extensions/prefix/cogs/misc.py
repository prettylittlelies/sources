import discord
import time
import asyncio
import json
from discord.ext import commands
from discord import Embed
from data.config import CONFIG
from typing import Optional
import datetime
from system.classes.permissions import Permissions

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._afk_lock = asyncio.Lock()
        
    def _format_duration(self, seconds: int) -> str:
        """Format duration into readable string"""
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0 or not parts:
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
            
        return " and ".join(parts)

    async def _load_json_messages(self, messages):
        """Helper method to load JSON messages asynchronously"""
        def _json_loads(msg):
            return json.loads(msg)
            
        if not messages:
            return []
            
        parsed = await asyncio.gather(*[
            self.bot.loop.run_in_executor(None, _json_loads, msg)
            for msg in messages
        ])
        return parsed

    async def _dump_json(self, data):
        """Helper method to dump JSON asynchronously"""
        return await self.bot.loop.run_in_executor(None, json.dumps, data)

    @commands.command(name="afk") 
    @commands.check(Permissions.is_blacklisted)
    async def afk(self, ctx, *, reason: Optional[str] = None):
        """Set AFK status"""
        warning_emoji = await self.bot.emojis.get("warning", "⚠️")
        
        try:
            async with self.bot.redis.redis.pipeline(transaction=True) as pipe:
                key = f"afk:{ctx.author.id}"
                
                exists = await pipe.exists(key).execute()
                if exists[0]:
                    return await ctx.send(embed=Embed(
                        description=f"{warning_emoji} {ctx.author.mention}: You are already AFK!",
                        color=CONFIG['embed_colors']['error']
                     ))
                    
                timestamp = int(time.time())
                await pipe.hset(
                    key,
                    mapping={
                        "timestamp": timestamp,
                        "reason": reason or ""
                    }
                ).execute()
                
                embed = Embed(
                    description=f"😴 {ctx.author.mention}: You are now AFK{f' with the reason: `{reason}`' if reason else ''}",
                    color=CONFIG['embed_colors']['default']
                )
                await ctx.send(embed=embed)
                
        except Exception as e:
            await ctx.send(embed=Embed(
                description=f"{warning_emoji} {ctx.author.mention}: An error occurred: {str(e)}",
                color=CONFIG['embed_colors']['error']
            ))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.lower().startswith(f"{self.bot.command_prefix}afk"):
            return

        try:
            pipe = self.bot.redis.redis.pipeline(transaction=True)
            tasks = []

            author_key = f"afk:{message.author.id}"
            pipe.hgetall(author_key)
            
            for user in message.mentions:
                pipe.hgetall(f"afk:{user.id}")
                
            results = await pipe.execute()
            
            if author_data := results[0]:
                duration = int(time.time() - int(author_data['timestamp']))
                if duration >= 2:
                    tasks.append(self.bot.redis.redis.delete(author_key))
                    time_str = self._format_duration(duration)
                    tasks.append(message.channel.send(embed=Embed(
                        description=f"👋 {message.author.mention}: Welcome back! You were gone for {time_str}",
                        color=CONFIG['embed_colors']['default']
                    )))

            afk_mentions = []
            for i, user in enumerate(message.mentions, 1):
                if user_data := results[i]:
                    timestamp = int(user_data['timestamp'])
                    afk_text = f"{user.mention} is AFK since <t:{timestamp}:R>"
                    if user_data['reason']:
                        afk_text += f" - `{user_data['reason']}`"
                    afk_mentions.append(afk_text)

            if afk_mentions:
                tasks.append(message.channel.send(embed=Embed(
                    description="\n".join(afk_mentions),
                    color=CONFIG['embed_colors']['default']
                )))

            if tasks:
                await asyncio.gather(*tasks)

        except Exception as e:
            print(f"AFK Error: {e}")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Store deleted messages in Redis."""
        if message.author.bot or not message.guild:
            return

        key = f"snipe:{message.guild.id}:{message.channel.id}"
        data = {
            "author_id": message.author.id,
            "author_name": str(message.author),
            "author_avatar": str(message.author.display_avatar.url),
            "content": message.content,
            "timestamp": int(message.created_at.timestamp())
        }

        json_data = await self._dump_json(data)
        async with self.bot.redis.redis.pipeline(transaction=True) as pipe:
            pipe.lpush(key, json_data)
            pipe.ltrim(key, 0, 49)
            await pipe.execute()

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Store edited messages in Redis."""
        if before.author.bot or not before.guild or before.content == after.content:
            return

        key = f"editsnipe:{before.guild.id}:{before.channel.id}"
        data = {
            "author_id": before.author.id,
            "author_name": str(before.author),
            "author_avatar": str(before.author.display_avatar.url),
            "content": before.content,
            "timestamp": int(before.created_at.timestamp())
        }

        async with self.bot.redis.redis.pipeline(transaction=True) as pipe:
            pipe.lpush(key, json.dumps(data))
            pipe.ltrim(key, 0, 49)
            await pipe.execute()

    @commands.command(
        name="snipe",
        aliases=["s"],
        description="Snipe deleted messages in the current channel.",
        usage="[user] [page]",
        example=",snipe @user 2"
    )
    @commands.check(Permissions.is_blacklisted)
    async def snipe(self, ctx, user: Optional[discord.Member] = None, page: Optional[int] = 1):
        """Retrieve and display deleted messages."""
        key = f"snipe:{ctx.guild.id}:{ctx.channel.id}"
        messages = await self.bot.redis.redis.lrange(key, 0, -1)
        messages = await self._load_json_messages(messages)

        if not messages:
            return await ctx.warning("No deleted messages found in this channel.")

        if user:
            messages = [msg for msg in messages if int(msg["author_id"]) == user.id]

        if not messages:
            return await ctx.warning(f"No deleted messages found for {user.mention}.")

        per_page = 1
        total_pages = (len(messages) + per_page - 1) // per_page
        page = max(1, min(page, total_pages))
        start = (page - 1) * per_page
        end = start + per_page
        messages = messages[start:end]

        for msg in messages:
            embed = Embed(
                description=msg["content"],
                color=CONFIG['embed_colors']['default'],
                timestamp=datetime.datetime.fromtimestamp(msg["timestamp"])
            )
            embed.set_author(
                name=msg["author_name"],
                icon_url=msg["author_avatar"]
            )
            embed.set_footer(text=f"{page}/{total_pages}")

            await ctx.send(embed=embed)


    @commands.command(
        name="editsnipe",
        aliases=["es"],
        description="Snipe edited messages in the current channel.",
        usage="[user] [page]",
        example=",editsnipe @user 2"
    )
    @commands.check(Permissions.is_blacklisted)
    async def editsnipe(self, ctx, user: Optional[discord.Member] = None, page: Optional[int] = 1):
        """Retrieve and display edited messages."""
        key = f"editsnipe:{ctx.guild.id}:{ctx.channel.id}"
        messages = await self.bot.redis.redis.lrange(key, 0, -1)
        if not messages:
            return await ctx.warning("No edited messages found in this channel.")
        messages = [json.loads(msg) for msg in messages]

        if user:
            messages = [msg for msg in messages if int(msg["author_id"]) == user.id]

        if not messages:
            return await ctx.warning(f"No edited messages found for {user.mention}.")

        per_page = 1
        total_pages = (len(messages) + per_page - 1) // per_page
        page = max(1, min(page, total_pages))
        start = (page - 1) * per_page
        end = start + per_page
        messages = messages[start:end]

        for msg in messages:
            embed = Embed(
                description=msg["content"],
                color=CONFIG['embed_colors']['default'],
                timestamp=datetime.datetime.fromtimestamp(msg["timestamp"])
            )
            embed.set_author(
                name=msg["author_name"],
                icon_url=msg["author_avatar"]
            )
            embed.set_footer(text=f"{page}/{total_pages}")

            await ctx.send(embed=embed)

    @commands.command(
        name="clearsnipe",
        aliases=["cs"],
        description="Clear all sniped and edited sniped messages in the current channel.",
        usage="",
        example=",clearsnipe"
    )
    @commands.has_permissions(manage_messages=True)
    @commands.check(Permissions.is_blacklisted)
    async def clearsnipe(self, ctx):
        """Clear all sniped and edited sniped messages in the current channel."""
        snipe_key = f"snipe:{ctx.guild.id}:{ctx.channel.id}"
        editsnipe_key = f"editsnipe:{ctx.guild.id}:{ctx.channel.id}"

        snipe_messages = await self.bot.redis.redis.lrange(snipe_key, 0, -1)
        editsnipe_messages = await self.bot.redis.redis.lrange(editsnipe_key, 0, -1)

        if not snipe_messages and not editsnipe_messages:
            return await ctx.warning("No sniped messages found in this channel.")

        await self.bot.redis.redis.delete(snipe_key)
        await self.bot.redis.redis.delete(editsnipe_key)
            
        await ctx.success("All snipes and edits in this channel have been cleared.")


async def setup(bot):
    await bot.add_cog(Misc(bot))