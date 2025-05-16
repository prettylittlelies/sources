import discord
import aiohttp
import asyncio
from discord import app_commands, File, Embed
from discord.ext import commands
from discord.ext.commands import Cog, hybrid_command, hybrid_group
from data.config import CONFIG
from typing import Optional, Union
from system.classes.permissions import Permissions

class Roleplay(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def update_count(self, user_id: int, target_id: int, action: str) -> str:
        """Update and get the ordinal count for an action between users"""
        cache_key = f"action:{user_id}:{target_id}:{action}"
        
        cached_count = await self.bot.redis.redis.get(cache_key)
        
        if cached_count:
            count = int(cached_count) + 1
            await self.bot.redis.redis.set(cache_key, str(count))
        else:
            query = "SELECT count FROM user_actions WHERE user_id = $1 AND target_user_id = $2 AND action = $3"
            result = await self.bot.db.fetchrow(query, user_id, target_id, action)
            
            if result:
                count = result['count'] + 1
                update_query = """
                    UPDATE user_actions 
                    SET count = $1 
                    WHERE user_id = $2 AND target_user_id = $3 AND action = $4
                """
                await self.bot.db.fetchrow(update_query + " RETURNING count", count, user_id, target_id, action)
            else:
                count = 1
                insert_query = """
                    INSERT INTO user_actions (user_id, target_user_id, action, count)
                    VALUES ($1, $2, $3, $4)
                    RETURNING count
                """
                await self.bot.db.fetchrow(insert_query, user_id, target_id, action, count)
        
        await self.bot.redis.redis.setex(cache_key, 3600, str(count))
        
        if 10 <= count % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(count % 10, 'th')
        
        return f"{count}{suffix}"

    @hybrid_group(
        name="roleplay", 
        description="Roleplay related commands",
        fallback="help"
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def roleplay(self, ctx):
        """Roleplay related commands"""
        if ctx.invoked_subcommand is None:
            embed = Embed(
                title="Roleplay Commands",
                description="Use these commands to roleplay with other users! (Or yourself)",
                color=await self.bot.color_manager.resolve(ctx.author.id)
            )
            
            commands = [
                "slap", "hug", "kiss", "bite", "baka", "cuddle", "feed", 
                "handhold", "handshake", "highfive", "kick", "pat", 
                "punch", "peck", "poke", "shoot", "cry"
            ]
            
            embed.add_field(
                name="Available Actions",
                value=", ".join(f"`{cmd}`" for cmd in commands),
                inline=False
            )
            
            embed.add_field(
                name="Usage",
                value=f"Use `{ctx.prefix}roleplay <action> [@user]` or `,roleplay <action> [@user]`",
                inline=False
            )
            
            await ctx.send(embed=embed)

    @roleplay.command(
        name="slap",
        description="Slap someone"
    )
    @app_commands.describe(user="The user to slap")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def slap(self, ctx, user: Optional[Union[discord.Member, discord.User]] = None):
        """Slap someone"""
        user = user or ctx.author
        
        async with ctx.typing():
            ordinal_count = await self.update_count(ctx.author.id, user.id, "slap")
            
            async with self.session.get("https://nekos.best/api/v2/slap") as response:
                if response.status == 200:
                    data = await response.json()
                    gif_url = data['results'][0]['url']
                    anime_name = data['results'][0]['anime_name']
                else:
                    error_emoji = await self.bot.emojis.get("warning", "❌")
                    return await ctx.send(embed=Embed(
                        description=f"{error_emoji} {ctx.author.mention}: Failed to fetch slap GIF.",
                        color=CONFIG['embed_colors']['error']
                    ))
            
            embed = Embed(
                description=f"**{ctx.author.mention}** **slaps** **{user.mention}** for the **{ordinal_count}** time!",
                color=await self.bot.color_manager.resolve(ctx.author.id)
            )
            embed.set_image(url=gif_url)
            embed.set_footer(text=f"From: {anime_name}")
            
            await ctx.send(embed=embed)

    @roleplay.command(
        name="hug",
        description="Hug someone"
    )
    @app_commands.describe(user="The user to hug")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def hug(self, ctx, user: Optional[Union[discord.Member, discord.User]] = None):
        """Hug someone"""
        user = user or ctx.author
        
        async with ctx.typing():
            ordinal_count = await self.update_count(ctx.author.id, user.id, "hug")
            
            async with self.session.get("https://nekos.best/api/v2/hug") as response:
                if response.status == 200:
                    data = await response.json()
                    gif_url = data['results'][0]['url']
                    anime_name = data['results'][0]['anime_name']
                else:
                    error_emoji = await self.bot.emojis.get("warning", "❌")
                    return await ctx.send(embed=Embed(
                        description=f"{error_emoji} {ctx.author.mention}: Failed to fetch hug GIF.",
                        color=CONFIG['embed_colors']['error']
                    ))
            
            embed = Embed(
                description=f"**{ctx.author.mention}** **hugs** **{user.mention}** for the **{ordinal_count}** time!",
                color=await self.bot.color_manager.resolve(ctx.author.id)
            )
            embed.set_image(url=gif_url)
            embed.set_footer(text=f"From: {anime_name}")
            
            await ctx.send(embed=embed)

    @roleplay.command(
        name="kiss",
        description="Kiss someone"
    )
    @app_commands.describe(user="The user to kiss")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def kiss(self, ctx, user: Optional[Union[discord.Member, discord.User]] = None):
        """Kiss someone"""
        user = user or ctx.author
        
        async with ctx.typing():
            ordinal_count = await self.update_count(ctx.author.id, user.id, "kiss")
            
            async with self.session.get("https://nekos.best/api/v2/kiss") as response:
                if response.status == 200:
                    data = await response.json()
                    gif_url = data['results'][0]['url']
                    anime_name = data['results'][0]['anime_name']
                else:
                    error_emoji = await self.bot.emojis.get("warning", "❌")
                    return await ctx.send(embed=Embed(
                        description=f"{error_emoji} {ctx.author.mention}: Failed to fetch kiss GIF.",
                        color=CONFIG['embed_colors']['error']
                    ))
            
            embed = Embed(
                description=f"**{ctx.author.mention}** **kisses** **{user.mention}** for the **{ordinal_count}** time!",
                color=await self.bot.color_manager.resolve(ctx.author.id)
            )
            embed.set_image(url=gif_url)
            embed.set_footer(text=f"From: {anime_name}")
            
            await ctx.send(embed=embed)

    @roleplay.command(
        name="bite",
        description="Bite someone"
    )
    @app_commands.describe(user="The user to bite")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def bite(self, ctx, user: Optional[Union[discord.Member, discord.User]] = None):
        """Bite someone"""
        user = user or ctx.author
        
        async with ctx.typing():
            ordinal_count = await self.update_count(ctx.author.id, user.id, "bite")
            
            async with self.session.get("https://nekos.best/api/v2/bite") as response:
                if response.status == 200:
                    data = await response.json()
                    gif_url = data['results'][0]['url']
                    anime_name = data['results'][0]['anime_name']
                else:
                    error_emoji = await self.bot.emojis.get("warning", "❌")
                    return await ctx.send(embed=Embed(
                        description=f"{error_emoji} {ctx.author.mention}: Failed to fetch bite GIF.",
                        color=CONFIG['embed_colors']['error']
                    ))
            
            embed = Embed(
                description=f"*Ouch!* **{ctx.author.mention}** **bites** **{user.mention}** for the **{ordinal_count}** time!",
                color=await self.bot.color_manager.resolve(ctx.author.id)
            )
            embed.set_image(url=gif_url)
            embed.set_footer(text=f"From: {anime_name}")
            
            await ctx.send(embed=embed)

    @roleplay.command(
        name="baka",
        description="Call someone a baka"
    )
    @app_commands.describe(user="The user to call baka")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def baka(self, ctx, user: Optional[Union[discord.Member, discord.User]] = None):
        """Call someone a baka"""
        user = user or ctx.author
        
        async with ctx.typing():
            ordinal_count = await self.update_count(ctx.author.id, user.id, "baka")
            
            async with self.session.get("https://nekos.best/api/v2/baka") as response:
                if response.status == 200:
                    data = await response.json()
                    gif_url = data['results'][0]['url']
                    anime_name = data['results'][0]['anime_name']
                else:
                    error_emoji = await self.bot.emojis.get("warning", "❌")
                    return await ctx.send(embed=Embed(
                        description=f"{error_emoji} {ctx.author.mention}: Failed to fetch baka GIF.",
                        color=CONFIG['embed_colors']['error']
                    ))
            
            embed = Embed(
                description=f"**{ctx.author.mention}** calls **{user.mention}** baka for the **{ordinal_count}** time!",
                color=await self.bot.color_manager.resolve(ctx.author.id)
            )
            embed.set_image(url=gif_url)
            embed.set_footer(text=f"From: {anime_name}")
            
            await ctx.send(embed=embed)

    @roleplay.command(
        name="cuddle",
        description="Cuddle with someone"
    )
    @app_commands.describe(user="The user to cuddle with")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def cuddle(self, ctx, user: Optional[Union[discord.Member, discord.User]] = None):
        """Cuddle with someone"""
        user = user or ctx.author
        
        async with ctx.typing():
            ordinal_count = await self.update_count(ctx.author.id, user.id, "cuddle")
            
            async with self.session.get("https://nekos.best/api/v2/cuddle") as response:
                if response.status == 200:
                    data = await response.json()
                    gif_url = data['results'][0]['url']
                    anime_name = data['results'][0]['anime_name']
                else:
                    error_emoji = await self.bot.emojis.get("warning", "❌")
                    return await ctx.send(embed=Embed(
                        description=f"{error_emoji} {ctx.author.mention}: Failed to fetch cuddle GIF.",
                        color=CONFIG['embed_colors']['error']
                    ))
            
            embed = Embed(
                description=f"**{ctx.author.mention}** **cuddles** **{user.mention}** for the **{ordinal_count}** time!",
                color=await self.bot.color_manager.resolve(ctx.author.id)
            )
            embed.set_image(url=gif_url)
            embed.set_footer(text=f"From: {anime_name}")
            
            await ctx.send(embed=embed)

    @roleplay.command(
        name="feed",
        description="Feed someone"
    )
    @app_commands.describe(user="The user to feed")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def feed(self, ctx, user: Optional[Union[discord.Member, discord.User]] = None):
        """Feed someone"""
        user = user or ctx.author
        
        async with ctx.typing():
            ordinal_count = await self.update_count(ctx.author.id, user.id, "feed")
            
            async with self.session.get("https://nekos.best/api/v2/feed") as response:
                if response.status == 200:
                    data = await response.json()
                    gif_url = data['results'][0]['url']
                    anime_name = data['results'][0]['anime_name']
                else:
                    error_emoji = await self.bot.emojis.get("warning", "❌")
                    return await ctx.send(embed=Embed(
                        description=f"{error_emoji} {ctx.author.mention}: Failed to fetch feed GIF.",
                        color=CONFIG['embed_colors']['error']
                    ))
            
            embed = Embed(
                description=f"**{ctx.author.mention}** **feeds** **{user.mention}** for the **{ordinal_count}** time!",
                color=await self.bot.color_manager.resolve(ctx.author.id)
            )
            embed.set_image(url=gif_url)
            embed.set_footer(text=f"From: {anime_name}")
            
            await ctx.send(embed=embed)

    @roleplay.command(
        name="handhold",
        description="Hold hands with someone"
    )
    @app_commands.describe(user="The user to hold hands with")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def handhold(self, ctx, user: Optional[Union[discord.Member, discord.User]] = None):
        """Hold hands with someone"""
        user = user or ctx.author
        
        async with ctx.typing():
            ordinal_count = await self.update_count(ctx.author.id, user.id, "handhold")
            
            async with self.session.get("https://nekos.best/api/v2/handhold") as response:
                if response.status == 200:
                    data = await response.json()
                    gif_url = data['results'][0]['url']
                    anime_name = data['results'][0]['anime_name']
                else:
                    error_emoji = await self.bot.emojis.get("warning", "❌")
                    return await ctx.send(embed=Embed(
                        description=f"{error_emoji} {ctx.author.mention}: Failed to fetch handhold GIF.",
                        color=CONFIG['embed_colors']['error']
                    ))
            
            embed = Embed(
                description=f"**{ctx.author.mention}** **holds hands with** **{user.mention}** for the **{ordinal_count}** time!",
                color=await self.bot.color_manager.resolve(ctx.author.id)
            )
            embed.set_image(url=gif_url)
            embed.set_footer(text=f"From: {anime_name}")
            
            await ctx.send(embed=embed)

    @roleplay.command(
        name="handshake",
        description="Shake hands with someone"
    )
    @app_commands.describe(user="The user to shake hands with")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def handshake(self, ctx, user: Optional[Union[discord.Member, discord.User]] = None):
        """Shake hands with someone"""
        user = user or ctx.author
        
        async with ctx.typing():
            ordinal_count = await self.update_count(ctx.author.id, user.id, "handshake")
            
            async with self.session.get("https://nekos.best/api/v2/handshake") as response:
                if response.status == 200:
                    data = await response.json()
                    gif_url = data['results'][0]['url']
                    anime_name = data['results'][0]['anime_name']
                else:
                    error_emoji = await self.bot.emojis.get("warning", "❌")
                    return await ctx.send(embed=Embed(
                        description=f"{error_emoji} {ctx.author.mention}: Failed to fetch handshake GIF.",
                        color=CONFIG['embed_colors']['error']
                    ))
            
            embed = Embed(
                description=f"**{ctx.author.mention}** **shakes hands with** **{user.mention}** for the **{ordinal_count}** time!",
                color=await self.bot.color_manager.resolve(ctx.author.id)
            )
            embed.set_image(url=gif_url)
            embed.set_footer(text=f"From: {anime_name}")
            
            await ctx.send(embed=embed)

    @roleplay.command(
        name="highfive",
        description="High five someone"
    )
    @app_commands.describe(user="The user to high five")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def highfive(self, ctx, user: Optional[Union[discord.Member, discord.User]] = None):
        """High five someone"""
        user = user or ctx.author
        
        async with ctx.typing():
            ordinal_count = await self.update_count(ctx.author.id, user.id, "highfive")
            
            async with self.session.get("https://nekos.best/api/v2/highfive") as response:
                if response.status == 200:
                    data = await response.json()
                    gif_url = data['results'][0]['url']
                    anime_name = data['results'][0]['anime_name']
                else:
                    error_emoji = await self.bot.emojis.get("warning", "❌")
                    return await ctx.send(embed=Embed(
                        description=f"{error_emoji} {ctx.author.mention}: Failed to fetch highfive GIF.",
                        color=CONFIG['embed_colors']['error']
                    ))
            
            embed = Embed(
                description=f"**{ctx.author.mention}** **high fives** **{user.mention}** for the **{ordinal_count}** time!",
                color=await self.bot.color_manager.resolve(ctx.author.id)
            )
            embed.set_image(url=gif_url)
            embed.set_footer(text=f"From: {anime_name}")
            
            await ctx.send(embed=embed)

    @roleplay.command(
        name="kick",
        description="Kick someone"
    )
    @app_commands.describe(user="The user to kick")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def kick(self, ctx, user: Optional[Union[discord.Member, discord.User]] = None):
        """Kick someone"""
        user = user or ctx.author
        
        async with ctx.typing():
            ordinal_count = await self.update_count(ctx.author.id, user.id, "kick")
            
            async with self.session.get("https://nekos.best/api/v2/kick") as response:
                if response.status == 200:
                    data = await response.json()
                    gif_url = data['results'][0]['url']
                    anime_name = data['results'][0]['anime_name']
                else:
                    error_emoji = await self.bot.emojis.get("warning", "❌")
                    return await ctx.send(embed=Embed(
                        description=f"{error_emoji} {ctx.author.mention}: Failed to fetch kick GIF.",
                        color=CONFIG['embed_colors']['error']
                    ))
            
            embed = Embed(
                description=f"**{ctx.author.mention}** **kicks** **{user.mention}** for the **{ordinal_count}** time!",
                color=await self.bot.color_manager.resolve(ctx.author.id)
            )
            embed.set_image(url=gif_url)
            embed.set_footer(text=f"From: {anime_name}")
            
            await ctx.send(embed=embed)

    @roleplay.command(
        name="pat",
        description="Pat someone"
    )
    @app_commands.describe(user="The user to pat")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def pat(self, ctx, user: Optional[Union[discord.Member, discord.User]] = None):
        """Pat someone"""
        user = user or ctx.author
        
        async with ctx.typing():
            ordinal_count = await self.update_count(ctx.author.id, user.id, "pat")
            
            async with self.session.get("https://nekos.best/api/v2/pat") as response:
                if response.status == 200:
                    data = await response.json()
                    gif_url = data['results'][0]['url']
                    anime_name = data['results'][0]['anime_name']
                else:
                    error_emoji = await self.bot.emojis.get("warning", "❌")
                    return await ctx.send(embed=Embed(
                        description=f"{error_emoji} {ctx.author.mention}: Failed to fetch pat GIF.",
                        color=CONFIG['embed_colors']['error']
                    ))
            
            embed = Embed(
                description=f"**{ctx.author.mention}** **pats** **{user.mention}** for the **{ordinal_count}** time!",
                color=await self.bot.color_manager.resolve(ctx.author.id)
            )
            embed.set_image(url=gif_url)
            embed.set_footer(text=f"From: {anime_name}")
            
            await ctx.send(embed=embed)

    @roleplay.command(
        name="punch",
        description="Punch someone"
    )
    @app_commands.describe(user="The user to punch")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def punch(self, ctx, user: Optional[Union[discord.Member, discord.User]] = None):
        """Punch someone"""
        user = user or ctx.author
        
        async with ctx.typing():
            ordinal_count = await self.update_count(ctx.author.id, user.id, "punch")
            
            async with self.session.get("https://nekos.best/api/v2/punch") as response:
                if response.status == 200:
                    data = await response.json()
                    gif_url = data['results'][0]['url']
                    anime_name = data['results'][0]['anime_name']
                else:
                    error_emoji = await self.bot.emojis.get("warning", "❌")
                    return await ctx.send(embed=Embed(
                        description=f"{error_emoji} {ctx.author.mention}: Failed to fetch punch GIF.",
                        color=CONFIG['embed_colors']['error']
                    ))
            
            embed = Embed(
                description=f"**{ctx.author.mention}** **punches** **{user.mention}** for the **{ordinal_count}** time!",
                color=await self.bot.color_manager.resolve(ctx.author.id)
            )
            embed.set_image(url=gif_url)
            embed.set_footer(text=f"From: {anime_name}")
            
            await ctx.send(embed=embed)

    @roleplay.command(
        name="peck",
        description="Peck someone"
    )
    @app_commands.describe(user="The user to peck")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def peck(self, ctx, user: Optional[Union[discord.Member, discord.User]] = None):
        """Peck someone"""
        user = user or ctx.author
        
        async with ctx.typing():
            ordinal_count = await self.update_count(ctx.author.id, user.id, "peck")
            
            async with self.session.get("https://nekos.best/api/v2/peck") as response:
                if response.status == 200:
                    data = await response.json()
                    gif_url = data['results'][0]['url']
                    anime_name = data['results'][0]['anime_name']
                else:
                    error_emoji = await self.bot.emojis.get("warning", "❌")
                    return await ctx.send(embed=Embed(
                        description=f"{error_emoji} {ctx.author.mention}: Failed to fetch peck GIF.",
                        color=CONFIG['embed_colors']['error']
                    ))
            
            embed = Embed(
                description=f"**{ctx.author.mention}** **pecks** **{user.mention}** for the **{ordinal_count}** time!",
                color=await self.bot.color_manager.resolve(ctx.author.id)
            )
            embed.set_image(url=gif_url)
            embed.set_footer(text=f"From: {anime_name}")
            
            await ctx.send(embed=embed)

    @roleplay.command(
        name="poke",
        description="Poke someone"
    )
    @app_commands.describe(user="The user to poke")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def poke(self, ctx, user: Optional[Union[discord.Member, discord.User]] = None):
        """Poke someone"""
        user = user or ctx.author
        
        async with ctx.typing():
            ordinal_count = await self.update_count(ctx.author.id, user.id, "poke")
            
            async with self.session.get("https://nekos.best/api/v2/poke") as response:
                if response.status == 200:
                    data = await response.json()
                    gif_url = data['results'][0]['url']
                    anime_name = data['results'][0]['anime_name']
                else:
                    error_emoji = await self.bot.emojis.get("warning", "❌")
                    return await ctx.send(embed=Embed(
                        description=f"{error_emoji} {ctx.author.mention}: Failed to fetch poke GIF.",
                        color=CONFIG['embed_colors']['error']
                    ))
            
            embed = Embed(
                description=f"**{ctx.author.mention}** **pokes** **{user.mention}** for the **{ordinal_count}** time!",
                color=await self.bot.color_manager.resolve(ctx.author.id)
            )
            embed.set_image(url=gif_url)
            embed.set_footer(text=f"From: {anime_name}")
            
            await ctx.send(embed=embed)

    @roleplay.command(
        name="shoot",
        description="Shoot someone"
    )
    @app_commands.describe(user="The user to shoot")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def shoot(self, ctx, user: Optional[Union[discord.Member, discord.User]] = None):
        """Shoot someone"""
        user = user or ctx.author
        
        async with ctx.typing():
            ordinal_count = await self.update_count(ctx.author.id, user.id, "shoot")
            
            async with self.session.get("https://nekos.best/api/v2/shoot") as response:
                if response.status == 200:
                    data = await response.json()
                    gif_url = data['results'][0]['url']
                    anime_name = data['results'][0]['anime_name']
                else:
                    error_emoji = await self.bot.emojis.get("warning", "❌")
                    return await ctx.send(embed=Embed(
                        description=f"{error_emoji} {ctx.author.mention}: Failed to fetch shoot GIF.",
                        color=CONFIG['embed_colors']['error']
                    ))
            
            embed = Embed(
                description=f"**{ctx.author.mention}** **shoots** **{user.mention}** for the **{ordinal_count}** time!",
                color=await self.bot.color_manager.resolve(ctx.author.id)
            )
            embed.set_image(url=gif_url)
            embed.set_footer(text=f"From: {anime_name}")
            
            await ctx.send(embed=embed)

    @roleplay.command(
        name="cry",
        description="Let it all out"
    )
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def cry(self, ctx):
        """Let it all out"""
        async with ctx.typing():
            ordinal_count = await self.update_count(ctx.author.id, ctx.author.id, "cry")
            
            async with self.session.get("https://nekos.best/api/v2/cry") as response:
                if response.status == 200:
                    data = await response.json()
                    gif_url = data['results'][0]['url']
                    anime_name = data['results'][0]['anime_name']
                else:
                    error_emoji = await self.bot.emojis.get("warning", "❌")
                    return await ctx.send(embed=Embed(
                        description=f"{error_emoji} {ctx.author.mention}: Failed to fetch cry GIF.",
                        color=CONFIG['embed_colors']['error']
                    ))
            
            embed = Embed(
                description=f"**{ctx.author.mention}** **cries** for the **{ordinal_count}** time!",
                color=await self.bot.color_manager.resolve(ctx.author.id)
            )
            embed.set_image(url=gif_url)
            embed.set_footer(text=f"From: {anime_name}")
            
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Roleplay(bot))