import uvloop
import asyncio
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
import os
import random
import string
import time
import asyncpg
import aiohttp
import uvloop
import traceback
import discord
import tuuid
from discord import Intents, CustomActivity, Embed, Interaction, app_commands
from discord.ext import commands
from discord.ext.commands import AutoShardedBot, errors, Command, MissingPermissions, BotMissingPermissions, CommandNotFound
from discord.utils import utcnow
from system.classes.db import Database
from system.classes.color import ColorManager
from system.classes.permissions import Permissions
from pathlib import Path
from system.classes.logger import Logger
from system.classes.emojis import EmojiManager
from system.classes.github import GitHubWebhook
from data.config import CONFIG
from asyncio import gather
from datetime import datetime, timedelta
from system.classes.tiktok import TikTok
from .patches import Help
from system.classes.redis import RedisManager
from system.classes.socials import SocialsManager
from typing import Optional, Dict

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_RETAIN"] = "True"

class Heist(AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=CONFIG['prefix'],
            owner_ids=CONFIG['owners'],
            activity=CustomActivity(name="🔗 heist.lol/discord"),
            intents=Intents.all(),
            help_command=Help(command_attrs={"aliases": ["h", "cmds"]}),
        )
        self.config = CONFIG
        self.logger = Logger()
        self._db_instance = None
        self._redis_instance = None
        self.permissions = None
        self.color_manager = None
        self._user_register_lock = asyncio.Lock()
        self.start_time = time.perf_counter()
        self.warn_emoji = "⚠️"
        self.tree.interaction_check = self.interaction_check
        self.before_invoke(self.before_invoke_handler)
        self._emoji_manager = None
        self.tiktok = TikTok(self)

    @property
    def db(self):
        if self._db_instance is None:
            raise RuntimeError("Database not initialized. Call await bot.initialize_db() first")
        return self._db_instance

    @property
    def redis(self):
        if self._redis_instance is None:
            raise RuntimeError("Redis not initialized. Call await bot.initialize_redis() first")
        return self._redis_instance

    async def initialize_db(self):
        if self._db_instance is None:
            self._db_instance = Database()
            await self._db_instance.initialize()

    async def initialize_redis(self):
        if self._redis_instance is None:
            self._redis_instance = RedisManager()
            await self._redis_instance.initialize()

    @property
    def emojis(self):
        if self._emoji_manager is None:
            self._emoji_manager = EmojiManager(self)
        return self._emoji_manager

    async def run(self):
        await super().start(self.config['token'], reconnect=True)
             
    async def __load(self, cog: str):
        try:
            await self.load_extension(cog)
            self.logger.info(f"Loaded {cog}")
        except errors.ExtensionAlreadyLoaded:
            pass
        except Exception as e:
            tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            self.logger.info(f"Failed to load {cog} due to exception: {tb}")
        
    async def _load_global_cooldown_lua(self):
        """Load the Lua script for global cooldowns"""
        lua_script = """
        local key = KEYS[1]
        local cooldown = tonumber(ARGV[1])
        local now = redis.call('TIME')[1]
        local last_used = redis.call('GET', key)
        
        if last_used then
            local remaining = cooldown - (now - tonumber(last_used))
            if remaining > 0 then
                return remaining
            end
        end
        
        redis.call('SET', key, now)
        redis.call('EXPIRE', key, cooldown)
        return 0
        """
        redis = await self.get_redis()
        return redis.redis.register_script(lua_script)
        
    async def check_global_cooldown(self, user_id: int) -> Optional[int]:
        """
        Check if user is on global cooldown
        Returns remaining seconds if on cooldown, None if not
        """
        if user_id in self.config['owners']:
            return None
            
        redis = await self.get_redis()
        key = redis.key(f"global_cooldown:{user_id}")
        
        cooldown = 3
        
        try:
            remaining = await self._global_cooldown_lua(
                keys=[key],
                args=[str(cooldown)]
            )
            return int(remaining) if remaining > 0 else None
        except Exception as e:
            self.logger.error(f"Error checking global cooldown: {e}")
            return None

    async def load_cogs(self):
        tasks = []
        extensions_dir = Path("extensions")
        if extensions_dir.exists():
            for category in ["userapp", "hybrid", "prefix"]:
                category_dir = extensions_dir / category / "cogs"
                if category_dir.exists():
                    for cog_file in category_dir.glob("*.py"):
                        if cog_file.name != "__init__.py":
                            cog_path = f"extensions.{category}.cogs.{cog_file.stem}"
                            tasks.append(self.__load(cog_path))
        if tasks:
            await gather(*tasks)
        
    async def setup_hook(self) -> None:
        await self.initialize_db()
        await self.initialize_redis()
        self.color_manager = ColorManager(self.db)
        self._global_cooldown_lua = await self._load_global_cooldown_lua()
        self.session = aiohttp.ClientSession()
        self.socials = SocialsManager(self.session)
        await self.emojis.initialize()
        self.warn_emoji = await self.emojis.get("warning", "⚠️")
        self.github = GitHubWebhook(self)
        await self.github.initialize()
        await self.load_cogs()
        try:
            await self.load_extension("jishaku")
            self.logger.info("Loaded jishaku")
        except Exception as e:
            self.logger.error(f"Failed to load jishaku: {e}")
        
    async def on_ready(self):
        try:
            synced = await self.tree.sync()
            self.logger.info(f"[MAIN] Synced {len(synced)} command(s)")
        except Exception as e:
            self.logger.error(f"[MAIN] Failed to sync command tree: {e}")
        self.logger.info(f"[MAIN] Logged in as {self.user.name}")
        uptime_emoji = await self.emojis.get('uptime')
        if channel := self.get_channel(1367923699403198604):
            elapsed = time.perf_counter() - self.start_time
            embed = discord.Embed(
                description=f"{uptime_emoji} <@1366081033853862038>: Instance took `{int(elapsed)} seconds` to start and is now online!",
                color=discord.Color.green()
            )
            await channel.send(embed=embed)

    async def _generate_error_code(self) -> str:
        chars = string.ascii_uppercase + string.digits + string.ascii_lowercase + tuuid.tuuid()
        return ''.join(await self.loop.run_in_executor(
            None,
            lambda: random.choices(chars, k=12)
        ))

    async def _send_error_report(self, error_code: str, error: Exception, command_name: str, user: discord.User) -> None:
        error_channel = self.get_channel(self.config['channels']['errors'])
        if not error_channel:
            return
        
        tb = await self.loop.run_in_executor(
            None,
            traceback.format_exception,
            type(error),
            error,
            error.__traceback__
        )
        tb = "".join(tb)
        
        embed = Embed(
            title=f"Error Report | {error_code}",
            color=self.config['embed_colors']['error']
        )
        
        embed.add_field(name="Command", value=f"```{command_name}```", inline=True)
        embed.add_field(name="User", value=f"```{user} ({user.id})```", inline=True)
        embed.add_field(name="Error", value=f"```py\n{tb[:1000]}```", inline=False)
        await error_channel.send(embed=embed)
        self.logger.error(tb)

    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
            
        if isinstance(error, commands.MissingPermissions):
            return await ctx.warning("You lack permissions to use this command.")
        
        if isinstance(error, commands.BotMissingPermissions):
            return await ctx.warning("I lack permissions to use this command.")
        
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send_help(ctx.command)
        
        if isinstance(error, commands.MissingRequiredAttachment):
            return await ctx.warning("You are missing an attachment!")
            
        if isinstance(error, (commands.CheckFailure, commands.CommandNotFound)):
            return
        
        if isinstance(error, commands.CommandOnCooldown):
            return
        
        error = getattr(error, 'original', error)
        error_code = await self._generate_error_code()
        code = f"`{error_code}`"
        
        warn = await self.emojis.get("warning", self.warn_emoji)
        embed = Embed(
            description=f"{warn} {ctx.author.mention}: Error occurred while performing command `{ctx.command.name}`\nUse the given error code to report it to the developers in the [`support server`](https://heist.lol/discord)",
            color=self.config['embed_colors']['error']
        )
        
        try:
            if hasattr(ctx, 'interaction') and ctx.interaction:
                try:
                    if not ctx.interaction.response.is_done():
                        await ctx.interaction.response.send_message(code, embed=embed)
                    else:
                        await ctx.interaction.followup.send(code, embed=embed)
                except (discord.NotFound, discord.HTTPException):
                    await ctx.send(code, embed=embed)
            else:
                await ctx.send(code, embed=embed)
        except Exception as e:
            self.logger.error(f"Failed to send error message: {e}")
            
        await self._send_error_report(error_code, error, ctx.command.name, ctx.author)

    async def on_error(self, event, *args, **kwargs):
        error = traceback.format_exc()
        self.logger.error(f"Event error in {event}: {error}")

    async def on_application_command_error(self, interaction: Interaction, error):
        if isinstance(error, app_commands.CommandNotFound):
            return
        
        error = getattr(error, 'original', error)
        error_code = await self._generate_error_code()
        code = f"`{error_code}`"
        
        warn = await self.emojis.get("warning", self.warn_emoji)
        embed = Embed(
            description=f"{warn} {interaction.user.mention}: Error occurred while performing command `{interaction.command.name}`\nUse the error code `{error_code}` to report it to the developers in the [`support server`](https://heist.lol/discord)",
            color=self.config['embed_colors']['error']
        )
        
        if not interaction.response.is_done():
            await interaction.response.send_message(code, embed=embed)
        else:
            await interaction.followup.send(code, embed=embed)
            
        await self._send_error_report(error_code, error, interaction.command.name, interaction.user)

    async def get_redis(self):
        """Proper async method to get Redis instance"""
        if not hasattr(self, '_redis_instance') or self._redis_instance is None:
            self._redis_instance = RedisManager()
            await self._redis_instance.initialize()
        return self._redis_instance

    async def _register_if_needed(self, user_id: int, username: str, display_name: str) -> None:
        async with self._user_register_lock:
            redis = await self.get_redis()
            redis_key = redis.key(f"user:{user_id}:exists")
            user_exists_in_cache = await redis.redis.get(redis_key)

            if not user_exists_in_cache:
                db = self.db
                async with db.pool.acquire() as conn:
                    user_exists = await conn.fetchval(
                        "SELECT 1 FROM user_data WHERE user_id = $1",
                        str(user_id))
                    if not user_exists:
                        await conn.execute("""
                            INSERT INTO user_data (user_id, username, displayname)
                            VALUES ($1, $2, $3)
                            ON CONFLICT (user_id) DO NOTHING
                        """, str(user_id), username, display_name)
                        limited_key = redis.key(f"user:{user_id}:limited")
                        await redis.redis.setex(limited_key, 7 * 24 * 60 * 60, '')
                        untrusted_key = redis.key(f"user:{user_id}:untrusted")
                        await redis.redis.setex(untrusted_key, 60 * 24 * 60 * 60, '')
                        self.logger.info(f"[DB] Registered new user: {username} ({user_id})")
                    await redis.redis.setex(redis_key, 600, '1')

    async def interaction_check(self, interaction: Interaction) -> bool:
        asyncio.create_task(self._register_if_needed(
            interaction.user.id,
            interaction.user.name,
            interaction.user.display_name
        ))
        return True

    async def before_invoke_handler(self, ctx):
        if not ctx.interaction and ctx.prefix and ctx.command:
            remaining = await self.check_global_cooldown(ctx.author.id)
            if remaining is not None:
                fseconds = "seconds" if remaining > 1 else "second"
                embed = Embed(
                    description=f"⌚ Getting ahead of the clock! Please wait **{remaining} {fseconds}**.",
                    color=self.config['embed_colors']['error']
                )
                try:
                    await ctx.send(embed=embed)
                except:
                    pass
                raise commands.CommandOnCooldown(ctx.command, remaining, ctx.command)

        asyncio.create_task(self._register_if_needed(
            ctx.author.id,
            ctx.author.name,
            ctx.author.display_name
        ))
        ctx._interaction_handled = False
        if ctx.interaction and not ctx.interaction.response.is_done():
            try:
                if not ctx.guild:
                    await ctx.interaction.response.defer()
                    ctx._interaction_handled = True
                else:
                    if not ctx.guild.me.guild_permissions.embed_links or not ctx.guild.me.guild_permissions.attach_files:
                        await ctx.interaction.response.defer(ephemeral=True)
                    else:
                        await ctx.interaction.response.defer()
                    ctx._interaction_handled = True
            except discord.errors.NotFound:
                self.logger.debug(f"Could not defer interaction for {ctx.author} - interaction expired")
            except Exception as e:
                self.logger.debug(f"Error deferring interaction: {e}")