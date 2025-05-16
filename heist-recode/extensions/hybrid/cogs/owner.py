import discord
import platform
import time
import asyncio
import os
from discord import ui
from discord.ui import View, button
from discord import (app_commands, Interaction, User, NotFound, HTTPException, ButtonStyle, Button, Embed)
from discord.ext import commands
from discord.ext.commands import (Cog, hybrid_command)
from system.classes.permissions import Permissions
from typing import Optional
from PIL import Image
import io
import aiohttp
from system.classes.logger import Logger

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.logger = Logger()
        self._redis = None

    async def cog_load(self):
        self._redis = await self.bot.get_redis()

    async def cog_unload(self):
        await self.session.close()

    admin = app_commands.Group(
        name="o", 
        description="Staff only commands",
        allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=False, private_channel=True),
        allowed_installs=app_commands.AppInstallationType(guild=True, user=True)
    )

    @admin.command()
    @app_commands.allowed_installs(guilds=False, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(action="Either add or remove a user from the blacklist.", user="The user to apply the action to.", reason="Optional reason of the action.")
    @app_commands.check(Permissions.is_owner)
    async def blacklist(self, interaction: Interaction, action: str, user: User = None, reason: str = f"Breaking [Heist's Terms of Service](<https://heist.lol/terms>)."):
        """Add or remove a user from the blacklist."""
        await interaction.response.defer(thinking=True)
        user = user or interaction.user
        user_id = str(user.id)

        if action == "add":
            await self.update_blacklist(user_id, "add", reason)
            await Permissions.invalidate_cache(user_id)

            embed = Embed(
                title="<:warning:1350239604925530192> Notice",
                description=f"You have been **blacklisted** from using [**Heist**](<https://heist.lol>).\nReason: **{reason}**\n\nIf you think this decision is wrong, you may appeal [**here**](https://discord.gg/gVarzmGAJC).",
                color=0x3b3b3b
            )
            embed.set_footer(text="heist.lol", icon_url="https://git.cursi.ng/heist.png?c")

            try:
                await user.send(embed=embed)
            except Exception as e:
                pass

            await interaction.followup.send(f"{user} has been blacklisted.", ephemeral=False)
        
        elif action == "remove":
            await self.update_blacklist(user_id, "remove")
            await Permissions.invalidate_cache(user_id)

            embed = Embed(
                title="<:warning:1350239604925530192> Notice",
                description=f"You have been **unblacklisted** from using [**Heist**](<https://heist.lol>).",
                color=0x3b3b3b
            )
            embed.set_footer(text="heist.lol", icon_url="https://git.cursi.ng/heist.png?c")

            try:
                await user.send(embed=embed)
            except Exception as e:
                pass

            await interaction.followup.send(f"{user} has been unblacklisted.", ephemeral=False)
        
        elif action == "removeall":
            blacklisted_users = await self.get_blacklisted_users()

            for blacklisted_user_id in blacklisted_users:
                await self.update_blacklist(blacklisted_user_id, "remove")

                try:
                    user = await self.client.fetch_user(blacklisted_user_id)
                    embed = Embed(
                        title="<:warning:1350239604925530192> Notice",
                        description=f"You have been **unblacklisted** from using Heist.\nReason: **Everyone has been unblacklisted.**\n-# Allow up to 5 minutes for this to process.",
                        color=0x3b3b3b
                    )
                    embed.set_footer(text="heist.lol", icon_url="https://git.cursi.ng/heist.png?c")
                    await user.send(embed=embed)
                except Exception as e:
                    print(e)

            await interaction.followup.send("All users have been unblacklisted.", ephemeral=False)

        else:
            await interaction.followup.send("Invalid action. Use `add`, `remove`, or `removeall`.", ephemeral=True)

    async def get_blacklisted_users(self):
        async with self.bot.db.pool.acquire() as conn:
            result = await conn.fetch('SELECT user_id FROM blacklisted')
            return [user['user_id'] for user in result]

    async def update_blacklist(self, user_id, action, reason=None):
        user_id_str = str(user_id)
        if action == "add":
            await self.bot.db.pool.execute(
                'INSERT INTO blacklisted (user_id, reason) VALUES ($1, $2) '
                'ON CONFLICT (user_id) DO UPDATE SET reason = EXCLUDED.reason',
                user_id_str, reason
            )
            await self._redis.redis.setex(f"blacklisted:{user_id_str}", 300, "True")
        elif action == "remove":
            await self.bot.db.pool.execute(
                'DELETE FROM blacklisted WHERE user_id = $1',
                user_id_str
            )
            await self._redis.redis.setex(f"blacklisted:{user_id_str}", 300, "False")

    async def update_user_status(self, user_id, status_type, action):
        user_id_str = str(user_id)
        if status_type == "premium":
            if action == "add":
                await self.bot.db.pool.execute(
                    'INSERT INTO donors (user_id, donor_status) VALUES ($1, 1) '
                    'ON CONFLICT (user_id) DO NOTHING',
                    user_id_str
                )
                await self._redis.redis.setex(f"donor:{user_id_str}", 300, "True")
                self.logger.info(f"Added premium status to user {user_id_str}")
            elif action == "remove":
                await self.bot.db.pool.execute(
                    'DELETE FROM donors WHERE user_id = $1',
                    user_id_str
                )
                await self._redis.redis.setex(f"donor:{user_id_str}", 300, "False")
                self.logger.info(f"Removed premium status from user {user_id_str}")
        elif status_type == "famous":
            if action == "add":
                await self.bot.db.pool.execute(
                    'UPDATE user_data SET fame = TRUE WHERE user_id = $1 AND fame IS FALSE',
                    user_id_str
                )
                await self._redis.redis.setex(f"famous:{user_id_str}", 300, "True")
            elif action == "remove":
                await self.bot.db.pool.execute(
                    'UPDATE user_data SET fame = FALSE WHERE user_id = $1 AND fame IS TRUE',
                    user_id_str
                )
                await self._redis.redis.setex(f"famous:{user_id_str}", 300, "False")

    async def update_admin(self, user_id, action):
        self.logger.debug(f"Updating admin status for user {user_id} with action {action}")
        user_id_str = str(user_id)
        if action == "add":
            await self.bot.db.pool.execute(
                'INSERT INTO owners (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING',
                user_id_str
            )
            await self._redis.redis.setex(f"owner:{user_id_str}", 300, "True")
            self.logger.info(f"Added user {user_id_str} to owners.")
        elif action == "remove":
            await self.bot.db.pool.execute(
                'DELETE FROM owners WHERE user_id = $1',
                user_id_str
            )
            await self._redis.redis.setex(f"owner:{user_id_str}", 300, "False")
            self.logger.info(f"Removed user {user_id_str} from owners.")

    @admin.command()
    @app_commands.allowed_installs(guilds=False, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.check(Permissions.is_owner)
    @app_commands.describe(action="Either add or remove status.", status="The status to apply.", user="The user to apply the action to.")
    @app_commands.choices(status=[
        app_commands.Choice(name="Premium", value="premium"),
        app_commands.Choice(name="Famous", value="famous"),
        app_commands.Choice(name="Trusted", value="trusted")
    ])
    async def grant(self, interaction: Interaction, action: str, status: str, user: User = None):
        """Grant or remove status from someone."""
        await interaction.response.defer(thinking=True)
        user = user or interaction.user
        user_id = str(user.id)

        loading_message = await interaction.followup.send(f"<a:loading:1269644867047260283> {interaction.user.mention}: please wait, this might take a while..", ephemeral=True)

        if action == "add":
            await self.update_user_status(user_id, status, "add")
            await Permissions.invalidate_cache(user_id)

            if status == "premium":
                embed = Embed(
                    title="<:warning:1350239604925530192> Notice",
                    description=f"You have been given **Premium** status on Heist.\nThank you for your donation!\n\nMake sure to join our [**Discord server**](https://discord.gg/gVarzmGAJC) to claim more perks.",
                    color=0x3b3b3b
                )
                embed.set_footer(text="heist.lol", icon_url="https://git.cursi.ng/heist.png?c")

                try:
                    await user.send(embed=embed)
                except Exception as e:
                    pass

                await loading_message.edit(content=f"<:premium:1311062205650833509> {user} has been given premium status.")

            elif status == "famous":
                try:
                    await user.send("You have been granted <:famous:1311067416251596870> **`Famous`** on Heist.")
                except Exception as e:
                    pass

                await loading_message.edit(content=f"<:famous:1311067416251596870> {user} has been given famous status.")

            elif status == "trusted":
                limited_key = f"user:{user_id}:limited"
                untrusted_key = f"user:{user_id}:untrusted"
                await self.redis.delete(limited_key)
                await self.redis.delete(untrusted_key)

                await loading_message.edit(content=f"<:trusted:1311067416251596870> {user} is now trusted.")

        elif action == "remove":
            await self.update_user_status(user_id, status, "remove")
            await Permissions.invalidate_cache(user_id)

            if status == "premium":
                embed = Embed(
                    title="<:warning:1350239604925530192> Notice",
                    description=f"Your **Premium** status has been removed on Heist.\n\nThis was unexpected? Make a ticket [**here**](https://discord.gg/gVarzmGAJC).",
                    color=0x3b3b3b
                )
                embed.set_footer(text="heist.lol", icon_url="https://git.cursi.ng/heist.png?c")

                try:
                    await user.send(embed=embed)
                except Exception as e:
                    pass

                await loading_message.edit(content=f"<:premium:1311062205650833509> {user} no longer has premium status.")

            elif status == "famous":
                try:
                    await user.send("Your <:famous:1311067416251596870> **`Famous`** has been removed on Heist.")
                except Exception as e:
                    pass

                await loading_message.edit(content=f"<:famous:1311067416251596870> {user} no longer has famous status.")

            elif status == "trusted":
                limited_key = f"user:{user_id}:limited"
                untrusted_key = f"user:{user_id}:untrusted"
                await self.redis.setex(limited_key, 7 * 24 * 60 * 60, '')
                await self.redis.setex(untrusted_key, 60 * 24 * 60 * 60, '')
                await loading_message.edit(content=f"<:trusted:1311067416251596870> {user} is no longer trusted.")

        else:
            await interaction.followup.send("Invalid action. Use `add` or `remove`.", ephemeral=True)

    @admin.command()
    @app_commands.allowed_installs(guilds=False, users=True)
    @app_commands.allowed_contexts(guilds=False, dms=True, private_channels=True)
    @app_commands.check(Permissions.is_creator)
    @app_commands.describe(action="Either add or remove a user as admin.", user="The user to apply the action to.")
    async def staff(self, interaction: Interaction, action: str, user: User = None):
        """Add or remove a user as Heist staff."""
        user = user or interaction.user
        user_id = str(user.id)

        try:
            if action == "add":
                await self.update_admin(user_id, "add")
                await Permissions.invalidate_cache(user_id)
                await interaction.response.send_message(f"{user} is now admin.", ephemeral=True)
            elif action == "remove":
                await self.update_admin(user_id, "remove")
                await Permissions.invalidate_cache(user_id)
                await interaction.response.send_message(f"{user} is no longer admin.", ephemeral=True)
            else:
                await interaction.response.send_message("Invalid action. Use `add` or `remove`.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
            self.logger.error(f"Error in staff command: {e}")

async def setup(bot):
    await bot.add_cog(Owner(bot))