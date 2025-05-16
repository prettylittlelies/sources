import discord
import platform
import time
import asyncio
import os
from discord import ui
from discord.ui import View, button
from discord import (app_commands, NotFound, HTTPException, ButtonStyle, Button, Embed)
from discord.ext import commands
from discord.ext.commands import (Cog, hybrid_command, GroupCog)
from system.classes.permissions import Permissions
from system.classes.color import ColorManager
from typing import Optional
from data.config import CONFIG
from PIL import Image
import io
import aiohttp

class Discord(GroupCog, name="discord"):
    def __init__(self, bot):
        self.bot = bot
        self.LURE_KEY = CONFIG.get('LURE_API_KEY')
        self.LASTFM_KEY = CONFIG.get('LASTFM_API_KEY')
        self.HEIST_KEY = CONFIG.get('HEIST_API_KEY')
        self.session = aiohttp.ClientSession()
        self.badge_emojis = {
            "hypesquad_house_1": "<:hypesquad_bravery:1263855923806470144>",
            "hypesquad_house_2": "<:hypesquad_brilliance:1263855913480097822>",
            "hypesquad_house_3": "<:hypesquad_balance:1263855909420138616>",
            "premium": "<:nitro:1263855900846981232>",
            "premium_type_1": "<:bronzen:1293983425828753480>",
            "premium_type_2": "<:silvern:1293983951983083623>",
            "premium_type_3": "<:goldn:1293983938485686475>",
            "premium_type_4": "<:platinumn:1293983921469526137>",
            "premium_type_5": "<:diamondn:1293983900435091566>",
            "premium_type_6": "<:emeraldn:1293983816259731527>",
            "premium_type_7": "<:rubyn:1293983910342164655>",
            "premium_type_8": "<:firen:1293983849264582666>",
            "guild_booster_lvl1": "<:boosts1:1263857045027819560>",
            "guild_booster_lvl2": "<:boosts2:1263857025658388613>",
            "guild_booster_lvl3": "<:boosts:1263856979911245897>",
            "guild_booster_lvl4": "<:boosts4:1263856929835450469>",
            "guild_booster_lvl5": "<:boosts5:1263856884708937739>",
            "guild_booster_lvl6": "<:boosts6:1263856802638860370>",
            "guild_booster_lvl7": "<:boosts7:1263856551555502211>",
            "guild_booster_lvl8": "<:boosts8:1263856534216114298>",
            "guild_booster_lvl9": "<:boosts9:1263856512506400871>",
            "early_supporter": "<:early_supporter:1265425918843814010>",
            "verified_developer": "<:earlybotdev:1265426039509749851>",
            "active_developer": "<:activedeveloper:1265426222444183645>",
            "hypesquad": "<:hypesquad_events:1265426613605240863>",
            "bug_hunter_level_1": "<:bughunter_1:1265426779523252285>",
            "bug_hunter_level_2": "<:bughunter_2:1265426786607562893>",
            "staff": "<:staff:1265426958322241596>",
            "partner": "<:partner:1265426965511536792>",
            "bot_commands": "<:supports_commands:1265427168469712908>",
            "legacy_username": "<:pomelo:1265427449999659061>",
            "quest_completed": "<:quest:1265427335058948247>",
            "bot": "<:bot:1290389425850679388>",
            "heist": "<:heist:1273999266154811392>"
        }

    @app_commands.command(name="user", description="View a Discord user's profile")
    @app_commands.describe(user="The user to view information about")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.check(Permissions.is_blacklisted)
    async def user(self, interaction: discord.Interaction, user: Optional[discord.User] = None):
        user = user or interaction.user
        await interaction.response.defer()
        
        is_blacklisted = await self.bot.db.check_blacklisted(user.id)
        is_booster = await self.bot.db.check_booster(user.id)
        is_donor = await self.bot.db.check_donor(user.id)
        is_donor_self = await self.bot.db.check_donor(interaction.user.id)
        is_owner = await self.bot.db.check_owner(user.id)
        is_owner_self = await self.bot.db.check_owner(interaction.user.id)
        is_famous = await self.bot.db.check_famous(user.id)
        embed_color = await self.bot.color_manager.resolve(interaction.user.id)

        is_founder = user.id == 1363295564133040272

        badges = []
        badge_names = []
        full_user = await self.bot.fetch_user(user.id)
        use_discord_method = True
        user_data = None

        try:
            url = f"http://127.0.0.1:8002/users/{user.id}"
            headers = {"X-API-Key": self.HEIST_KEY}
            timeout = aiohttp.ClientTimeout(total=5)
            async with self.session.get(url, headers=headers, timeout=timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and 'user' in data and 'id' in data['user']:
                        use_discord_method = False
                        user_data = data.get('user', {})
                        if 'badges' in data and data['badges']:
                            for badge in data['badges']:
                                badge_emoji = self.badge_emojis.get(badge['id'])
                                if badge_emoji and badge_emoji not in badges:
                                    badges.append(badge_emoji)
                                    badge_names.append(badge['id'])
                                    
                            if not user.bot and "premium_since" in data:
                                premium_since = datetime.fromisoformat(data["premium_since"].replace("Z", "+00:00"))
                                now = datetime.now(premium_since.tzinfo)
                                months_subscribed = (now - premium_since).days / 30.44
                                
                                nitro_emoji = None
                                nitro_key = None
                                if months_subscribed >= 72:
                                    nitro_emoji = self.badge_emojis.get("premium_type_8")
                                    nitro_key = "premium_type_8"
                                elif months_subscribed >= 60:
                                    nitro_emoji = self.badge_emojis.get("premium_type_7")
                                    nitro_key = "premium_type_7"
                                elif months_subscribed >= 36:
                                    nitro_emoji = self.badge_emojis.get("premium_type_6")
                                    nitro_key = "premium_type_6"
                                elif months_subscribed >= 24:
                                    nitro_emoji = self.badge_emojis.get("premium_type_5")
                                    nitro_key = "premium_type_5"
                                elif months_subscribed >= 12:
                                    nitro_emoji = self.badge_emojis.get("premium_type_4")
                                    nitro_key = "premium_type_4"
                                elif months_subscribed >= 6:
                                    nitro_emoji = self.badge_emojis.get("premium_type_3")
                                    nitro_key = "premium_type_3"
                                elif months_subscribed >= 3:
                                    nitro_emoji = self.badge_emojis.get("premium_type_2")
                                    nitro_key = "premium_type_2"
                                elif months_subscribed >= 1:
                                    nitro_emoji = self.badge_emojis.get("premium_type_1")
                                    nitro_key = "premium_type_1"
                                else:
                                    nitro_emoji = self.badge_emojis.get("premium")
                                    nitro_key = "premium"

                                if nitro_emoji:
                                    nitro_position = None
                                    if "premium" in badge_names:
                                        nitro_position = badge_names.index("premium")
                                    
                                    if nitro_key.startswith("premium_type_"):
                                        if nitro_position is not None:
                                            badges[nitro_position] = nitro_emoji
                                            badge_names[nitro_position] = nitro_key
                                        else:
                                            insert_index = 0
                                            for name in badge_names:
                                                if name > "premium":
                                                    break
                                                insert_index += 1
                                            badges.insert(insert_index, nitro_emoji)
                                            badge_names.insert(insert_index, nitro_key)
                                    elif nitro_key == "premium":
                                        if nitro_position is None:
                                            insert_index = 0
                                            for name in badge_names:
                                                if name > "premium":
                                                    break
                                                insert_index += 1
                                            badges.insert(insert_index, nitro_emoji)
                                            badge_names.insert(insert_index, nitro_key)
        except:
            use_discord_method = True
        
        if use_discord_method and not user.bot:
            user_flags = user.public_flags.all()
            for flag in user_flags:
                badge_emoji = self.badge_emojis.get(flag.name)
                if badge_emoji:
                    badges.append(badge_emoji)
                    badge_names.append(flag.name)

            if full_user.avatar and full_user.avatar.key.startswith('a_') or full_user.banner:
                nitro_emoji = self.badge_emojis.get("premium", "")
                if nitro_emoji:
                    insert_index = 0
                    for name in badge_names:
                        if name > "premium":
                            break
                        insert_index += 1
                    badges.insert(insert_index, nitro_emoji)
                    badge_names.insert(insert_index, "premium")
        elif user.bot:
            badges.append(self.badge_emojis.get("bot", ""))

        badge_string = f"### {' '.join(badges)}" if badges else ""

        heist_titles = []
        if not user.bot:
            if not is_blacklisted:
                if is_owner:
                    if is_founder:
                        heist_titles.append("<a:heistowner:1343768654357205105> **`Heist Owner`**")
                    else:
                        heist_titles.append("<:hstaff:1311070369829883925> **`Heist Admin`**")
                if is_famous:
                    heist_titles.append("<:famous:1311067416251596870> **`Famous`**")
                if is_booster:
                    heist_titles.append("<:boosts:1263854701535821855> **`Booster`**")
                if is_donor:
                    heist_titles.append("<:premium:1311062205650833509> **`Premium`**")
                if not is_donor:
                    heist_titles.append("<:heist:1273999266154811392> **`Standard`**")
            else:
                heist_titles.append("❌ **`Blacklisted`** (lol)")

        heist_titles_string = ", ".join(heist_titles)

        description = badge_string
        if heist_titles_string:
            description += f"\n{heist_titles_string}"
            
        lastfm_username = await self.bot.db.fetchval(
            "SELECT lastfm_username FROM lastfm_usernames WHERE user_id = $1",
            str(user.id))

        has_audio = False
        song_name = None
        artist_name = None
        if lastfm_username:
            try:
                api_key = self.LASTFM_KEY
                recent_tracks_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={lastfm_username}&api_key={api_key}&format=json"

                async with self.session.get(recent_tracks_url) as recent_tracks_response:
                    if recent_tracks_response.status == 200:
                        tracks = (await recent_tracks_response.json())['recenttracks'].get('track', [])

                        if tracks:
                            now_playing = None
                            for track in tracks:
                                if '@attr' in track and 'nowplaying' in track['@attr'] and track['@attr']['nowplaying'] == 'true':
                                    now_playing = track
                                    break

                            if now_playing:
                                artist_name = now_playing['artist']['#text']
                                song_name = now_playing['name']

                                trackenc = urllib.parse.quote_plus(song_name)
                                artistenc = urllib.parse.quote_plus(artist_name)
                                artist_url = f"https://www.last.fm/music/{artistenc}"
                                api_url = f"http://127.0.0.1:2053/api/search?lastfm_username={lastfm_username}&track_name={trackenc}&artist_name={artistenc}"
                                headers = {"X-API-Key": f"{self.HEIST_KEY}"}
                                
                                async with self.session.get(api_url, headers=headers) as spotify_response:
                                    if spotify_response.status == 200:
                                        spotify_data = await spotify_response.json()
                                        song_url = spotify_data.get('spotify_link')
                                        description += f"\n-# <:lastfm:1275185763574874134> [**{song_name}**]({song_url}) by [{artist_name}]({artist_url})"
                                    else:
                                        description += f"\n-# <:lastfm:1275185763574874134> **{song_name}** by {artist_name}"
                            else:
                                last_played = tracks[-1]
                                artist_name = last_played['artist']['#text']
                                song_name = last_played['name']

                                trackenc = urllib.parse.quote_plus(song_name)
                                artistenc = urllib.parse.quote_plus(artist_name)
                                artist_url = f"https://www.last.fm/music/{artistenc}"
                                api_url = f"http://127.0.0.1:2053/api/search?lastfm_username={lastfm_username}&track_name={trackenc}&artist_name={artistenc}"
                                headers = {"X-API-Key": f"{self.HEIST_KEY}"}

                                async with self.session.get(api_url, headers=headers) as spotify_response:
                                    if spotify_response.status == 200:
                                        spotify_data = await spotify_response.json()
                                        song_url = spotify_data.get('spotify_link')
                                        description += f"\n-# <:lastfm:1275185763574874134> Last listened to [**{song_name}**]({song_url}) by [{artist_name}]({artist_url})"
                                    else:
                                        description += f"\n-# <:lastfm:1275185763574874134> Last listened to **{song_name}** by {artist_name}"

                            query = f"{song_name} {artist_name}"
                            headers = {
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                            }
                            async with self.session.get(f"https://api.stats.fm/api/v1/search/elastic?query={query}%20{artist_name}&type=track&limit=1", headers=headers) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    tracks = data.get("items", {}).get("tracks", [])

                                    if tracks:
                                        genius_title = song_name.lower().strip()
                                        genius_artist = artist_name.lower().strip()

                                        for track in tracks:
                                            track_title = track.get("name", "").lower().strip()
                                            track_artists = [artist.get("name", "").lower().strip() for artist in track.get("artists", [])]
                                            spotify_preview = track.get("spotifyPreview")
                                            apple_preview = track.get("appleMusicPreview")

                                            title_match = genius_title in track_title or track_title in genius_title
                                            artist_match = any(genius_artist in artist_name or artist_name in genius_artist for artist_name in track_artists)

                                            if title_match and artist_match and (spotify_preview or apple_preview):
                                                has_audio = True
                                                break
            except Exception as e:
                print(e)
                pass

        if user_data and "bio" in user_data and user_data["bio"]:
            description += f"\n{user_data['bio']}"
            
        description += f"\n\n-# **Created on** <t:{int(user.created_at.timestamp())}:f> (<t:{int(user.created_at.timestamp())}:R>)"

        embed = discord.Embed(
            description=description,
            color=embed_color
        )

        if user_data and 'clan' in user_data and user_data.get('clan') and isinstance(user_data['clan'], dict):
            clan = user_data['clan']
            clan_tag = clan.get('tag')
            clan_badge = clan.get('badge')
            identity_guild_id = clan.get('identity_guild_id')
            if clan_tag and clan_badge and identity_guild_id:
                clan_badge_url = f"https://cdn.discordapp.com/clan-badges/{identity_guild_id}/{clan_badge}.png?size=16"
                embed.set_author(name=f"{clan_tag}", icon_url=clan_badge_url)
                embed.description = f"**{user.display_name} (@{user.name})**\n{description}"
            else:
                embed.set_author(name=f"{user.display_name} (@{user.name})", icon_url=user.display_avatar.url)
                embed.description = description
        else:
            embed.set_author(name=f"{user.display_name} (@{user.name})", icon_url=user.display_avatar.url)
            embed.description = description

        embed.set_thumbnail(url=user.display_avatar.url)

        banner_url = full_user.banner.url if full_user.banner else None
        if banner_url:
            embed.set_image(url=banner_url)
        
        embed.set_footer(text=f"heist.lol • {user.id}", icon_url="https://csyn.me/assets/heist.png?c") 

        view = discord.ui.View(timeout=300)

        async def on_timeout():
            for item in view.children:
                if isinstance(item, discord.ui.Button) and item.style != discord.ButtonStyle.link:
                    item.disabled = True
            try:
                await interaction.edit_original_response(view=view)
            except discord.NotFound:
                pass

        view.on_timeout = on_timeout

        profile_button = discord.ui.Button(label="View Profile", emoji=discord.PartialEmoji.from_str("<:person:1295440206706511995>"), style=discord.ButtonStyle.link, url=f"discord://-/users/{user.id}")
        view.add_item(profile_button)

        avatar_history_button = discord.ui.Button(
            label="Avatar History",
            emoji=discord.PartialEmoji.from_str("<:unlock:1295440365226037340>"),
            style=discord.ButtonStyle.secondary,
            custom_id=f"avatar_history_{user.id}_{interaction.user.id}"
        )
        view.add_item(avatar_history_button)

        if has_audio and song_name and artist_name:
            audio_button = discord.ui.Button(
                emoji=discord.PartialEmoji.from_str("<:audio:1345517095101923439>"),
                style=discord.ButtonStyle.secondary,
                custom_id=f"audio_{user.id}_{interaction.user.id}"
            )

            async def audio_button_callback(button_interaction: discord.Interaction):
                await button_interaction.response.defer(ephemeral=True)
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                query = f"{song_name} {artist_name}"
                async with self.session.get(f"https://api.stats.fm/api/v1/search/elastic?query={query}%20{artist_name}&type=track&limit=1", headers=headers) as response:
                    if response.status != 200:
                        await button_interaction.followup.send("Failed to fetch track data.", ephemeral=True)
                        return
                    
                    data = await response.json()
                    tracks = data.get("items", {}).get("tracks", [])

                    if not tracks:
                        await button_interaction.followup.send("No tracks found.", ephemeral=True)
                        return

                    genius_title = song_name.lower().strip()
                    genius_artist = artist_name.lower().strip()

                    best_match = None
                    for track in tracks:
                        track_title = track.get("name", "").lower().strip()
                        track_artists = [artist.get("name", "").lower().strip() for artist in track.get("artists", [])]
                        spotify_preview = track.get("spotifyPreview")
                        apple_preview = track.get("appleMusicPreview")

                        title_match = genius_title in track_title or track_title in genius_title
                        artist_match = any(genius_artist in artist_name or artist_name in genius_artist for artist_name in track_artists)

                        if title_match and artist_match:
                            if spotify_preview or apple_preview:
                                best_match = track
                                break
                            else:
                                best_match = best_match or track

                    if not best_match:
                        await button_interaction.followup.send("No matching track found.", ephemeral=True)
                        return

                    preview_url = best_match.get("spotifyPreview") or best_match.get("appleMusicPreview")

                    if preview_url:
                        async with self.session.get(preview_url) as audio_response:
                            if audio_response.status == 200:
                                audio_data = await audio_response.read()

                                try:
                                    def process_audio(data):
                                        audio = AudioSegment.from_file(io.BytesIO(data))
                                        opus_io = io.BytesIO()
                                        audio.export(opus_io, format="opus", parameters=["-b:a", "128k", "-application", "voip"])
                                        opus_io.seek(0)
                                        return opus_io

                                    opus_io = await asyncio.to_thread(process_audio, audio_data)
                                    
                                    audio_file = discord.File(opus_io, filename="audio.opus")
                                    
                                    await interaction.followup.send(file=audio_file, voice_message=True, ephemeral=True)
                                    
                                except Exception as e:
                                    if 'opus_io' in locals():
                                        opus_io.close()
                                    await interaction.followup.send(f"Error converting audio: {str(e)}", ephemeral=True)
                            else:
                                await interaction.followup.send("Failed to fetch audio preview.", ephemeral=True)
                    else:
                        await interaction.followup.send("No audio preview available.", ephemeral=True)

            audio_button.callback = audio_button_callback
            view.add_item(audio_button)

        guilds_button = None
        if is_owner_self:
            guilds_button = discord.ui.Button(
                label="Guilds",
                emoji=discord.PartialEmoji.from_str("<:group:1343755056536621066>"),
                style=discord.ButtonStyle.green,
                custom_id=f"guilds_{user.id}_{interaction.user.id}"
            )
            if guilds_button:
                view.add_item(guilds_button)

        await interaction.followup.send(embed=embed, view=view)

        guilds_button_callback = None
        if guilds_button:
            async def guilds_button_callback(button_interaction: discord.Interaction):
                if button_interaction.user.id != interaction.user.id:
                    await button_interaction.response.send_message("You cannot use this button.", ephemeral=True)
                    return

                await button_interaction.response.defer(thinking=True, ephemeral=True)

                target_user = await self.bot.fetch_user(user.id)

                processing_embed = discord.Embed(
                    description=f"<a:loading:1269644867047260283> {interaction.user.mention}: processing..",
                    color=await self.bot.color_manager.resolve(interaction.user.id)
                )
                processing = await button_interaction.followup.send(embed=processing_embed)

                headers = {"X-API-Key": self.HEIST_KEY}
                guilds_info = []
                guild_ids = set()

                retries = 0
                max_retries = 5
                backoff_factor = 2
                timeout = aiohttp.ClientTimeout(total=2)

                while retries < max_retries:
                    try:
                        async with self.session.get(f"http://127.0.0.1:8002/mutualguilds/{user.id}", headers=headers, timeout=timeout) as resp:
                            if resp.status == 200:
                                guilds_data = await resp.json()
                                for guild_data in guilds_data:
                                    guild_id = guild_data.get("id")
                                    if guild_id not in guild_ids:
                                        guild_ids.add(guild_id)
                                        guilds_info.append(guild_data)

                                if len(guilds_info) == 0:
                                    embed = discord.Embed(
                                        title=f"{target_user.name}'s guilds shared with Heist (0)",
                                        description="-# No guilds shared with user.",
                                        color=await self.bot.color_manager.resolve(interaction.user.id)
                                    )
                                    embed.set_footer(text="heist.lol", icon_url="https://csyn.me/assets/heist.png?c")
                                    embed.set_thumbnail(url=target_user.avatar.url if target_user.avatar else target_user.default_avatar.url)
                                    await processing.edit(embed=embed)
                                    return

                                total_pages = (len(guilds_info) + 4) // 5
                                current_page = 0

                                embed = discord.Embed(
                                    title=f"{target_user.name}'s guilds shared with Heist ({len(guilds_info)})",
                                    url=f"https://discord.com/users/{target_user.id}",
                                    color=await self.bot.color_manager.resolve(interaction.user.id)
                                )

                                embed.description = ""

                                start_idx = current_page * 5
                                end_idx = min(start_idx + 5, len(guilds_info))

                                for guild in guilds_info[start_idx:end_idx]:
                                    guild_name = guild.get("name", "Unknown Guild")
                                    vanity = guild.get("vanity_url")
                                    vanity_text = f"`discord.gg/{vanity}`" if vanity else "`no vanity found`"
                                    embed.description += f"**{guild_name}**\n-# {vanity_text}\n\n"

                                embed.set_author(
                                    name=f"{target_user.name}",
                                    icon_url=target_user.avatar.url if target_user.avatar else target_user.default_avatar.url
                                )
                                embed.set_thumbnail(url=target_user.avatar.url if target_user.avatar else target_user.default_avatar.url)
                                embed.set_footer(text=f"Page {current_page + 1}/{total_pages} • heist.lol", icon_url="https://csyn.me/assets/heist.png?c")

                                view = discord.ui.View()

                                previous_button = discord.ui.Button(
                                    emoji=discord.PartialEmoji.from_str("<:left:1265476224742850633>"), 
                                    style=discord.ButtonStyle.primary, 
                                    disabled=True,
                                    custom_id="previous"
                                )
                                view.add_item(previous_button)

                                next_button = discord.ui.Button(
                                    emoji=discord.PartialEmoji.from_str("<:right:1265476229876678768>"), 
                                    style=discord.ButtonStyle.primary, 
                                    disabled=total_pages <= 1,
                                    custom_id="next"
                                )
                                view.add_item(next_button)

                                skip_button = discord.ui.Button(
                                    emoji=discord.PartialEmoji.from_str("<:sort:1317260205381386360>"),
                                    style=discord.ButtonStyle.secondary,
                                    custom_id="skip"
                                )
                                view.add_item(skip_button)

                                json_button = discord.ui.Button(
                                    emoji=discord.PartialEmoji.from_str("<:json:1292867766755524689>"),
                                    style=discord.ButtonStyle.secondary,
                                    custom_id="json"
                                )
                                view.add_item(json_button)

                                delete_button = discord.ui.Button(
                                    emoji=discord.PartialEmoji.from_str("<:bin:1317214464231079989>"),
                                    style=discord.ButtonStyle.danger,
                                    custom_id="delete"
                                )
                                view.add_item(delete_button)

                                async def button_callback(button_interaction: discord.Interaction):
                                    nonlocal current_page
                                    if button_interaction.user.id != interaction.user.id:
                                        await button_interaction.response.send_message("You cannot use these buttons.", ephemeral=True)
                                        return

                                    if button_interaction.data["custom_id"] == "delete":
                                        await button_interaction.response.defer()
                                        await button_interaction.delete_original_response()
                                        return

                                    if button_interaction.data["custom_id"] == "skip":
                                        class GoToPageModal(discord.ui.Modal, title="Go to Page"):
                                            page_number = discord.ui.TextInput(label="Navigate to page", placeholder=f"Enter a page number (1-{total_pages})", min_length=1, max_length=len(str(total_pages)))

                                            async def on_submit(self, interaction: discord.Interaction):
                                                try:
                                                    page = int(self.page_number.value) - 1
                                                    if page < 0 or page >= total_pages:
                                                        raise ValueError
                                                    nonlocal current_page
                                                    current_page = page
                                                    await update_message()
                                                    await interaction.response.defer()
                                                except ValueError:
                                                    await interaction.response.send_message("Invalid choice, cancelled.", ephemeral=True)

                                        modal = GoToPageModal()
                                        await button_interaction.response.send_modal(modal)
                                        return

                                    if button_interaction.data["custom_id"] == "previous":
                                        current_page = max(0, current_page - 1)
                                    elif button_interaction.data["custom_id"] == "next":
                                        current_page = min(total_pages - 1, current_page + 1)

                                    await button_interaction.response.defer()
                                    await update_message()

                                async def update_message():
                                    embed.description = ""
                                    start_idx = current_page * 5
                                    end_idx = min(start_idx + 5, len(guilds_info))

                                    for guild in guilds_info[start_idx:end_idx]:
                                        guild_name = guild.get("name", "Unknown Guild")
                                        vanity = guild.get("vanity_url")
                                        vanity_text = f"`discord.gg/{vanity}`" if vanity else "`no vanity found`"
                                        embed.description += f"**{guild_name}**\n-# {vanity_text}\n\n"

                                    embed.set_footer(text=f"Page {current_page + 1}/{total_pages} • heist.lol", icon_url="https://csyn.me/assets/heist.png?c")

                                    view.children[0].disabled = current_page == 0
                                    view.children[1].disabled = current_page == total_pages - 1

                                    await processing.edit(embed=embed, view=view)

                                async def json_button_callback(button_interaction: discord.Interaction):
                                    formatjson = json.dumps(guilds_info, indent=4)
                                    file = io.BytesIO(formatjson.encode())
                                    await button_interaction.response.send_message(file=discord.File(file, filename="guilds.json"), ephemeral=True)

                                for button in view.children[:-2]:
                                    button.callback = button_callback

                                json_button.callback = json_button_callback
                                delete_button.callback = button_callback

                                await processing.edit(embed=embed, view=view)
                                break

                    except Exception as e:
                        print(f"Error occurred: {e}. Retrying...")
                        retries += 1
                        await asyncio.sleep(backoff_factor * retries)
                else:
                    await button_interaction.followup.send("An error occurred while fetching guilds after multiple attempts.", ephemeral=True)

            guilds_button.callback = guilds_button_callback

        async def avatar_history_button_callback(button_interaction: discord.Interaction):
            await self.handle_avatar_history(button_interaction)

        avatar_history_button.callback = avatar_history_button_callback

    async def handle_avatar_history(self, interaction: discord.Interaction):
        custom_id = interaction.data['custom_id']
        parts = custom_id.split('_')
        target_user_id, author_id = parts[2], parts[3]
        target_user = await self.bot.fetch_user(int(target_user_id))
        await interaction.response.defer(thinking=True, ephemeral=True)
        
        url = f"https://api.lure.rocks/avatars/{target_user.id}"
        headers = {"X-API-Key": self.LURE_KEY}
        
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status != 200:
                    response_text = await response.text()
                    await interaction.followup.send("No avatar history found for user.", ephemeral=True)
                    return
                    
                avatar_data = await response.json()

                avatar_data = await response.json()
                if not avatar_data or not avatar_data.get('avatars'):
                    await interaction.followup.send("No avatar history found for user.", ephemeral=True)
                    return
                    
                view = AvatarHistoryView(interaction, avatar_data, target_user, interaction.user)
                embed = await view.create_embed()
                view.update_buttons()
                await interaction.followup.send(embed=embed, view=view)
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)

    @hybrid_command(
        name="avatar",
        description="View a user's avatar",
        aliases=["av"]
    )
    @app_commands.describe(user="The user whose avatar you want to view")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def avatar(self, ctx: commands.Context, user: Optional[discord.User] = None):
        user = user or ctx.author

        try:
            avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
            if isinstance(ctx, commands.Context):
                await ctx.send(avatar_url)
            else:
                await ctx.response.send_message(avatar_url)

        except Exception as e:
            if isinstance(ctx, commands.Context):
                await ctx.send(f"An error occurred: {e}")
            else:
                await ctx.response.send_message(f"An error occurred: {e}", ephemeral=True)

    @hybrid_command(
        name="banner",
        description="View a user's banner",
        aliases=["bn"]
    )
    @app_commands.describe(user="The user whose banner you want to view")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True) 
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def banner(self, ctx: commands.Context, user: Optional[discord.User] = None):
        user = user or ctx.author

        try:
            full_user = await self.bot.fetch_user(user.id)

            banner = full_user.banner
            if banner is None:
                if isinstance(ctx, commands.Context):
                    await ctx.send(f"**{user}** has no banner set.")
                else:
                    await ctx.response.send_message(f"**{user}** has no banner set.")
                return

            if isinstance(ctx, commands.Context):
                await ctx.send(banner.url)
            else:
                await ctx.response.send_message(banner.url)

        except Exception as e:
            if isinstance(ctx, commands.Context):
                await ctx.warning(f"An error occurred: {e}")
            else:
                await ctx.response.send_message(f"An error occurred: {e}", ephemeral=True)

    @hybrid_command(
        name="serveravatar",
        description="View a user's server avatar",
        aliases=["sav"]
    )
    @app_commands.describe(user="The user whose server avatar you want to view")
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False) 
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def serveravatar(self, ctx: commands.Context, user: Optional[discord.Member] = None):
        """View a user's server avatar."""
        user = user or ctx.author

        try:
            avatar_url = user.display_avatar.url

            if isinstance(ctx, commands.Context):
                await ctx.send(avatar_url)
            else:
                await ctx.response.send_message(avatar_url)

        except Exception as e:
            if isinstance(ctx, commands.Context):
                await ctx.warning(f"An error occurred: {e}")
            else:
                await ctx.response.send_message(f"An error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Discord(bot))