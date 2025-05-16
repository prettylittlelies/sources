import discord
import platform
import time
import asyncio
import os
from discord import ui
from discord.ui import View, button
from discord.ext import commands
from discord import (app_commands, NotFound, HTTPException, ButtonStyle, Button, Embed)
from discord.ext.commands import (Cog, hybrid_command)
from system.classes.permissions import Permissions
from data.config import CONFIG
from typing import Optional
import aiohttp

class TestButton(discord.ui.Button):
    async def callback(self, interaction):
        await interaction.response.send_message('t')

class TestContainer(discord.ui.Container):
    text1 = discord.ui.TextDisplay("Hello world")
    text2 = discord.ui.TextDisplay("Row 3", row=2)

    section = discord.ui.Section(
        accessory=TestButton(
            label="Section Button",
        )
    ).add_item(discord.ui.TextDisplay("Text in a section"))

class TestView(discord.ui.LayoutView):
    container = TestContainer(id=1)

class Info(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.LASTFM_KEY = CONFIG.get('LASTFM_API_KEY')
        self.HEIST_KEY = CONFIG.get('HEIST_API_KEY')
        
    @hybrid_command(
        name="invite",
        description="Authorize the bot."
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def invite(self, ctx):
        invite = "https://discord.com/oauth2/authorize?client_id=1225070865935368265"
        view = discord.ui.View()
        button = discord.ui.Button(label="invite", url=invite, style=discord.ButtonStyle.link)
        view.add_item(button)
        await ctx.send(view=view)

    @hybrid_command(
        name="about",
        aliases=["info", "bi", "botinfo"],
        description="View information about the bot"
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def about(self, ctx):
        total_members = sum(g.member_count for g in self.bot.guilds)
        text_channels = sum(len(g.text_channels) for g in self.bot.guilds)
        voice_channels = sum(len(g.voice_channels) for g in self.bot.guilds)
        category_count = sum(len(g.categories) for g in self.bot.guilds)

        def count_lines_of_code(directory):
            total_lines = 0
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(".py"):
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            total_lines += sum(1 for _ in f)
            return total_lines

        project_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        total_lines_of_code = count_lines_of_code(project_directory)

        embed = Embed(
            color=await self.bot.color_manager.resolve(ctx.author.id),
        )
        embed.set_author(
            name=f"{self.bot.user.name}",
            icon_url=self.bot.user.display_avatar.url
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        info = f"Premium multi-purpose discord bot made by the [**Heist Team**](https://heist.lol)\n"
        info += f"Used by **{len([m for m in self.bot.users if not m.bot]):,}** members in **{len(self.bot.guilds):,}** servers on **{self.bot.shard_count or 1}** shards"
        embed.description = info

        members = (
            f"> **Total:** {total_members:,}\n"
            f"> **Human:** {len([m for m in self.bot.users if not m.bot]):,}\n"
            f"> **Bots:** {len([m for m in self.bot.users if m.bot]):,}"
        )
        
        channels = (
            f"> **Text:** {text_channels:,}\n"
            f"> **Voice:** {voice_channels:,}\n"
            f"> **Categories:** {category_count:,}"
        )

        system = (
            f"> **Commands:** {len(self.bot.commands):,}\n"
            f"> **Discord.py:** {discord.__version__}\n"
            f"> **Lines of code:** {total_lines_of_code:,}"
        )

        embed.add_field(name="Members", value=members, inline=True)
        embed.add_field(name="Channels", value=channels, inline=True)
        embed.add_field(name="System", value=system, inline=True)
        
        view = View()
        view.add_item(discord.ui.Button(
            style=ButtonStyle.link,
            url="https://discord.com/oauth2/authorize?client_id=1366081033853862038",
            emoji=await self.bot.emojis.get('link'),
            label="Authorize"
        ))
        view.add_item(discord.ui.Button(
            style=ButtonStyle.link,
            url="https://heist.lol/discord",
            emoji=await self.bot.emojis.get('link'),
            label="Support"
        ))
        view.add_item(discord.ui.Button(
            style=ButtonStyle.link,
            url="https://github.com/HeistIndustries",
            emoji=await self.bot.emojis.get('link'),
            label="Github"
        ))
        await ctx.send(embed=embed, view=view)

    @app_commands.command(name="me", description="View your Heist info")
    @app_commands.allowed_installs(guilds=False, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(
        user="Lookup Heist user by Discord ID",
        uid="Lookup user by Heist UID"
    )
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def me(self, interaction: discord.Interaction, uid: Optional[str] = None, user: Optional[discord.User] = None):
        if uid and user:
            await interaction.response.send_message("You cannot use both the UID and User parameters.", ephemeral=True)
            return

        await interaction.response.defer()

        if uid:
            if not uid.isdigit():
                await interaction.followup.send("The provided UID is not a valid integer.", ephemeral=True)
                return
            if uid == "0":
                uid = "1"
            user_id = await self.bot.db.fetchval("SELECT user_id FROM user_data WHERE hid = $1", int(uid))
            if not user_id:
                await interaction.followup.send("This HID does not belong to anyone.", ephemeral=True)
                return
            try:
                user = await self.bot.fetch_user(int(user_id))
            except:
                await interaction.followup.send("Could not fetch user information.", ephemeral=True)
                return
        elif user:
            user_id = str(user.id)
            hid = await self.bot.db.fetchval("SELECT hid FROM user_data WHERE user_id = $1", user_id)
            if not hid:
                await interaction.followup.send("User is not in Heist's database. <:angry:1311402645780434994>", ephemeral=True)
                return
        else:
            user = interaction.user
            user_id = str(user.id)

        user_name = user.name

        user_exists = await self.bot.db.fetchval("SELECT 1 FROM user_data WHERE user_id = $1", user_id)
        if not user_exists:
            await self.bot.db.execute("INSERT INTO user_data (user_id) VALUES ($1)", user_id)

        hid = await self.bot.db.fetchval("SELECT hid FROM user_data WHERE user_id = $1", user_id)

        results = await asyncio.gather(
            self.bot.db.fetchval("SELECT Fame FROM user_data WHERE user_id = $1", user_id),
            self.bot.db.check_owner(user_id),
            self.bot.db.check_donor(user_id),
            self.bot.db.check_booster(user.id),
            self.bot.db.check_blacklisted(user_id),
        )
        
        fame_status, is_owner, is_donor, is_booster, is_blacklisted = results
        is_founder = user.id == 1363295564133040272

        lastfm_info = ""
        try:
            lastfm_data = await self.bot.db.fetchrow(
                "SELECT l.lastfm_username, s.lastfm_state "
                "FROM lastfm_usernames l "
                "LEFT JOIN settings s ON l.user_id = s.user_id "
                "WHERE l.user_id = $1", user_id
            )
            
            if lastfm_data and lastfm_data['lastfm_username']:
                lastfm_username = lastfm_data['lastfm_username']
                lastfm_state = lastfm_data['lastfm_state'] or 'Show'

                api_key = self.LASTFM_KEY
                recent_tracks_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={lastfm_username}&api_key={api_key}&format=json"

                async with self.session.get(recent_tracks_url) as recent_tracks_response:
                    if recent_tracks_response.status == 200:
                        tracks = (await recent_tracks_response.json())['recenttracks'].get('track', [])
                        if tracks:
                            track = tracks[0]
                            is_now_playing = '@attr' in track and 'nowplaying' in track['@attr'] and track['@attr']['nowplaying'] == 'true'
                            artist_name = track['artist']['#text']
                            track_name = track['name']

                            if is_now_playing:
                                artistenc = urllib.parse.quote(artist_name)
                                trackenc = urllib.parse.quote(track_name)

                                spotify_url = f"http://127.0.0.1:2053/api/search?lastfm_username={lastfm_username}&track_name={trackenc}&artist_name={artistenc}"
                                headers = {"X-API-Key": self.HEIST_KEY}

                                async with self.session.get(spotify_url, headers=headers) as spotify_response:
                                    status = "<:lastfm:1275185763574874134>"
                                    if spotify_response.status == 200:
                                        spotify_data = await spotify_response.json()
                                        spotify_track_url = spotify_data.get('spotify_link')

                                        if lastfm_state == 'Show':
                                            if spotify_track_url:
                                                lastfm_info = f"{status} ***[{track_name}]({spotify_track_url})*** ([@{lastfm_username}](https://www.last.fm/user/{lastfm_username}))\n\n"
                                            else:
                                                lastfm_info = f"{status} ***{track_name}*** ([@{lastfm_username}](https://www.last.fm/user/{lastfm_username}))\n\n"
                                        else:
                                            if spotify_track_url:
                                                lastfm_info = f"{status} ***[{track_name}]({spotify_track_url})***\n\n"
                                            else:
                                                lastfm_info = f"{status} ***{track_name}***\n\n"
                                    else:
                                        if lastfm_state == 'Show':
                                            lastfm_info = f"{status} ***{track_name}*** ([@{lastfm_username}](https://www.last.fm/user/{lastfm_username}))\n\n"
                                        else:
                                            lastfm_info = f"{status} ***{track_name}***\n\n"
                            elif lastfm_state == 'Show':
                                lastfm_info = f"<:lastfm:1275185763574874134> [@{lastfm_username}](https://www.last.fm/user/{lastfm_username})\n\n"
        except Exception as e:
            self.bot.logger.error(f"Error fetching Last.fm data: {e}")

        if is_blacklisted:
            status_string = "<:bl1:1263853643216584764><:bl2:1263853966618394724><:bl3:1263854236601552907><:bl4:1263854052559552555><:bl5:1263854267228356731>"
        else:
            statuses = []
            if is_owner:
                if is_founder:
                    statuses.append("<a:heistowner:1343768654357205105> **`Heist Owner`**")
                else:
                    statuses.append("<:hstaff:1311070369829883925> **`Heist Admin`**")
            if fame_status:
                statuses.append("<:famous:1311067416251596870> **`Famous`**")
            if is_booster:
                statuses.append("<:boosts:1263854701535821855> **`Booster`**")
            if is_donor:
                statuses.append("<:premium:1311062205650833509> **`Premium`**")
            if not is_donor:
                statuses.append("<:heist:1273999266154811392> **`Standard`**")

            status_string = ", ".join(statuses)

        embed = discord.Embed(
            description=lastfm_info + status_string,
            color=await self.bot.color_manager.resolve(interaction.user.id)
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_author(
            name=f"{user_name} ; uid {hid}",
            icon_url=user.display_avatar.url
        )
        embed.set_footer(
            text=f"heist.lol • {user.id}",
            icon_url="https://git.cursi.ng/heist.png?"
        )

        await interaction.followup.send(embed=embed)

    @hybrid_command(
        name="ping",
        aliases=["ms", "latency", "lat"],
        description="View the bot's latency."
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def ping(self, ctx):
        try:
            start_time = time.time()
            embed = Embed(color=await self.bot.color_manager.resolve(ctx.author.id))
            
            latency = round(self.bot.latency * 1000)
            description = (
                f"> 📡 **Ping:** `{latency}ms`\n"
                f"> 🗄️ **Database:** `2ms`"
            )
            
            embed.description = description
            
            if ctx.interaction:
                if ctx.interaction.response.is_done():
                    message = await ctx.interaction.followup.send(embed=embed)
                else:
                    await ctx.interaction.response.send_message(embed=embed)
                    message = await ctx.interaction.original_response()
            else:
                message = await ctx.send(embed=embed)

            edit_ping = round((time.time() - start_time) * 1000)
            await asyncio.sleep(1)
            
            description = (
                f"> 📡 **Ping:** `{latency}ms` (edit: **{edit_ping}ms**)\n"
                f"> 🗄️ **Database:** `2ms`"
            )
            
            embed.description = description
            await message.edit(embed=embed)
            
        except (NotFound, HTTPException):
            embed.description = description
            await ctx.send(embed=embed)

    @hybrid_command(
        name="cv2",
        description="playing with cv2"
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def cv2test(self, ctx):
        """Test Discord UI components"""
        await ctx.send(view=TestView())

async def setup(bot):
    await bot.add_cog(Info(bot))