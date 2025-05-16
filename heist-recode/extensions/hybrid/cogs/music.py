import discord
from discord import app_commands, Embed, File
from discord.ext import commands
from data.config import CONFIG
import aiohttp
import asyncio
import urllib.parse
import time
import io
from PIL import Image
from typing import Optional
import calendar
from system.classes.previews import AudioPreviewHandler
from system.classes.paginator import Paginator
from system.classes.logger import Logger
from system.classes.permissions import Permissions
from collections import Counter
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
import logging 

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.LASTFM_KEY = CONFIG.get('LASTFM_API_KEY')
        self.HEIST_KEY = CONFIG.get('HEIST_API_KEY')
        self.logger = Logger()

    def cog_unload(self):
        asyncio.create_task(self.session.close())
        
    async def get_pagination_emojis(self):
        """Get custom pagination emojis or fallback to defaults"""
        emojis = {}
        
        for name, fallback in [
            ('first', "⏮️"),
            ('left', "◀️"),
            ('right', "▶️"),
            ('last', "⏭️"),
            ('bin', "🗑️"),
            ('cancel', "✖️"),
            ('sort', "🔄")
        ]:
            if callable(getattr(self.bot.emojis, 'get', None)):
                emoji = await self.bot.emojis.get(name)
                if emoji is None:
                    emoji = fallback
            else:
                emoji = fallback
            emojis[name] = emoji
            
        return emojis
        
    async def add_pagination_controls(self, paginator, multi_page=True):
        """Add standard pagination controls to a paginator"""
        emojis = await self.get_pagination_emojis()
        
        if multi_page:
            paginator.add_button("back", emoji=emojis['left'])
            paginator.add_button("next", emoji=emojis['right'])
        
        paginator.add_button("delete", emoji=emojis['cancel'], style=discord.ButtonStyle.danger)
        paginator.add_button("page")
        
        return paginator

    async def get_dominant_color(self, image_data):
        def process_image(data):
            image = Image.open(io.BytesIO(data))
            image = image.resize((1, 1))
            image = image.convert("RGB")
            dominant_color = image.getpixel((0, 0))
            return (dominant_color[0] << 16) + (dominant_color[1] << 8) + dominant_color[2]
        
        return await asyncio.to_thread(process_image, image_data)

    @commands.hybrid_group(
        name="lastfm",
        description="LastFM music commands",
        aliases=["lf", "lfm"]
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def lastfm(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
    
    @commands.hybrid_group(
        name="statsfm",
        description="StatsFM music commands",
        aliases=["sf", "sfm"]
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def statsfm(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
    
    @statsfm.command(
        name="set",
        description="Set your Stats.fm username"
    )
    @app_commands.describe(username="Your Stats.fm username")
    async def statsfm_set(self, ctx: commands.Context, username: str):
        """Set your Stats.fm username"""
        
        if not username.replace('_', '').isalnum():
            return await ctx.warning("Username can only contain letters, numbers, and underscores.")
        
        if ' ' in username:
            return await ctx.warning("Username cannot contain spaces.")
        
        user_id = str(ctx.author.id)
        
        headers = {"User-Agent": "Heist Bot/1.0"}
        async with self.session.get(
            f"https://api.stats.fm/api/v1/users/{username}",
            headers=headers
        ) as response:
            if response.status == 404:
                return await ctx.warning(f"Could not find Stats.fm user with username `{username}`.")
            elif response.status != 200:
                return await ctx.warning("The Stats.fm API is currently unavailable.")
        
        async with self.bot.db.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO statsfm_usernames (user_id, statsfm_username)
                VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE
                SET statsfm_username = EXCLUDED.statsfm_username
            """, user_id, username)
    
            await ctx.success(f"[{username}](https://stats.fm/user/{username}) has been linked with success.")
    
    @statsfm.command(
        name="nowplaying",
        description="Get your current playing track on Stats.fm",
        aliases=["np"]
    )
    @app_commands.describe(username="Stats.fm username (optional)")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def statsfm_nowplaying(self, ctx: commands.Context, username: Optional[str] = None):
        """Get your current playing track on Stats.fm"""
        async with ctx.typing():
            user_id = str(ctx.author.id)
            
            async with self.bot.db.pool.acquire() as conn:
                if username is None:
                    result = await conn.fetchrow(
                        "SELECT statsfm_username FROM statsfm_usernames WHERE user_id = $1", 
                        user_id
                    )
                    
                    if not result or not result['statsfm_username']:
                        return await ctx.warning(
                            f"You haven't set your Stats.fm username yet. "
                            f"Use `/statsfm set` to set it."
                        )
                    
                    statsfm_username = result['statsfm_username']
                else:
                    statsfm_username = username
                
                headers = {"User-Agent": "Heist Bot/1.0"}
                is_playing = True
                last_seen = None
                current_track = None
                
                try:
                    async with self.session.get(
                        f"https://api.stats.fm/api/v1/users/{statsfm_username}/streams/current",
                        headers=headers
                    ) as response:
                        if response.status == 404:
                            return await ctx.warning(f"Could not find Stats.fm user with username `{statsfm_username}`.")
                        elif response.status == 409:
                            return await ctx.warning("Please re-link your Spotify to the Stats.fm account you're using.")
                        elif response.status != 200:
                            return await ctx.warning("The Stats.fm API is currently unavailable.")
                        data = await response.json()
        
                    if not data or not isinstance(data.get('item'), dict):
                        is_playing = False
                        async with self.session.get(
                            f"https://api.stats.fm/api/v1/users/{statsfm_username}/streams/recent",
                            headers=headers
                        ) as response:
                            if response.status != 200:
                                return await ctx.warning("You're currently not listening to something.")
                            recent_data = await response.json()
                            
                            if not recent_data or not recent_data.get('items') or not recent_data['items']:
                                return await ctx.warning("No recent listening activity found.")
                            
                            item = recent_data['items'][0]
                            current_track = item.get('track')
                            end_time = item.get('endTime')
                            
                            if end_time:
                                end_datetime = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                                now = datetime.now(timezone.utc)
                                time_diff = now - end_datetime
                                
                                minutes = int(time_diff.total_seconds() / 60)
                                hours = int(minutes / 60)
                                days = int(hours / 24)
                                months = int(days / 30)
                                years = int(days / 365)
                                
                                if years > 0:
                                    last_seen = f"{years} year{'s' if years != 1 else ''} ago"
                                elif months > 0:
                                    last_seen = f"{months} month{'s' if months != 1 else ''} ago"
                                elif days > 0:
                                    last_seen = f"{days} day{'s' if days != 1 else ''} ago"
                                elif hours > 0:
                                    last_seen = f"{hours} hour{'s' if hours != 1 else ''} ago"
                                else:
                                    last_seen = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
                    else:
                        current_track = data['item'].get('track')
                        is_playing = data['item'].get('isPlaying', False)
                        
                    if not current_track:
                        return await ctx.warning("Failed to get track information.")
        
                    song_name = current_track['name']
                    artist_name = current_track['artists'][0]['name']
                    album_name = current_track['albums'][0]['name']
                    cover_url = current_track['albums'][0].get('image', None)
                    
                    if is_playing:
                        progress_ms = data['item']['progressMs']
                        duration_ms = current_track['durationMs']
                        device_name = data['item']['deviceName']
                        platform = data['item']['platform'].capitalize()
                    else:
                        progress_ms = current_track['durationMs']
                        duration_ms = current_track['durationMs']
        
                    embed_color = CONFIG['embed_colors']['default']
                    if cover_url:
                        try:
                            async with self.session.get(cover_url) as resp:
                                if resp.status == 200:
                                    image_data = await resp.read()
                                    embed_color = await self.get_dominant_color(image_data)
                        except Exception:
                            pass
        
                    progress_bar_task = asyncio.create_task(self.create_progress_bar(embed_color, progress_ms, duration_ms))
                    
                    display_name = None
                    async with self.session.get(
                        f"https://api.stats.fm/api/v1/users/{statsfm_username}/",
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            user_data = await response.json()
                            if user_data and isinstance(user_data.get('item'), dict):
                                display_name = user_data['item'].get('displayName', statsfm_username)
                    
                    spotify_id = None
                    for ext_id in current_track.get('externalIds', {}).get('spotify', []):
                        if ext_id:
                            spotify_id = ext_id
                            break
                            
                    spotify_url = f"https://open.spotify.com/track/{spotify_id}" if spotify_id else None
                    artist_url = f"https://stats.fm/artist/{current_track['artists'][0]['id']}"
                    album_url = f"https://stats.fm/album/{current_track['albums'][0]['id']}"
        
                    description = f"-# [{artist_name}]({artist_url}) • [*{album_name}*]({album_url})"
                    
                    if is_playing:
                        progress = f"{progress_ms//60000}:{str(progress_ms//1000%60).zfill(2)}"
                        duration = f"{duration_ms//60000}:{str(duration_ms//1000%60).zfill(2)}"
                        description += f"\n-# **`{progress}/{duration}`**"
                        
                        if cover_url:
                            try:
                                async with self.session.get(cover_url) as resp:
                                    if resp.status == 200:
                                        image_data = await resp.read()
                                        embed_color = await self.get_dominant_color(image_data)
                            except Exception:
                                embed_color = CONFIG['embed_colors']['default']
                        if device_name:
                            description += f"\n-# on 📱 **{device_name}**"
                    else:
                        description += f"\n-# **Paused**" if not last_seen else f"\n-# **Last listened {last_seen}**"
        
                    embed = Embed(
                        title=f"**{song_name}**",
                        description=description,
                        color=embed_color
                    )
                    
                    if cover_url:
                        embed.set_thumbnail(url=cover_url)
                    
                    embed.set_author(
                        name=f"{ctx.author.name} · @{statsfm_username}",
                        icon_url=ctx.author.display_avatar.url,
                        url=f"https://stats.fm/user/{statsfm_username}"
                    )
                    
                    if spotify_url:
                        embed.url = spotify_url
                        
                    progress_bar = await progress_bar_task
                    embed.set_image(url="attachment://progress.png")
                    
               
                    embed.set_footer(
                        text=f"stats.fm · {display_name or statsfm_username}", 
                        icon_url="https://git.cursi.ng/statsfm_logo.png"
                    )
                    
                    spotify_preview = current_track.get('spotifyPreview')
                    apple_preview = current_track.get('appleMusicPreview')
                    has_audio = bool(spotify_preview or apple_preview)
        
                    paginator = Paginator(
                        bot=self.bot,
                        embeds=[embed],
                        destination=ctx,
                        timeout=360,
                        invoker=ctx.author.id,
                        files=[progress_bar]
                    )
                                            
                    if spotify_url:
                        paginator.add_link_button(
                            url=spotify_url,
                            emoji=discord.PartialEmoji.from_str("<:spotify:1274904265114124308>"),
                            persist=True
                        )
                    else:
                        paginator.add_link_button(
                            url="https://spotify.com",
                            emoji=discord.PartialEmoji.from_str("<:spotify:1274904265114124308>"),
                            persist=True,
                            disabled=True
                        )
                    
                    async def audio_preview_callback(interaction, view):
                        await interaction.response.defer(ephemeral=True)
                        preview_url = spotify_preview or apple_preview
                        if preview_url:
                            await AudioPreviewHandler(self.session).send_preview(interaction, preview_url)
                        else:
                            await interaction.followup.send("No audio preview available", ephemeral=True)
                    
                    paginator.add_custom_button(
                        callback=audio_preview_callback,
                        emoji=discord.PartialEmoji.from_str("<:audio:1345517095101923439>"),
                        style=discord.ButtonStyle.secondary,
                        disabled=not has_audio,
                        custom_id="nowplayingaudio"
                    )
                    
                    await paginator.start()
        
                except Exception as e:
                    await ctx.warning(f"An error occurred while fetching Stats.fm data\n{e}")
    
    async def create_progress_bar(self, color: int, progress_ms: int, duration_ms: int):
        def _render():
            width, height = 300, 10
            image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            red = (color >> 16) & 255
            green = (color >> 8) & 255
            blue = color & 255
            progress = progress_ms / duration_ms if duration_ms > 0 else 1
            progress_width = int(width * progress)
            draw.rectangle([(0, 0), (width, height)], fill=(255, 255, 255, 50))
            draw.rectangle([(0, 0), (progress_width, height)], fill=(red, green, blue, 255))
            
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            return discord.File(img_byte_arr, 'progress.png')
        
        return await asyncio.to_thread(_render)
    
    @lastfm.command(
        name="nowplaying",
        description="Get your current playing track on Last.fm",
        aliases=["np"]
    )
    @app_commands.describe(username="Last.fm username (optional)")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def lastfm_nowplaying(self, ctx: commands.Context, username: Optional[str] = None):
        """Get your current playing track on Last.fm"""
        async with ctx.typing():
            user_id = str(ctx.author.id)
            
            async with self.bot.db.pool.acquire() as conn:
                result = await conn.fetchrow(
                    "SELECT l.lastfm_username, s.lastfm_state "
                    "FROM lastfm_usernames l "
                    "LEFT JOIN settings s ON l.user_id = s.user_id "
                    "WHERE l.user_id = $1", 
                    user_id
                )
                
                if username is None:
                    if not result or not result['lastfm_username']:
                        return await ctx.warning(
                            f"You haven't set your Last.fm username yet. "
                            f"Use `lastfm set` to set it."
                        )
                    
                    lastfm_username = result['lastfm_username']
                    lastfm_visibility = result.get('lastfm_state', 'Show')
                else:
                    lastfm_username = username
                    lastfm_visibility = 'Show'
                
                user_info_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={lastfm_username}&api_key={self.LASTFM_KEY}&format=json"
                recent_tracks_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={lastfm_username}&api_key={self.LASTFM_KEY}&format=json&limit=1"
                
                async with self.session.get(user_info_url) as user_response, \
                       self.session.get(recent_tracks_url) as tracks_response:
                    
                    if user_response.status != 200 or tracks_response.status != 200:
                        return await ctx.warning(f"Failed to fetch data from Last.fm. Status codes: {user_response.status}, {tracks_response.status}")
                    
                    user_data = await user_response.json()
                    tracks_data = await tracks_response.json()
                    
                    if 'error' in user_data or 'error' in tracks_data:
                        return await ctx.warning(f"Last.fm error: {user_data.get('message', tracks_data.get('message', 'Unknown error'))}")
                    
                    if 'recenttracks' not in tracks_data or not tracks_data['recenttracks'].get('track'):
                        return await ctx.warning(f"No recent tracks found for user {lastfm_username}.")
                    
                    tracks = tracks_data['recenttracks']['track']
                    if not tracks:
                        return await ctx.warning(f"No recent tracks found for user {lastfm_username}.")
                    
                    track = tracks[0]
                    artist_name = track['artist']['#text']
                    track_name = track['name']
                    album_name = track.get('album', {}).get('#text', '')
                    
                    artistenc = urllib.parse.quote(artist_name)
                    trackenc = urllib.parse.quote(track_name)
                    albumenc = urllib.parse.quote(album_name) if album_name else ''
                    
                    now_playing = '@attr' in track and 'nowplaying' in track['@attr'] and track['@attr']['nowplaying'] == 'true'
                    
                    track_info_url = f"http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={self.LASTFM_KEY}&artist={artistenc}&track={trackenc}&username={lastfm_username}&format=json&limit=1"
                    album_info_url = f"http://ws.audioscrobbler.com/2.0/?method=album.getInfo&api_key={self.LASTFM_KEY}&artist={artistenc}&album={albumenc}&username={lastfm_username}&format=json&limit=1" if album_name else None
                    artist_info_url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getInfo&api_key={self.LASTFM_KEY}&artist={artistenc}&username={lastfm_username}&format=json&limit=1"
                    
                    responses = await asyncio.gather(
                        self.session.get(track_info_url),
                        self.session.get(album_info_url) if album_info_url else asyncio.sleep(0),
                        self.session.get(artist_info_url),
                        return_exceptions=True
                    )
                    
                    track_info_response = responses[0]
                    album_info_response = responses[1] if album_info_url else None
                    artist_info_response = responses[2]
                    
                    track_scrobbles = 0
                    album_scrobbles = 0
                    artist_scrobbles = 0
                    total_scrobbles = int(user_data['user'].get('playcount', 0)) if 'user' in user_data else 0
                    
                    if isinstance(track_info_response, aiohttp.ClientResponse) and track_info_response.status == 200:
                        track_data = await track_info_response.json()
                        if 'track' in track_data and 'userplaycount' in track_data['track']:
                            track_scrobbles = int(track_data['track']['userplaycount'])
                    
                    if album_info_url and isinstance(album_info_response, aiohttp.ClientResponse) and album_info_response.status == 200:
                        album_data = await album_info_response.json()
                        if 'album' in album_data and 'userplaycount' in album_data['album']:
                            album_scrobbles = int(album_data['album']['userplaycount'])
                    
                    if isinstance(artist_info_response, aiohttp.ClientResponse) and artist_info_response.status == 200:
                        artist_data = await artist_info_response.json()
                        if 'artist' in artist_data and 'stats' in artist_data['artist']:
                            artist_scrobbles = int(artist_data['artist']['stats'].get('userplaycount', 0))
                    
                    cover_art_url = track.get('image', [])[-1].get('#text') if track.get('image') else None
                    
                    artist_url = f"https://www.last.fm/music/{artistenc}"
                    album_url = f"https://www.last.fm/music/{artistenc}/{albumenc}" if album_name else None
                    track_url = track.get('url', f"https://www.last.fm/music/{artistenc}/_/{trackenc}")
                    
                    spotify_track_url = None
                    try:
                        spotify_url = f"http://127.0.0.1:2053/api/search?lastfm_username={lastfm_username}&track_name={trackenc}&artist_name={artistenc}"
                        
                        headers = {"X-API-Key": self.HEIST_KEY}
                        async with self.session.get(spotify_url, headers=headers) as spotify_response:
                            if spotify_response.status == 200:
                                spotify_data = await spotify_response.json()
                                spotify_track_url = spotify_data.get('spotify_link')
                            else:
                                self.logger.warning(f"Failed to fetch Spotify URL. Status code: {spotify_response.status}")
                    except Exception as e:
                        self.logger.error(f"Error fetching Spotify URL: {str(e)}")
                        pass
                    
                    preview_handler = AudioPreviewHandler(self.session)
                    preview_url = await preview_handler.get_preview(track_name=track_name, artist_name=artist_name)
                    
                    if 'date' in track:
                        timestamp = int(track['date']['uts'])
                        timestamp_str = f"<t:{timestamp}:R>"
                    else:
                        timestamp_str = "Now playing"
                    
                    embed_color = CONFIG['embed_colors']['default']
                    if cover_art_url:
                        try:
                            async with self.session.get(cover_art_url) as resp:
                                if resp.status == 200:
                                    image_data = await resp.read()
                                    
                                    embed_color = await self.get_dominant_color(image_data)
                        except Exception:
                            pass
                    
                    embed = Embed(
                        title=track_name,
                        url=track_url,
                        color=embed_color
                    )
                    
                    display_username = "(hidden)" if lastfm_visibility == 'Hide' else lastfm_username
                    author_text = f"Now playing for {display_username}" if now_playing else f"Last track for {display_username}"
                    author_url = None if lastfm_visibility == 'Hide' else f"https://last.fm/user/{lastfm_username}"
                    
                    embed.set_author(
                        name=author_text,
                        icon_url=ctx.author.display_avatar.url,
                        url=author_url
                    )
                    
                    now_playing_description = f"[{artist_name}]({artist_url})"
                    if album_name:
                        now_playing_description += f" • [*{album_name}*]({album_url})"
                    
                    embed.description = now_playing_description
                    
                    scrobble_info = f"{track_scrobbles} track scrobble{'s' if track_scrobbles != 1 else ''}"
                    if album_name:
                        scrobble_info += f" · {album_scrobbles} album scrobble{'s' if album_scrobbles != 1 else ''}\n"
                    scrobble_info += f"{artist_scrobbles} artist scrobble{'s' if artist_scrobbles != 1 else ''}"
                    scrobble_info += f" · {total_scrobbles} total scrobble{'s' if total_scrobbles != 1 else ''}"
                    
                    if cover_art_url:
                        embed.set_thumbnail(url=cover_art_url)
                        
                    embed.set_footer(
                        text=f"{scrobble_info}", 
                        icon_url="https://git.cursi.ng/lastfm_logo.png"
                    )
    
                    paginator = Paginator(
                        bot=self.bot,
                        embeds=[embed],
                        destination=ctx,
                        timeout=360,
                        invoker=ctx.author.id
                    )
                                            
                    if spotify_track_url:
                        paginator.add_link_button(
                            url=spotify_track_url,
                            emoji=discord.PartialEmoji.from_str("<:spotify:1274904265114124308>"),
                            persist=True
                        )
                    else:
                        paginator.add_link_button(
                            url="https://spotify.com",
                            emoji=discord.PartialEmoji.from_str("<:spotify:1274904265114124308>"),
                            persist=True,
                            disabled=True
                        )
                    
                    async def audio_preview_callback(interaction, view):
                        await interaction.response.defer(ephemeral=True)
                        if preview_url:
                            await preview_handler.send_preview(interaction, preview_url)
                        else:
                            await interaction.followup.send("No audio preview available", ephemeral=True)
                    
                    paginator.add_custom_button(
                        callback=audio_preview_callback,
                        emoji=discord.PartialEmoji.from_str("<:audio:1345517095101923439>"),
                        style=discord.ButtonStyle.secondary,
                        disabled=not bool(preview_url),
                        custom_id="nowplayingaudio"
                    )
                    
                    await paginator.start()

    @lastfm.command(
        name="set",
        description="Set your Last.fm username"
    )
    @app_commands.describe(username="Your Last.fm username")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def lastfm_set(self, ctx: commands.Context, username: str):
        """Set your Last.fm username"""
   
        if not username.replace('_', '').isalnum():
            return await ctx.warning("Username can only contain letters, numbers, and underscores.")
      
        if ' ' in username:
            return await ctx.warning("Username cannot contain spaces.")
        user_id = str(ctx.author.id)
        
        user_info_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={username}&api_key={self.LASTFM_KEY}&format=json"
        async with self.session.get(user_info_url) as response:
            if response.status != 200:
                return await ctx.warning(f"Failed to verify Last.fm username. Please try again later.")
                
            data = await response.json()
            if 'error' in data:
                return await ctx.warning(f"Invalid Last.fm username. Please check and try again.")
        
        async with self.bot.db.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO lastfm_usernames (user_id, lastfm_username)
                    VALUES ($1, $2)
                    ON CONFLICT (user_id) DO UPDATE
                    SET lastfm_username = EXCLUDED.lastfm_username
                """, user_id, username)

                await conn.execute("""
                    UPDATE lastfm_friends
                    SET friend_lastfm_name = $1
                    WHERE friend_id = $2
                """, username, user_id)

                await ctx.success(f"[{username}](https://last.fm/user/{username}) has been linked with success.")
    
    @lastfm.command(
        name="profile",
        description="View Last.fm profile"
    )
    @app_commands.describe(username="Last.fm username to lookup (optional)")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def lastfm_profile(self, ctx: commands.Context, username: Optional[str] = None):
        """View Last.fm profile"""
        async with ctx.typing():
            user_id = str(ctx.author.id)
            
            async with self.bot.db.pool.acquire() as conn:
                if username is None:
                    result = await conn.fetchrow(
                        "SELECT lastfm_username FROM lastfm_usernames WHERE user_id = $1", 
                        user_id
                    )
                    
                    visibility_result = await conn.fetchrow(
                        "SELECT lastfm_state FROM settings WHERE user_id = $1",
                        user_id
                    )
                    
                    if not result or not result['lastfm_username']:
                        return await ctx.warning(
                            f"You haven't set your Last.fm username yet. "
                            f"Use `lastfm set` to set it."
                        )
                    
                    lastfm_username = result['lastfm_username']
                    lastfm_visibility = visibility_result['lastfm_state'] if visibility_result else 'Show'
                else:
                    lastfm_username = username
                    lastfm_visibility = 'Show'
                
                is_hidden = lastfm_visibility == 'Hide'
                display_username = "Hidden" if is_hidden else lastfm_username
                user_url = None if is_hidden else f"https://last.fm/user/{lastfm_username}"
                
                try:
                    user_info_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={lastfm_username}&api_key={self.LASTFM_KEY}&format=json"
                    async with self.session.get(user_info_url) as response:
                        if response.status != 200:
                            return await ctx.warning("Failed to fetch Last.fm profile data.")
                        user_info = await response.json()
                        if 'error' in user_info:
                            return await ctx.warning(f"Last.fm error: {user_info.get('message', 'Unknown error')}")
                        
                        user_info = user_info.get('user', {})
                    
                    top_artists_url = f"http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user={lastfm_username}&api_key={self.LASTFM_KEY}&format=json&limit=5"
                    async with self.session.get(top_artists_url) as response:
                        if response.status == 200:
                            top_artists_data = await response.json()
                            top_artists = top_artists_data.get('topartists', {}).get('artist', [])
                        else:
                            top_artists = []
                    
                    unique_counts = {'artists': 0, 'albums': 0, 'tracks': 0}
                    for method in ['artist', 'album', 'track']:
                        url = f"http://ws.audioscrobbler.com/2.0/?method=user.gettop{method}s&user={lastfm_username}&api_key={self.LASTFM_KEY}&format=json&limit=1"
                        async with self.session.get(url) as response:
                            if response.status == 200:
                                data = await response.json()
                                unique_counts[f"{method}s"] = int(data.get(f'top{method}s', {}).get('@attr', {}).get('total', 0))
                    
                    recent_tracks_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={lastfm_username}&api_key={self.LASTFM_KEY}&format=json&limit=1"
                    async with self.session.get(recent_tracks_url) as response:
                        recent_tracks_data = await response.json()
                        last_track = None
                        if response.status == 200:
                            tracks = recent_tracks_data.get('recenttracks', {}).get('track', [])
                            if tracks:
                                last_track = tracks[0]
                    
                    top_tracks_url = f"http://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user={lastfm_username}&api_key={self.LASTFM_KEY}&format=json&limit=5"
                    async with self.session.get(top_tracks_url) as response:
                        if response.status == 200:
                            top_tracks_data = await response.json()
                            top_tracks = top_tracks_data.get('toptracks', {}).get('track', [])
                        else:
                            top_tracks = []
                    
                    top_albums_url = f"http://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user={lastfm_username}&api_key={self.LASTFM_KEY}&format=json&limit=5"
                    async with self.session.get(top_albums_url) as response:
                        if response.status == 200:
                            top_albums_data = await response.json()
                            top_albums = top_albums_data.get('topalbums', {}).get('album', [])
                        else:
                            top_albums = []
                            
                    friended = await conn.fetchval(
                        "SELECT COUNT(*) FROM lastfm_friends WHERE user_id = $1", user_id
                    )
                    befriendedby = await conn.fetchval(
                        "SELECT COUNT(*) FROM lastfm_friends WHERE friend_id = $1", user_id
                    )
                    
                    discord_display_name = ctx.author.display_name
                    lastfm_display = "Hidden" if is_hidden else (user_info.get('realname') or user_info.get('name', lastfm_username))
                    country = user_info.get('country') if not is_hidden else None
                    registered = int(user_info.get('registered', {}).get('unixtime', 0))
                    playcount = int(user_info.get('playcount', 0))
                    profile_picture = user_info.get('image', [{}])[-1].get('#text', ctx.author.display_avatar.url)
                    
                    embed = Embed(
                        title=f"{discord_display_name} (@{display_username})" if discord_display_name else f"@{display_username}", 
                        url=user_url,
                        color=await self.get_dominant_color(await self.session.get(profile_picture).read()) if profile_picture else None
                    )
                    
                    embed.description = f"-# **Country:** {country}\n-# **Type:** User" if country else "-# **Type:** User"
                    
                    embed.add_field(name="Scrobbles", value=f"{playcount:,}", inline=True)
                    embed.add_field(name="Artists", value=f"{unique_counts['artists']:,}", inline=True)
                    embed.add_field(name="Albums", value=f"{unique_counts['albums']:,}", inline=True)
                    embed.add_field(name="Created", value=f"<t:{registered}:D>", inline=True)
                    
                    if last_track:
                        track_name = last_track.get('name', 'Unknown')
                        artist_name = last_track.get('artist', {}).get('#text', 'Unknown')
                        track_url = last_track.get('url', '')
                        
                        if '@attr' in last_track and 'nowplaying' in last_track['@attr'] and last_track['@attr']['nowplaying'] == 'true':
                            embed.add_field(
                                name="Now Playing",
                                value=f"[{track_name}]({track_url}) by **{artist_name}**",
                                inline=True
                            )
                        elif 'date' in last_track:
                            timestamp = int(last_track['date']['uts'])
                            embed.add_field(
                                name="Last Scrobble",
                                value=f"[{track_name}]({track_url}) by **{artist_name}**\n<t:{timestamp}:R>",
                                inline=True
                            )
                    
                    embed.add_field(
                        name="Community Stats", 
                        value=f"-# **Friends:** {friended}\n-# **Followers:** {befriendedby}\n-# **Following:** {friended}", 
                        inline=True
                    )
                    
                    top_artists_str = "\n".join([f"-# **{i+1}.** [{artist['name']}]({artist['url']}) ({artist['playcount']})" for i, artist in enumerate(top_artists[:5])])
                    embed.add_field(name="Top Artists", value=top_artists_str or "No artists found.", inline=True)
                    
                    top_tracks_str = "\n".join([f"-# **{i+1}.** [{track['name']}]({track['url']}) ({track['playcount']})" for i, track in enumerate(top_tracks[:5])])
                    embed.add_field(name="Top Tracks", value=top_tracks_str or "No tracks found.", inline=True)
                    
                    top_albums_str = "\n".join([f"-# **{i+1}.** [{album['name']}]({album['url']}) ({album['playcount']})" for i, album in enumerate(top_albums[:5])])
                    embed.add_field(name="Top Albums", value=top_albums_str or "No albums found.", inline=True)
                    
                    embed.set_thumbnail(url=profile_picture)
                    embed.set_footer(
                        text=f"{display_username} • {friended} friends • befriended by {befriendedby}", 
                        icon_url="https://git.cursi.ng/lastfm_logo.png"
                    )
                    
                    paginator = Paginator(
                        bot=self.bot,
                        embeds=[embed],
                        destination=ctx,
                        timeout=360,
                        invoker=ctx.author.id
                    )
                    
                    if not is_hidden:
                        paginator.add_link_button(
                            url=f"https://last.fm/user/{lastfm_username}",
                            emoji="🔗",
                            label="Last.fm Profile"
                        )
                    
                    await paginator.start()
                    
                except Exception as e:
                    await ctx.warning(f"An error occurred while fetching Last.fm profile")

    @lastfm.command(
        name="artist",
        description="Get information about a Last.fm artist"
    )
    @app_commands.describe(artist="Name of the artist")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def lastfm_artist(self, ctx: commands.Context, artist: str):
        """Get information about a Last.fm artist"""
        async with ctx.typing():
            user_id = str(ctx.author.id)
            
            async with self.bot.db.pool.acquire() as conn:
                result = await conn.fetchrow(
                    "SELECT lastfm_username FROM lastfm_usernames WHERE user_id = $1", 
                    user_id
                )
                
                if not result or not result['lastfm_username']:
                    return await ctx.warning(
                        f"You haven't set your Last.fm username yet. "
                        f"Use `lastfm set` to set it."
                    )
                
                lastfm_username = result['lastfm_username']
            
            artist_name_escaped = urllib.parse.quote(artist)
            
            artist_info_url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist={artist_name_escaped}&api_key={self.LASTFM_KEY}&format=json"
            user_artist_info_url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist={artist_name_escaped}&username={lastfm_username}&api_key={self.LASTFM_KEY}&format=json"
            artist_tags_url = f"http://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&artist={artist_name_escaped}&api_key={self.LASTFM_KEY}&format=json"
            user_info_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={lastfm_username}&api_key={self.LASTFM_KEY}&format=json"
            
            try:
                artist_info_response, user_artist_info_response, tags_response, user_info_response = await asyncio.gather(
                    self.session.get(artist_info_url),
                    self.session.get(user_artist_info_url),
                    self.session.get(artist_tags_url),
                    self.session.get(user_info_url)
                )
                
                if artist_info_response.status != 200:
                    return await ctx.warning("Failed to retrieve artist information.")
                
                artist_info_data = await artist_info_response.json()
                if "artist" not in artist_info_data:
                    return await ctx.warning("Artist not found. Are you sure they have a Last.fm page?")
                
                artist_info = artist_info_data["artist"]
                artist_playcount = int(artist_info["stats"]["playcount"])
                artist_listeners = int(artist_info["stats"]["listeners"])
                artist_bio = artist_info.get("bio", {}).get("summary", "").split("<")[0].strip()
                
                user_artist_info_data = await user_artist_info_response.json()
                user_playcount = int(user_artist_info_data.get("artist", {}).get("stats", {}).get("userplaycount", 0))
                
                tags_data = await tags_response.json()
                top_tag = tags_data.get("toptags", {}).get("tag", [{}])[0].get("name", "Unknown")
                
                user_data = await user_info_response.json()
                total_scrobbles = int(user_data.get("user", {}).get("playcount", 0))
                
                spotify_url = f"http://127.0.0.1:2053/api/spotify/artist?artist_name={artist_name_escaped}"
                headers = {"X-API-Key": self.HEIST_KEY}
                
                try:
                    async with self.session.get(spotify_url, headers=headers) as spotify_response:
                        if spotify_response.status == 200:
                            spotify_data = await spotify_response.json()
                            artist_image = spotify_data.get('cover_art')
                        else:
                            artist_image = artist_info["image"][3]["#text"] if artist_info.get("image") else None
                except Exception:
                    artist_image = artist_info["image"][3]["#text"] if artist_info.get("image") else None
                
                percentage_of_plays = (user_playcount / total_scrobbles * 100) if total_scrobbles > 0 else 0
                
                embed_color = None
                if artist_image:
                    try:
                        async with self.session.get(artist_image) as resp:
                            if resp.status == 200:
                                image_data = await resp.read()
                                embed_color = await self.get_dominant_color(image_data)
                    except Exception:
                        pass
                
                embed = Embed(
                    description=f"`{artist_listeners:,}` listeners\n`{artist_playcount:,}` global plays\n`{user_playcount:,}` plays by you",
                    color=embed_color
                )
                
                if artist_image:
                    embed.set_thumbnail(url=artist_image)
                
                embed.set_author(
                    name=f"Artist: {artist_info['name']}", 
                    url=artist_info["url"], 
                    icon_url=ctx.author.display_avatar.url
                )
                
                if artist_bio:
                    embed.add_field(
                        name="Summary", 
                        value=artist_bio[:1024], 
                        inline=False
                    )
                
                embed.set_footer(
                    text=f"Image source: {'Spotify' if 'spotify_data' in locals() else 'Last.fm'}\n{percentage_of_plays:.2f}% of all your scrobbles are for this artist\n{top_tag}", 
                    icon_url="https://git.cursi.ng/lastfm_logo.png"
                )
                
                paginator = Paginator(
                    bot=self.bot,
                    embeds=[embed],
                    destination=ctx,
                    timeout=360,
                    invoker=ctx.author.id
                )
                
                paginator.add_link_button(
                    url=artist_info["url"],
                    emoji="🔗",
                    label="View on Last.fm"
                )
                
                await paginator.start()
                
            except Exception as e:
                await ctx.warning(f"An error occurred while fetching artist information")

    @lastfm.command(
        name="spotify",
        description="Find your current playing Last.fm song on Spotify"
    )
    @app_commands.describe(username="Last.fm username (optional)")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def lastfm_spotify(self, ctx: commands.Context, username: Optional[str] = None):
        """Find your current playing Last.fm song on Spotify"""
        async with ctx.typing():
            user_id = str(ctx.author.id)
            
            async with self.bot.db.pool.acquire() as conn:
                if username is None:
                    result = await conn.fetchrow(
                        "SELECT lastfm_username FROM lastfm_usernames WHERE user_id = $1", 
                        user_id
                    )
                    
                    if not result or not result['lastfm_username']:
                        return await ctx.warning(
                            f"You haven't set your Last.fm username yet. "
                            f"Use `lastfm set` to set it."
                        )
                    
                    lastfm_username = result['lastfm_username']
                else:
                    lastfm_username = username
                
                recent_tracks_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={lastfm_username}&api_key={self.LASTFM_KEY}&format=json&limit=1"
                
                try:
                    async with self.session.get(recent_tracks_url) as response:
                        if response.status != 200:
                            return await ctx.warning(f"Failed to fetch data from Last.fm. Status code: {response.status}")
                        
                        data = await response.json()
                        if 'error' in data:
                            return await ctx.warning(f"Last.fm error: {data.get('message', 'Unknown error')}")
                        
                        tracks = data.get('recenttracks', {}).get('track', [])
                        
                        if not tracks:
                            return await ctx.warning(f"No recent tracks found for user {lastfm_username}.")
                        
                        track = tracks[0]
                        artist_name = track['artist']['#text']
                        track_name = track['name']
                        
                        spotify_url = f"http://127.0.0.1:2053/api/search?track_name={urllib.parse.quote(track_name)}&artist_name={urllib.parse.quote(artist_name)}"
                        
                        headers = {"X-API-Key": self.HEIST_KEY}
                        async with self.session.get(spotify_url, headers=headers) as spotify_response:
                            if spotify_response.status == 200:
                                spotify_data = await spotify_response.json()
                                spotify_link = spotify_data.get('spotify_link')
                                
                                if spotify_link:
                                    embed = Embed(
                                        title="Track Found on Spotify!",
                                        description=f"**{track_name}** by **{artist_name}**\n\n[Open in Spotify]({spotify_link})",
                                        color=0x1DB954
                                    )
                                    
                                    if spotify_data.get('cover_art'):
                                        embed.set_thumbnail(url=spotify_data['cover_art'])
                                    
                                    embed.set_footer(
                                        text=f"{lastfm_username} • Last.fm to Spotify", 
                                        icon_url="https://git.cursi.ng/lastfm_logo.png"
                                    )
                                    
                                    paginator = Paginator(
                                        bot=self.bot,
                                        embeds=[embed],
                                        destination=ctx,
                                        timeout=360,
                                        invoker=ctx.author.id
                                    )
                                    
                                    paginator.add_link_button(
                                        url=spotify_link,
                                        emoji=discord.PartialEmoji.from_str("<:spotify:1274904265114124308>"),
                                        persist=True
                                    )
                                    
                                    await paginator.start()
                                else:
                                    await ctx.warning(f"Couldn't find '{track_name}' by '{artist_name}' on Spotify.")
                            else:
                                await ctx.warning(f"Failed to search Spotify. Status code: {spotify_response.status}")
                
                except Exception as e:
                    await ctx.warning(f"An error occurred")

    @lastfm.group(
        name="friends",
        description="Last.fm friends management",
        aliases=["f"]
    )
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def lastfm_friends(self, ctx: commands.Context):
        """Manage your Last.fm friends"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @lastfm_friends.command(
        name="add",
        description="Add someone as a Last.fm friend"
    )
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    @app_commands.describe(user="The user you want to add as a Last.fm friend")
    async def lastfm_add_friend(self, ctx: commands.Context, user: discord.User):
        """Add someone as a Last.fm friend"""
        user_id = str(ctx.author.id)
        friend_id = str(user.id)
        
        if user_id == friend_id:
            return await ctx.warning("You cannot add yourself as a friend!")
        
        async with self.bot.db.pool.acquire() as conn:
            try:
                visibility_result = await conn.fetchrow(
                    "SELECT lastfm_state FROM settings WHERE user_id = $1",
                    friend_id
                )
                friend_visibility = visibility_result['lastfm_state'] if visibility_result else 'Show'
                
                if friend_visibility == 'Hide':
                    return await ctx.warning(
                        f"{user.name} has their Last.fm hidden, you can't add them."
                    )
                
                user_result = await conn.fetchrow(
                    "SELECT lastfm_username FROM lastfm_usernames WHERE user_id = $1",
                    user_id
                )
                friend_result = await conn.fetchrow(
                    "SELECT lastfm_username FROM lastfm_usernames WHERE user_id = $1",
                    friend_id
                )
                
                if not user_result:
                    return await ctx.warning(
                        f"You haven't set your Last.fm username yet. "
                        f"Use `lastfm set` to set it first."
                    )
                
                if not friend_result:
                    return await ctx.warning(
                        f"{user.name} hasn't linked their Last.fm account with Heist."
                    )
                
                existing_friend = await conn.fetchrow(
                    "SELECT 1 FROM lastfm_friends WHERE user_id = $1 AND friend_id = $2",
                    user_id, friend_id
                )
                
                if existing_friend:
                    return await ctx.warning(
                        f"You're already friends with {user.name} on Last.fm!"
                    )
                
                await conn.execute("""
                    INSERT INTO lastfm_friends (user_id, friend_id)
                    VALUES ($1, $2)
                """, user_id, friend_id)
                
                await ctx.success(f"Successfully added {user.name} as a Last.fm friend!")
                
            except Exception as e:
                await ctx.warning(f"Database error while adding friend")

    @lastfm_friends.command(
        name="remove",
        description="Remove a user from your Last.fm friends list"
    )
    @app_commands.describe(user="The user you want to remove as a Last.fm friend")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def lastfm_remove_friend(self, ctx: commands.Context, user: discord.User):
        """Remove a user from your Last.fm friends list"""
        user_id = str(ctx.author.id)
        friend_id = str(user.id)
        
        if user_id == friend_id:
            return await ctx.warning("You cannot remove yourself as a friend!")
        
        async with self.bot.db.pool.acquire() as conn:
            try:
                friend = await conn.fetchrow("""
                    SELECT 1 
                    FROM lastfm_friends
                    WHERE user_id = $1 AND friend_id = $2
                """, user_id, friend_id)
                
                if not friend:
                    return await ctx.warning(
                        f"{user.name} is not in your Last.fm friends list!"
                    )
                
                await conn.execute("""
                    DELETE FROM lastfm_friends
                    WHERE user_id = $1 AND friend_id = $2
                """, user_id, friend_id)
                
                await ctx.success(f"Successfully removed {user.name} from your Last.fm friends!")
                
            except Exception as e:
                await ctx.warning(f"Database error while removing friend")
    
    @lastfm_friends.command(
        name="list",
        description="View your Last.fm friends list"
    )
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def lastfm_friends_list(self, ctx: commands.Context):
        """View your Last.fm friends list"""
        user_id = str(ctx.author.id)
        
        async with self.bot.db.pool.acquire() as conn:
            try:
                friends = await conn.fetch("""
                    SELECT 
                        f.friend_id, 
                        lf.lastfm_username,
                        COALESCE(s.lastfm_state, 'Show') as visibility
                    FROM lastfm_friends f
                    JOIN lastfm_usernames lf ON f.friend_id = lf.user_id
                    LEFT JOIN settings s ON f.friend_id = s.user_id
                    WHERE f.user_id = $1
                """, user_id)
                
                if not friends:
                    return await ctx.warning(
                        "You haven't added any Last.fm friends yet! Use `/lastfm friends add` to add friends."
                    )
                
                friend_data = []
                for friend in friends:
                    try:
                        friend_user = await self.bot.fetch_user(int(friend['friend_id']))
                        discord_link = f"[{friend_user.name}](discord://-/users/{friend_user.id})"
                    except:
                        discord_link = f"Unknown User ({friend['friend_id']})"
                    
                    lastfm_link = (f"[@{friend['lastfm_username']}](https://www.last.fm/user/{friend['lastfm_username']})" 
                                  if friend['visibility'] != 'Hide' else "hidden")
                    
                    friend_data.append((discord_link.lower(), f"• {discord_link} ({lastfm_link})"))
                
                friend_data.sort(key=lambda x: x[0])
                friend_entries = [x[1] for x in friend_data]
                
                friends_per_page = 10
                total_pages = (len(friend_entries) + friends_per_page - 1) // friends_per_page
                
                embeds = []
                for i in range(total_pages):
                    start_idx = i * friends_per_page
                    end_idx = min(start_idx + friends_per_page, len(friend_entries))
                    current_page_entries = friend_entries[start_idx:end_idx]
                    
                    embed = Embed(
                        title="Your Last.fm Friends",
                        description="\n".join(current_page_entries),
                        color=None
                    )
                    
                    embed.set_thumbnail(url=ctx.author.display_avatar.url)
                    embed.set_footer(
                        text=f"Total friends: {len(friend_entries)} (Page {i+1}/{total_pages})",
                        icon_url="https://git.cursi.ng/lastfm_logo.png"
                    )
                    
                    embeds.append(embed)
                
                paginator = Paginator(
                    bot=self.bot,
                    embeds=embeds,
                    destination=ctx,
                    timeout=360,
                    invoker=ctx.author.id
                )
                
                await self.add_pagination_controls(paginator, multi_page=len(embeds) > 1)
                
                await paginator.start()
                
            except Exception as e:
                await ctx.warning(f"An error occurred")

    @lastfm.group(
        name="top",
        description="Last.fm top music statistics",
        aliases=["t"]
    )
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def lastfm_top(self, ctx: commands.Context):
        """Last.fm top music statistics"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    async def fetch_top_items(self, lastfm_username, item_type, period="7day", limit=50):
        """Fetch top items (tracks, artists, albums) from Last.fm API"""
        period_mapping = {
            "7 days": "7day",
            "1 month": "1month",
            "3 months": "3month",
            "6 months": "6month",
            "1 year": "12month",
            "lifetime": "overall"
        }
        
        period_key = period_mapping.get(period, period)
        
        url = f"http://ws.audioscrobbler.com/2.0/?method=user.gettop{item_type}&user={lastfm_username}&api_key={self.LASTFM_KEY}&format=json&period={period_key}&limit={limit}"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                return None
            
            data = await response.json()
            if f'top{item_type}' not in data:
                return None
            
            result = data[f'top{item_type}']
            return result.get(item_type[:-1] if item_type.endswith('s') else item_type, [])
    
    @lastfm_top.command(
        name="tracks",
        description="Get your Last.fm top tracks"
    )
    @app_commands.describe(
        username="Last.fm username (optional)",
        period="Time period for the content"
    )
    async def lastfm_top_tracks(self, ctx: commands.Context, username: Optional[str] = None, period: str = "7 days"):
        """Get your Last.fm top tracks"""
        await self._lastfm_top_command(ctx, "tracks", username, period)
    
    @lastfm_top.command(
        name="artists",
        description="Get your Last.fm top artists"
    )
    @app_commands.describe(
        username="Last.fm username (optional)",
        period="Time period for the content"
    )
    async def lastfm_top_artists(self, ctx: commands.Context, username: Optional[str] = None, period: str = "7 days"):
        """Get your Last.fm top artists"""
        await self._lastfm_top_command(ctx, "artists", username, period)
    
    @lastfm_top.command(
        name="albums",
        description="Get your Last.fm top albums"
    )
    @app_commands.describe(
        username="Last.fm username (optional)",
        period="Time period for the content"
    )
    async def lastfm_top_albums(self, ctx: commands.Context, username: Optional[str] = None, period: str = "7 days"):
        """Get your Last.fm top albums"""
        await self._lastfm_top_command(ctx, "albums", username, period)
    
    async def _lastfm_top_command(self, ctx: commands.Context, item_type, username: Optional[str] = None, period: str = "7 days"):
        """Handler for top tracks/artists/albums commands"""
        async with ctx.typing():
            user_id = str(ctx.author.id)
            
            valid_periods = ["7 days", "1 month", "3 months", "6 months", "1 year", "lifetime"]
            if period not in valid_periods:
                return await ctx.warning(
                    f"Invalid period. Valid options are: {', '.join(valid_periods)}"
                )
            
            async with self.bot.db.pool.acquire() as conn:
                if username is None:
                    result = await conn.fetchrow(
                        "SELECT lastfm_username FROM lastfm_usernames WHERE user_id = $1", 
                        user_id
                    )
                    
                    visibility_result = await conn.fetchrow(
                        "SELECT lastfm_state FROM settings WHERE user_id = $1",
                        user_id
                    )
                    
                    if not result or not result['lastfm_username']:
                        return await ctx.warning(
                            f"You haven't set your Last.fm username yet. "
                            f"Use `lastfm set` to set it."
                        )
                    
                    real_username = result['lastfm_username']
                    visibility = visibility_result['lastfm_state'] if visibility_result else 'Show'
                    display_username = "(hidden)" if visibility == 'Hide' else real_username
                else:
                    real_username = username
                    if real_username.lower() == (await conn.fetchval("SELECT lastfm_username FROM lastfm_usernames WHERE user_id = $1", user_id) or "").lower():
                        visibility_result = await conn.fetchrow("SELECT lastfm_state FROM settings WHERE user_id = $1", user_id)
                        visibility = visibility_result['lastfm_state'] if visibility_result else 'Show'
                        display_username = "(hidden)" if visibility == 'Hide' else real_username
                    else:
                        display_username = real_username
                        visibility = 'Show'
            
            try:
                user_info_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={real_username}&api_key={self.LASTFM_KEY}&format=json"
                async with self.session.get(user_info_url) as response:
                    if response.status != 200:
                        return await ctx.warning("Failed to fetch user data from Last.fm.")
                    
                    user_info = await response.json()
                    if 'error' in user_info:
                        return await ctx.warning(f"Last.fm error: {user_info.get('message', 'Unknown error')}")
                    
                    total_scrobbles = int(user_info.get('user', {}).get('playcount', 0))
                
                period_mapping = {
                    "7 days": "7day",
                    "1 month": "1month",
                    "3 months": "3month",
                    "6 months": "6month",
                    "1 year": "12month",
                    "lifetime": "overall"
                }
                
                period_key = period_mapping[period]
                
                if item_type == "albums":
                    items = await self.fetch_top_items(real_username, "albums", period_key, 50)
                elif item_type == "artists":
                    items = await self.fetch_top_items(real_username, "artists", period_key, 50)
                else:
                    items = await self.fetch_top_items(real_username, "tracks", period_key, 50)
                
                if not items:
                    return await ctx.warning(f"No {item_type} found for this user or period.")
                
                items_per_page = 10
                total_pages = (len(items) + items_per_page - 1) // items_per_page
                
                embeds = []
                for page in range(total_pages):
                    start_idx = page * items_per_page
                    end_idx = min(start_idx + items_per_page, len(items))
                    current_page_items = items[start_idx:end_idx]
                    
                    thumbnail_url = ''
                    if current_page_items:
                        first_item = current_page_items[0]
                        
                        if item_type == "tracks":
                            album_images = first_item.get('album', {}).get('image', [])
                            for image in album_images:
                                if image.get('#text') and image.get('size') == 'large':
                                    thumbnail_url = image['#text']
                                    break
                        elif item_type == "albums":
                            images = first_item.get('image', [])
                            for image in images:
                                if image.get('#text') and image.get('size') == 'large':
                                    thumbnail_url = image['#text']
                                    break
                        elif item_type == "artists":
                            try:
                                artist_name = first_item['name']
                                artist_name_escaped = urllib.parse.quote(artist_name)
                                spotify_url = f"http://127.0.0.1:2053/api/spotify/artist?artist_name={artist_name_escaped}"
                                headers = {"X-API-Key": self.HEIST_KEY}
                                
                                async with self.session.get(spotify_url, headers=headers) as spotify_response:
                                    if spotify_response.status == 200:
                                        spotify_data = await spotify_response.json()
                                        thumbnail_url = spotify_data.get('cover_art')
                            except:
                                pass
                            
                            if not thumbnail_url:
                                images = first_item.get('image', [])
                                for image in images:
                                    if image.get('#text') and image.get('size') == 'large':
                                        thumbnail_url = image['#text']
                                        break
                    
                    description = ""
                    for i, item in enumerate(current_page_items, start=start_idx + 1):
                        if item_type == "albums" or item_type == "tracks":
                            name = item['name']
                            artist_name = item['artist']['name']
                            playcount = item['playcount']
                            artist_url = f"https://www.last.fm/music/{urllib.parse.quote(artist_name)}"
                            
                            if item_type == "tracks":
                                item_url = f"{artist_url}/_/{urllib.parse.quote(name)}"
                            else:
                                item_url = f"{artist_url}/{urllib.parse.quote(name)}"
                                
                            description += f"{i}. **[{name}]({item_url})** by [{artist_name}]({artist_url}) - *{playcount} plays*\n"
                        
                        elif item_type == "artists":
                            name = item['name']
                            playcount = item['playcount']
                            artist_url = f"https://www.last.fm/music/{urllib.parse.quote(name)}"
                            description += f"{i}. **[{name}]({artist_url})** - *{playcount} plays*\n"
                    
                    embed_color = None
                    if thumbnail_url:
                        try:
                            async with self.session.get(thumbnail_url) as resp:
                                if resp.status == 200:
                                    image_data = await resp.read()
                                    embed_color = await self.get_dominant_color(image_data)
                        except:
                            pass
                    
                    author_name = f"{display_username}'s Top {item_type.capitalize()} ({period})" if display_username != "(hidden)" else f"Top {item_type.capitalize()} ({period})"
                    author_url = f"https://last.fm/user/{real_username}" if display_username != "(hidden)" else None
                    
                    embed = Embed(
                        description=description.strip(),
                        color=embed_color
                    )
                    
                    embed.set_author(name=author_name, url=author_url, icon_url=ctx.author.display_avatar.url)
                    
                    if thumbnail_url:
                        embed.set_thumbnail(url=thumbnail_url)
                    
                    footer_text = f"Page {page + 1}/{total_pages} • {display_username} has {total_scrobbles} scrobbles"
                    embed.set_footer(text=footer_text, icon_url="https://git.cursi.ng/lastfm_logo.png")
                    
                    embeds.append(embed)
                
                paginator = Paginator(
                    bot=self.bot,
                    embeds=embeds,
                    destination=ctx,
                    timeout=360,
                    invoker=ctx.author.id
                )
                
                await self.add_pagination_controls(paginator, multi_page=len(embeds) > 1)
                
                await paginator.start()
                
            except Exception as e:
                await ctx.warning(f"An error occurred")

    @lastfm.command(
        name="latest",
        description="Get latest Last.fm scrobbles",
        aliases=["recent", "recent-tracks", "rt"]
    )
    @app_commands.describe(username="Last.fm username (optional)")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def lastfm_latest(self, ctx: commands.Context, username: Optional[str] = None):
        """Get latest Last.fm scrobbles"""
        async with ctx.typing():
            user_id = str(ctx.author.id)
            
            async with self.bot.db.pool.acquire() as conn:
                if username is None:
                    result = await conn.fetchrow(
                        "SELECT lastfm_username FROM lastfm_usernames WHERE user_id = $1", 
                        user_id
                    )
                    
                    visibility_result = await conn.fetchrow(
                        "SELECT lastfm_state FROM settings WHERE user_id = $1",
                        user_id
                    )
                    
                    if not result or not result['lastfm_username']:
                        return await ctx.warning(
                            f"You haven't set your Last.fm username yet. "
                            f"Use `lastfm set` to set it."
                        )
                    
                    real_username = result['lastfm_username']
                    visibility = visibility_result['lastfm_state'] if visibility_result else 'Show'
                    display_username = "(hidden)" if visibility == 'Hide' else real_username
                else:
                    real_username = username
                    display_username = real_username
                    visibility = 'Show'
            
            try:
                tracks_per_page = 5
                fetch_limit = 50
                recent_tracks_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={real_username}&api_key={self.LASTFM_KEY}&format=json&limit={fetch_limit}&page=1"
                
                async with self.session.get(recent_tracks_url) as response:
                    if response.status != 200:
                        return await ctx.warning("Failed to fetch tracks from Last.fm.")
                    
                    data = await response.json()
                    if 'error' in data:
                        return await ctx.warning(f"Last.fm error: {data.get('message', 'Unknown error')}")
                    
                    if 'recenttracks' not in data or not data['recenttracks'].get('track'):
                        return await ctx.warning("You haven't played anything recently.")
                    
                    total_scrobbles = int(data['recenttracks']['@attr']['total'])
                    total_pages = (total_scrobbles + tracks_per_page - 1) // tracks_per_page
                    
                    tracks = data['recenttracks']['track'][:tracks_per_page]
                    
                    async def create_embed_for_page(page_tracks, page_num):
                        embed_description = []
                        current_art = None
                        
                        for track in page_tracks:
                            track_name = track.get('name', 'Unknown Track')
                            artist_name = track.get('artist', {}).get('#text', 'Unknown Artist')
                            album_name = track.get('album', {}).get('#text', '')
                            
                            if '@attr' in track and 'nowplaying' in track['@attr'] and track['@attr']['nowplaying'] == 'true':
                                timestamp_str = "Now playing"
                            elif 'date' in track:
                                timestamp = int(track['date']['uts'])
                                timestamp_str = f"<t:{timestamp}:R>"
                            else:
                                timestamp_str = "Unknown time"
                            
                            track_url = track.get('url', '#')
                            track_hyperlink = f"[{track_name}]({track_url})"
                            
                            if not current_art:
                                for image in track.get('image', []):
                                    if image.get('size') == 'large' and image.get('#text'):
                                        current_art = image['#text']
                                        break
                            
                            if album_name:
                                embed_description.append(f"• {track_hyperlink}\n  by **{artist_name}** on *{album_name}* ({timestamp_str})\n")
                            else:
                                embed_description.append(f"• {track_hyperlink}\n  by **{artist_name}** ({timestamp_str})\n")
                        
                        lastfm_url = f"https://www.last.fm/user/{real_username}" if display_username != "(hidden)" else None
                        title = f"Latest tracks for {display_username}"
                        
                        embed = Embed(
                            description="".join(embed_description),
                            color=None
                        )
                        
                        embed.set_author(name=title, url=lastfm_url, icon_url=ctx.author.display_avatar.url)
                        embed.set_footer(
                            text=f"Page {page_num + 1}/{total_pages} • {display_username} has {total_scrobbles} scrobbles", 
                            icon_url="https://git.cursi.ng/lastfm_logo.png"
                        )
                        
                        if current_art:
                            embed.set_thumbnail(url=current_art)
                        
                        return embed
                    
                    initial_embed = await create_embed_for_page(tracks, 0)
                    
                    async def get_tracks_for_page(page):
                        api_page = (page * tracks_per_page) // fetch_limit + 1
                        api_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={real_username}&api_key={self.LASTFM_KEY}&format=json&limit={fetch_limit}&page={api_page}"
                        
                        async with self.session.get(api_url) as resp:
                            if resp.status != 200:
                                return None
                            
                            page_data = await resp.json()
                            if 'recenttracks' not in page_data or not page_data['recenttracks'].get('track'):
                                return None
                            
                            tracks_list = page_data['recenttracks']['track']
                            start_index = (page * tracks_per_page) % fetch_limit
                            end_index = start_index + tracks_per_page
                            
                            return tracks_list[start_index:end_index]
                    
                    class LastfmPaginator(Paginator):
                        def __init__(self, bot, destination, initial_embed, total_pages, invoker):
                            super().__init__(
                                bot=bot,
                                embeds=[initial_embed],
                                destination=destination,
                                timeout=360,
                                invoker=invoker
                            )
                            self.total_pages = total_pages
                            self.current_page = 0
                            self.page_cache = {0: tracks}
                        
                        async def get_embed_for_page(self, page_num):
                            if page_num not in self.page_cache:
                                self.page_cache[page_num] = await get_tracks_for_page(page_num)
                            
                            if self.page_cache[page_num]:
                                return await create_embed_for_page(self.page_cache[page_num], page_num)
                            else:
                                return Embed(
                                    title="Error",
                                    description="Failed to load this page of tracks.",
                                    color=0xff0000
                                )
                        
                        async def update_current_page(self, interaction, new_page):
                            if 0 <= new_page < self.total_pages:
                                self.current_page = new_page
                                new_embed = await self.get_embed_for_page(new_page)
                                self.embeds[0] = new_embed
                                await interaction.message.edit(embed=new_embed)
                    
                    paginator = LastfmPaginator(
                        bot=self.bot,
                        destination=ctx,
                        initial_embed=initial_embed,
                        total_pages=min(total_pages, 100),
                        invoker=ctx.author.id
                    )
                    
                    await self.add_pagination_controls(paginator, multi_page=True)
                    
                    await paginator.start()
            
            except Exception as e:
                await ctx.warning(f"An error occurred")
async def setup(bot):
    await bot.add_cog(Music(bot))