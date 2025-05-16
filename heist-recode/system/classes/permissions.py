import discord
from discord.ext import commands
from discord import app_commands
from typing import Union
from system.classes.db import Database
from system.classes.redis import RedisManager

class Permissions:
    footer = "heist.lol"
    
    @staticmethod
    async def _send_response(ctx: Union[commands.Context, discord.Interaction], message: str) -> None:
        if isinstance(ctx, discord.Interaction):
            if ctx.response.is_done():
                await ctx.followup.send(message, ephemeral=True)
            else:
                await ctx.response.send_message(message, ephemeral=True)
        else:
            await ctx.reply(message)

    @staticmethod
    async def is_owner(ctx: Union[commands.Context, discord.Interaction]) -> bool:
        if isinstance(ctx, discord.Interaction):
            user = ctx.user
            db = ctx.client.db if hasattr(ctx.client, 'db') else Database()
        else:
            user = ctx.author
            db = ctx.bot.db if hasattr(ctx, 'bot') else Database()
        
        is_owner = await db.check_owner(user.id)
        
        if not is_owner:
            await Permissions._send_response(ctx, f"<:warning:1350239604925530192> {user.mention}: You are not Heist staff.")
        return is_owner

    @staticmethod
    async def is_blacklisted(ctx: Union[commands.Context, discord.Interaction]) -> bool:
        if isinstance(ctx, discord.Interaction):
            user = ctx.user
            db = ctx.client.db if hasattr(ctx.client, 'db') else Database()
        else:
            user = ctx.author
            db = ctx.bot.db if hasattr(ctx, 'bot') else Database()
            is_blacklisted = await db.check_blacklisted(user.id)
            return not is_blacklisted
            
        is_blacklisted = await db.check_blacklisted(user.id)
        
        if is_blacklisted:
            async with db.pool.acquire() as conn:
                reason = await conn.fetchval(
                    "SELECT reason FROM blacklisted WHERE user_id = $1",
                    str(user.id))
                
            message = (
                f"You are blacklisted from using [Heist](<https://{Permissions.footer}>) "
                f"for **\"{reason}\"**.\n"
                f"# Wrongfully blacklisted? You may appeal [**here**](<https://discord.gg/6ScZFN3wPA>)."
            )
            await Permissions._send_response(ctx, message)
            
        if not is_blacklisted:
            return True
        return False

    @staticmethod
    async def is_donor(ctx: Union[commands.Context, discord.Interaction]) -> bool:
        if isinstance(ctx, discord.Interaction):
            user = ctx.user
            db = ctx.client.db if hasattr(ctx.client, 'db') else Database()
        else:
            user = ctx.author
            db = ctx.bot.db if hasattr(ctx, 'bot') else Database()
            
        is_donor = await db.check_donor(user.id)
        
        if not is_donor:
            message = "<:premium:1311062205650833509> This is a premium-only command. Run </premium buy:1278389799857946700> to learn more."
            await Permissions._send_response(ctx, message)
            return False
        return True

    @staticmethod
    async def is_booster(ctx: Union[commands.Context, discord.Interaction]) -> bool:
        if isinstance(ctx, discord.Interaction):
            user = ctx.user
            db = ctx.client.db if hasattr(ctx.client, 'db') else Database()
        else:
            user = ctx.author
            db = ctx.bot.db if hasattr(ctx, 'bot') else Database()
            
        is_booster = await db.check_booster(user.id)
        
        if not is_booster:
            message = "<:boosts:1263854701535821855> This is a booster-only command. Boost the server to access this feature!"
            await Permissions._send_response(ctx, message)
            return False
        return is_booster

    @staticmethod
    async def is_famous(ctx: Union[commands.Context, discord.Interaction]) -> bool:
        if isinstance(ctx, discord.Interaction):
            user = ctx.user
            db = ctx.client.db if hasattr(ctx.client, 'db') else Database()
        else:
            user = ctx.author
            db = ctx.bot.db if hasattr(ctx, 'bot') else Database()
            
        is_famous = await db.check_famous(user.id)
        
        if not is_famous:
            message = "This command is only available to famous users."
            await Permissions._send_response(ctx, message)
            return False
        return is_famous

    @staticmethod
    async def invalidate_cache(user_id: int, bot=None) -> None:
        redis = await bot.get_redis() if hasattr(bot, 'get_redis') else RedisManager()
        if hasattr(redis, 'initialize'):
            await redis.initialize()
            
        keys = [
            f"owner:{user_id}",
            f"blacklist:{user_id}",
            f"donor:{user_id}",
            f"booster:{user_id}",
            f"famous:{user_id}"
        ]
        await redis.redis.delete(*[redis.key(k) for k in keys])

    @staticmethod
    async def is_disabled(ctx: Union[commands.Context, discord.Interaction]) -> bool:
        if isinstance(ctx, discord.Interaction):
            user = ctx.user
        else:
            user = ctx.author
            
        creator_ids = ["123"]
        if str(user.id) not in creator_ids:
            message = "This command is temporarily disabled."
            await Permissions._send_response(ctx, message)
            return False
        return True

    @staticmethod
    async def is_creator(ctx: Union[commands.Context, discord.Interaction]) -> bool:
        if isinstance(ctx, discord.Interaction):
            user = ctx.user
        else:
            user = ctx.author
            
        creator_ids = ["1326213864391442504", "935448935777050645", "1363295564133040272"]
        if str(user.id) not in creator_ids:
            message = "This command is not available to you."
            await Permissions._send_response(ctx, message)
            self.logger.debug(f"User {user.id} attempted to use a creator-only command.")
            return False
        return True
        self.logger.debug(f"User {user.id} is a creator.")

    @staticmethod
    async def is_bloxlink_staff(ctx: Union[commands.Context, discord.Interaction]) -> bool:
        if isinstance(ctx, discord.Interaction):
            user = ctx.user
        else:
            user = ctx.author
            
        bstaff_ids = ["84117866944663552"]
        if str(user.id) in bstaff_ids:
            message = "This command is disabled."
            await Permissions._send_response(ctx, message)
            return False
        return True

    @staticmethod
    async def is_tester(ctx: Union[commands.Context, discord.Interaction]) -> bool:
        if isinstance(ctx, discord.Interaction):
            user = ctx.user
        else:
            user = ctx.author
            
        tester_ids = ["1326213864391442504", "249837467128037376"]
        if str(user.id) not in tester_ids:
            message = "This command is still in testing."
            await Permissions._send_response(ctx, message)
            return False
        return True

    @staticmethod
    async def is_ecorework(ctx: Union[commands.Context, discord.Interaction]) -> bool:
        if isinstance(ctx, discord.Interaction):
            user = ctx.user
            db = ctx.client.db if hasattr(ctx.client, 'db') else Database()
        else:
            user = ctx.author
            db = ctx.bot.db if hasattr(ctx, 'bot') else Database()
            
        is_owner = await db.check_owner(user.id)
        if not is_owner:
            message = "This will be available next economy reset."
            await Permissions._send_response(ctx, message)
            return False
        return is_owner