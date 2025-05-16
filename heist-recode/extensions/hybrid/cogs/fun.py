import discord
import time
import base64
import random
import aiohttp
import asyncio
import io
import os
from io import BytesIO
from discord import app_commands, File, Embed, Interaction
from discord.ext import commands
from discord.ext.commands import Cog, hybrid_command
from typing import Optional
from system.classes.permissions import Permissions

class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        if self.session and not self.session.closed:
            await self.session.close()

    @hybrid_command(
        name="howgay",
        description="Check how gay someone is",
        aliases=["gayrate"]
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(user="The user you want to check the gayness of")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def howgay(self, ctx: commands.Context, user: Optional[discord.User] = None):
        user = user or ctx.author
        
        if user.id == 1363295564133040272:
            await ctx.send("cosmin is NOT gay 😭🙏🏿")
            return
    
        rgay = random.randint(1, 100)
        gay = rgay / 1.17

        emoji = (
            "🏳️‍🌈" if gay > 75 else
            "🤑" if gay > 50 else
            "🤫" if gay > 25 else
            "🔥"
        )

        await ctx.send(
            f"**{user.name}** is **{gay:.2f}%** gay {emoji}"
        )

    @hybrid_command(
        name="howautistic",
        description="Check how autistic someone is",
        aliases=["autisticrate"]
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(user="The user you want to check the autism of")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def howautistic(self, ctx: commands.Context, user: Optional[discord.User] = None):
        user = user or ctx.author

        if user.id == 1363295564133040272:
            await ctx.send("cosmin is NOT autistic 😭🙏🏿")
            return

        rautistic = random.randint(1, 100)
        autistic = rautistic / 1.17

        emoji = (
            "🧩" if autistic > 75 else
            "🧠" if autistic > 50 else
            "🤐" if autistic > 25 else
            "🔥"
        )

        await ctx.send(
            f"**{user.name}** is **{autistic:.2f}%** autistic {emoji}"
        )

    @hybrid_command(
        name="ppsize",
        description="Check the size of someone's pp",
        aliases=["pp"]
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(user="The user you want to check the pp size of")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def ppsize(self, ctx: commands.Context, user: Optional[discord.User] = None):
        user = user or ctx.author

        length = random.randint(1, 20)
        pp = "=" * length
        emoji = "D"
        
        await ctx.send(
            f"**{user.name}**'s pp:\n**`8{pp}{emoji}`**"
        )

async def setup(bot):
    await bot.add_cog(Fun(bot))