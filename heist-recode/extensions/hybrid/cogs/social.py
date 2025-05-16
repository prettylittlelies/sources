import discord
from discord import app_commands
from discord.ext import commands
from discord import Embed, File
from typing import Optional, List, Dict, Any
from data.config import CONFIG
import asyncio, re, io, aiohttp, datetime, functools
from system.classes.paginator import Paginator
from urllib.parse import urlparse
import json
from system.classes.permissions import Permissions
from typing import Optional, List, Union
from system.classes.logger import Logger
from bs4 import BeautifulSoup

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tiktok = self.bot.tiktok
        self.instagram = bot.socials.instagram
        self.session = aiohttp.ClientSession()
        self.media_cache = {}
        self.cache_size_limit = 50
        self.logger = Logger()
        self.config = CONFIG

    def cog_unload(self):
        asyncio.create_task(self.session.close())
        self.media_cache.clear()

    async def download_images_in_parallel(self, image_urls):
        """Download multiple images in parallel"""
        tasks = []
        for url in image_urls:
            if url in self.media_cache:
                tasks.append(asyncio.create_task(asyncio.sleep(0, result=self.media_cache[url])))
            else:
                tasks.append(asyncio.create_task(self.tiktok.download_media(url)))
        
        results = await asyncio.gather(*tasks)
        
        for i, url in enumerate(image_urls):
            if url not in self.media_cache and results[i]:
                if len(self.media_cache) >= self.cache_size_limit:
                    self.media_cache.pop(next(iter(self.media_cache)))
                self.media_cache[url] = results[i]
                
        return results

    def format_metric(self, value, use_millions=False):
        """Format numeric values to human-readable format (k, M)"""
        if use_millions and value >= 1000000:
            return f"{int(value/1000000)}M" if value % 1000000 == 0 else f"{value/1000000:.1f}M"
        elif value >= 1000:
            return f"{int(value/1000)}k" if value % 1000 == 0 else f"{value/1000:.1f}k"
        return str(value)

    def process_description(self, description: str) -> str:
        """Process TikTok description to format hashtags as links"""
        if not description:
            return ""
        return "> " + re.sub(r"#(\S+)", r"[#\1](<https://tiktok.com/tag/\1>)", description)

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
            ('sort', "🔄"),
            ('audio', "🔊")
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
            paginator.add_button("goto", emoji=emojis['sort'])
        
        paginator.add_button("delete", emoji=emojis['cancel'], style=discord.ButtonStyle.danger)
        paginator.add_button("page")
        
        return paginator

    async def prepare_tiktok_slideshow(self, ctx, video, tiktok_link, processed_desc, tiktokstats, avatar_file):
        """Prepare paginated slideshow for TikTok images"""
        all_images = video.images
        images_per_page = 9
        total_pages = (len(all_images) + images_per_page - 1) // images_per_page
        
        embeds = []
        files_list = []
        
        for page in range(total_pages):
            page_embed = Embed(
                description=processed_desc,
                color=CONFIG['embed_colors']['default']
            )
            
            page_embed.set_author(
                name=f"{video.author_nickname} (@{video.author_username})",
                url=tiktok_link,
                icon_url="attachment://avatar.png"
            )
            
            page_embed.set_footer(
                text=f"Page {page + 1}/{total_pages} - {tiktokstats}",
                icon_url="https://git.cursi.ng/tiktok_logo.png?2"
            )
            
            embeds.append(page_embed)
        
        if ctx.guild and ctx.guild.me.guild_permissions.attach_files:
            page_download_tasks = []
            for page in range(total_pages):
                start_idx = page * images_per_page
                end_idx = min(start_idx + images_per_page, len(all_images))
                current_page_images = all_images[start_idx:end_idx]
                page_download_tasks.append(self.download_images_in_parallel(current_page_images))
            
            all_page_downloads = await asyncio.gather(*page_download_tasks)
            
            for page, page_downloads in enumerate(all_page_downloads):
                page_files = [avatar_file]
                for i, image_data in enumerate(page_downloads):
                    if image_data:
                        file = File(image_data, filename=f"image{i + 1}.png")
                        page_files.append(file)
                files_list.append(page_files)
        else:
            for page in range(total_pages):
                start_idx = page * images_per_page
                end_idx = min(start_idx + images_per_page, len(all_images))
                current_page_images = all_images[start_idx:end_idx]
                
                for i, image_url in enumerate(current_page_images):
                    embeds[page].add_field(name=f"Image {i + 1}", value=f"[View Image]({image_url})", inline=False)
                
                files_list.append([avatar_file])
        
        return embeds, files_list, total_pages

    async def setup_audio_preview_button(self, paginator, audio_url):
        """Set up the audio preview button for TikTok content"""
        self.logger.debug(f"Audio preview requested for {audio_url}")
        async def audio_preview_callback(interaction):
            await interaction.response.defer(ephemeral=True)
            try:
                if audio_url in self.media_cache:
                    audio_content = self.media_cache[audio_url]
                else:
                    async with self.session.get(audio_url) as music_response:
                        if music_response.status == 200:
                            audio_content = await music_response.read()
                            if len(self.media_cache) >= self.cache_size_limit:
                                self.media_cache.pop(next(iter(self.media_cache)))
                            self.media_cache[audio_url] = audio_content
                        else:
                            await interaction.followup.send("Failed to download the audio.", ephemeral=True)
                            return

                audio_file = discord.File(io.BytesIO(audio_content), filename="audio.mp3")
                await interaction.followup.send(file=audio_file, ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"Error processing audio: {str(e)}", ephemeral=True)
                self.logger.error(f"Error processing audio: {str(e)}")
        
        paginator.add_custom_button(
            callback=audio_preview_callback,
            emoji=discord.PartialEmoji.from_str("<:audio:1345517095101923439>"),
            style=discord.ButtonStyle.secondary,
            custom_id="slideshowaudio"
        )
        
        return paginator

    async def upload_to_catbox(self, file_data: io.BytesIO) -> str | None:
        """Upload a file to catbox.moe"""
        try:
            data = aiohttp.FormData()
            data.add_field('reqtype', 'fileupload')
            data.add_field('fileToUpload', file_data, filename='video.mp4')
            async with self.session.post('https://catbox.moe/user/api.php', data=data) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    return None
        except Exception:
            return None

    @commands.hybrid_group(
        name="snapchat",
        description="Snapchat social commands",
        aliases=["snap"]
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def snapchat(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @snapchat.command(
        name="user",
        description="View Snapchat user info",
        aliases=["u", "profile"]
    )
    @app_commands.describe(username="The Snapchat username to lookup")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def scuser(self, ctx: commands.Context, username: str):
        if not username:
            error_emoji = await self.bot.emojis.get("warning", "❌")
            await ctx.send(
                embed=Embed(
                    description=f"{error_emoji} Please provide a Snapchat username",
                    color=CONFIG['embed_colors']['error']
                )
            )
            return

        async with ctx.typing():
            try:
                user_info = await self.get_snapchat_info(username)
                
                if not user_info:
                    error_emoji = await self.bot.emojis.get("warning", "❌")
                    await ctx.send(
                        embed=Embed(
                            description=f"{error_emoji} User does not exist",
                            color=CONFIG['embed_colors']['error']
                        )
                    )
                    return

                title = f"{user_info.get('displayName', username)} (@{user_info['username']})"
                if user_info.get('badge') == 1:
                    title += " <:scstar:1294423745997307979>"

                embed = Embed(
                    title=title,
                    url=f"https://www.snapchat.com/add/{username}",
                    color=CONFIG['embed_colors']['default']
                )

                if user_info['type'] == 'publicProfileInfo':
                    subscriber_count = user_info.get('subscribers', 0)
                    description = user_info.get('bio', '')
                    if user_info.get('website'):
                        website_url = user_info['website']
                        description += f"\n[Website]({website_url})"
                    embed.description = description
                    embed.add_field(
                        name="Subscribers", 
                        value=f"**`{subscriber_count:,}`**", 
                        inline=True
                    )
                    
                    if user_info.get('profile_picture_url'):
                        embed.set_thumbnail(url=user_info['profile_picture_url'])
                else:
                    embed.add_field(
                        name="Username", 
                        value=user_info['username'], 
                        inline=True
                    )
                    embed.add_field(
                        name="Display Name", 
                        value=user_info.get('displayName', 'N/A'), 
                        inline=True
                    )
                    if user_info.get('bitmoji_url'):
                        embed.set_image(url=user_info['bitmoji_url'])
                    if user_info.get('snapcode_url'):
                        embed.set_thumbnail(
                            url=user_info['snapcode_url'].replace("&type=SVG", "&type=PNG")
                        )

                embed.set_author(
                    name=ctx.author.name,
                    icon_url=ctx.author.display_avatar.url
                )
                embed.set_footer(
                    text="snapchat.com",
                    icon_url="https://git.cursi.ng/snapchat_logo.png"
                )

                await ctx.send(embed=embed)

            except Exception as e:
                error_emoji = await self.bot.emojis.get("warning", "❌")
                await ctx.send(
                    embed=Embed(
                        description=f"{error_emoji} Failed to fetch Snapchat profile: {str(e)}",
                        color=CONFIG['embed_colors']['error']
                    )
                )

    async def get_snapchat_info(self, username: str) -> dict:
        url = f"https://www.snapchat.com/add/{username}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        async with self.bot.session.get(url, headers=headers) as response:
            if response.status != 200:
                return None
            
            text = await response.text()
            
            def parse_html(html_content):
                soup = BeautifulSoup(html_content, 'html.parser')
                script_tag = soup.find('script', type='application/json')
                return script_tag.string if script_tag else None
            
            script_content = await asyncio.to_thread(parse_html, text)
            if not script_content:
                return None

            try:
                data = json.loads(script_content)
                user_profile = data['props']['pageProps']['userProfile']
                
                if user_profile['$case'] == 'userInfo':
                    user_info = user_profile.get('userInfo', {})
                    return {
                        'type': 'userInfo',
                        'username': user_info.get('username'),
                        'displayName': user_info.get('displayName'),
                        'snapcode_url': user_info.get('snapcodeImageUrl'),
                        'bitmoji_url': user_info.get('bitmoji3d', {}).get('avatarImage', {}).get('url')
                    }
                elif user_profile['$case'] == 'publicProfileInfo':
                    public_profile_info = user_profile.get('publicProfileInfo', {})
                    return {
                        'type': 'publicProfileInfo',
                        'username': public_profile_info.get('username'),
                        'displayName': public_profile_info.get('title'),
                        'snapcode_url': public_profile_info.get('snapcodeImageUrl'),
                        'profile_picture_url': public_profile_info.get('profilePictureUrl'),
                        'bio': public_profile_info.get('bio'),
                        'website': public_profile_info.get('websiteUrl'),
                        'subscribers': public_profile_info.get('subscriberCount'),
                        'badge': public_profile_info.get('badge', 0)
                    }
            except (KeyError, json.JSONDecodeError):
                return None

    @commands.hybrid_group(
        name="instagram",
        description="Instagram social commands",
        aliases=["insta", "ig"],
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def instagram(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @instagram.command(
        name="user",
        description="View Instagram user info",
        aliases=["u", "profile"]
    )
    @app_commands.describe(username="The Instagram username to lookup")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def iguser(self, ctx: commands.Context, username: str):
        if not username:
            error_emoji = await self.bot.emojis.get("warning", "❌")
            await ctx.send(
                embed=Embed(
                    description=f"{error_emoji} Please provide an Instagram username",
                    color=CONFIG['embed_colors']['error']
                )
            )
            return

        def format_number(number_str):
            try:
                number = float(number_str.replace('M', '').replace('K', ''))
                if 'M' in number_str:
                    return f"{number:.1f}m"
                elif 'K' in number_str:
                    return f"{number:.1f}k"
                return number_str
            except:
                return number_str

        async with ctx.typing():
            try:
                data = await self.instagram.get_profile(username)

                title = f"{data.username}"
                if data.verified:
                    title += " <:verified_light_blue:1362170749271408911>"

                embed = Embed(
                    title=title,
                    url=data.url,
                    description=data.bio if data.bio else None,
                    color=CONFIG['embed_colors']['default']
                )

                embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)

                if data.avatar_url:
                    embed.set_thumbnail(url=data.avatar_url)

                embed.add_field(name="Followers", value=f"**`{format_number(data.followers)}`**", inline=True)
                embed.add_field(name="Following", value=f"**`{format_number(data.following)}`**", inline=True)
                embed.add_field(name="Posts", value=f"**`{format_number(data.posts)}`**", inline=True)

                embed.set_footer(
                    text="instagram.com",
                    icon_url="https://git.cursi.ng/instagram_logo.png?e"
                )

                await ctx.send(embed=embed)

            except Exception as e:
                error_emoji = await self.bot.emojis.get("warning", "❌")
                await ctx.send(
                    embed=Embed(
                        description=f"{error_emoji} Failed to fetch Instagram profile: {str(e)}",
                        color=CONFIG['embed_colors']['error']
                    )
                )

    @commands.hybrid_group(
        name="tiktok",
        description="tiktok social commands",
        aliases=["tik", "tt"],
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def tiktokg(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @tiktokg.command(
        name="repost",
        description="Repost a TikTok post",
        aliases=["r"]
    )
    @app_commands.describe(url="The TikTok post URL to download")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def tiktok(self, ctx: commands.Context, url: str):
        if not url:
            error_emoji = await self.bot.emojis.get("warning", "❌")
            await ctx.send(
                embed=Embed(
                    description=f"{error_emoji} Please provide a TikTok URL",
                    color=CONFIG['embed_colors']['error']
                )
            )
            return

        parsed = urlparse(url.strip())
        hostname = parsed.netloc.lower()

        if not (hostname == 'tiktok.com' or hostname.endswith('.tiktok.com')):
            error_emoji = await self.bot.emojis.get("warning", "❌")
            await ctx.send(
                embed=Embed(
                    description=f"{error_emoji} Please provide a valid TikTok URL",
                    color=CONFIG['embed_colors']['error']
                )
            )
            return

        async with ctx.typing():
            try:
                data_task = asyncio.create_task(self.tiktok.get_video_data(url))
                data = await data_task
                avatar_buffer = await self.tiktok.download_media(data.author_pfp)
                avatar_file = File(avatar_buffer, filename="avatar.png")

                video_id = None
                if hasattr(data, "video_id"):
                    video_id = data.video_id
                else:
                    match = re.search(r'video/(\d+)', data.video_url)
                    if match:
                        video_id = match.group(1)
                    else:
                        match = re.search(r'video/(\d+)', url)
                        if match:
                            video_id = match.group(1)
                
                tiktok_link = f"https://www.tiktok.com/@{data.author_username}/video/{video_id}" if video_id else url
                processed_desc = self.process_description(data.title)

                likes = self.format_metric(data.likes)
                views = self.format_metric(data.play_count, use_millions=True)
                comments = self.format_metric(data.comments)
                shares = self.format_metric(data.shares)
                
                tiktokstats = f"❤️ {likes} • 👁️ {views} • 🗨️ {comments} • 🔄 {shares}"

                if data.images:
                    embeds, files_list, total_pages = await self.prepare_tiktok_slideshow(
                        ctx, data, tiktok_link, processed_desc, tiktokstats, avatar_file
                    )
                    
                    paginator = Paginator(
                        bot=self.bot,
                        embeds=embeds,
                        destination=ctx,
                        timeout=360,
                        invoker=ctx.author.id,
                        files=files_list[0]
                    )
                    
                    await self.add_pagination_controls(paginator, multi_page=total_pages > 1)
                    
                    if data.audio_url:
                        self.logger.debug(f"Audio URL: {data.audio_url}")
                        await self.setup_audio_preview_button(paginator, data.audio_url)
                    
                    original_edit_page = paginator.edit_page
                    
                    async def custom_edit_page(interaction):
                        page_num = paginator.page
                        
                        if 0 <= page_num < len(files_list):
                            current_embed = paginator.embeds[page_num]
                            page_files = files_list[page_num]
                            
                            await interaction.message.edit(embed=current_embed, attachments=page_files, view=paginator)
                        else:
                            await original_edit_page(interaction)
                    
                    paginator.edit_page = custom_edit_page
                    
                    await paginator.start()
                
                else:
                    embed = Embed(
                        description=processed_desc,
                        color=CONFIG['embed_colors']['default']
                    )
                    
                    embed.set_author(
                        name=f"{data.author_nickname} (@{data.author_username})",
                        url=tiktok_link,
                        icon_url="attachment://avatar.png"
                    )
                    
                    embed.set_footer(
                        text=tiktokstats,
                        icon_url="https://git.cursi.ng/tiktok_logo.png?2"
                    )
                    
                    video_result = await self.tiktok.download_video(data.video_url)
                    
                    if isinstance(video_result, str):
                        await ctx.send(
                            f"[Video Link]({video_result})\n"
                            f"-# We have uploaded this video thru [catbox.moe](https://catbox.moe) "
                            f"due to discord's file size limit."
                        )
                    else:
                        video_size = video_result.getbuffer().nbytes
                        if video_size <= 10 * 1024 * 1024:
                            files = [avatar_file, File(video_result, "video.mp4")]
                            await ctx.send(files=files, embed=embed)
                        elif video_size <= 50 * 1024 * 1024:
                            catbox_url = await self.upload_to_catbox(video_result)
                            if catbox_url:
                                message = f"-# Uploaded by **`{data.author_nickname}`** [**`(@{data.author_username})`**](<https://www.tiktok.com/@{data.author_username}>)\n"
                                if data.title:
                                    message += f"-# {processed_desc}\n"
                                message += f"-# {tiktokstats}\n\n-# [**TikTok**](<{tiktok_link}>) • [**Download**]({catbox_url})\n-# This video exceeds the limit of 10MB, hence it was uploaded to [catbox](<https://catbox.moe>)."
                                await ctx.send(message)
                            else:
                                await ctx.send(
                                    "Failed to upload to catbox, video is too large for Discord.",
                                    embed=embed
                                )
                        else:
                            await ctx.send(
                                "Video is too large to process.",
                                embed=embed
                            )
            
            except Exception as e:
                error_emoji = await self.bot.emojis.get("warning", "❌")
                await ctx.send(
                    embed=Embed(
                        description=f"{error_emoji} Failed to process TikTok content: {str(e)}",
                        color=CONFIG['embed_colors']['error']
                    )
                )

    @tiktokg.command(
        name="trending",
        description="Show trending TikTok videos",
        aliases=["fyp"]
    )
    @app_commands.describe(
        region="Region code (e.g., US, UK, JP)"
    )
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def trending(self, ctx: commands.Context, region: Optional[str] = "US"):
        async with ctx.typing():
            try:
                videos_task = asyncio.create_task(self.tiktok.get_trending_videos(region.upper(), 1))
                videos = await videos_task
                
                if not videos:
                    await ctx.send("No trending videos found for the specified region")
                    return

                for video in videos:
                    avatar_buffer = await self.tiktok.download_media(video.author_pfp)
                    avatar_file = File(avatar_buffer, filename="avatar.png")
                    video_id = getattr(video, 'video_id', None) or (video.video_url.split('/video/')[1].split('?')[0] if '/video/' in video.video_url else None)
                    tiktok_link = f"https://www.tiktok.com/@{video.author_username}/video/{video_id}" if video_id else video.video_url
                    processed_desc = self.process_description(video.title)

                    likes = self.format_metric(video.likes)
                    views = self.format_metric(video.play_count, use_millions=True)
                    comments = self.format_metric(video.comments)
                    shares = self.format_metric(video.shares)
                    tiktokstats = f"❤️ {likes} • 👁️ {views} • 🗨️ {comments} • 🔄 {shares}"

                    if getattr(video, 'images', None):
                        embeds, files_list, total_pages = await self.prepare_tiktok_slideshow(
                            ctx, video, tiktok_link, processed_desc, tiktokstats, avatar_file
                        )
                        
                        paginator = Paginator(
                            bot=self.bot,
                            embeds=embeds,
                            destination=ctx,
                            timeout=360,
                            invoker=ctx.author.id,
                            files=files_list[0]
                        )
                        
                        await self.add_pagination_controls(paginator, multi_page=total_pages > 1)
                        
                        if getattr(video, 'audio_url', None):
                            self.logger.debug(f"Audio URL: {video.audio_url}")
                            await self.setup_audio_preview_button(paginator, video.audio_url)
                            self.logger.debug(f"Audio preview button added for {video.audio_url}")
                        
                        await paginator.start()
                    else:
                        embed = Embed(
                            description=processed_desc,
                            color=CONFIG['embed_colors']['default']
                        )
                        
                        embed.set_author(
                            name=f"{video.author_nickname} (@{video.author_username})",
                            url=f"https://www.tiktok.com/@{video.author_username}/{video_id}",
                            icon_url="attachment://avatar.png"
                        )
                        embed.set_footer(
                            text=tiktokstats,
                            icon_url="https://git.cursi.ng/tiktok_logo.png?2"
                        )

                        video_result = await self.tiktok.download_video(video.video_url)
                        
                        if isinstance(video_result, str):
                            await ctx.send(
                                f"[Video Link]({video_result})\n"
                                f"-# We have uploaded this video thru [catbox.moe](https://catbox.moe) "
                                f"due to discord's file size limit."
                            )
                        else:
                            video_size = video_result.getbuffer().nbytes
                            if video_size <= 10 * 1024 * 1024:
                                files = [avatar_file, File(video_result, "video.mp4")]
                                await ctx.send(files=files, embed=embed)
                            elif video_size <= 50 * 1024 * 1024:
                                catbox_url = await self.upload_to_catbox(video_result)
                                if catbox_url:
                                    message = f"-# Uploaded by **`{video.author_nickname}`** [**`(@{video.author_username})`**](<https://www.tiktok.com/@{video.author_username}>)\n"
                                    if video.title:
                                        message += f"-# {processed_desc}\n"
                                    message += f"-# {tiktokstats}\n\n-# [**TikTok**](<{tiktok_link}>) • [**Download**]({catbox_url})\n-# This video exceeds the limit of 10MB, hence it was uploaded to [catbox](<https://catbox.moe>)."
                                    await ctx.send(message)
                                else:
                                    await ctx.send(
                                        "Failed to upload to catbox, video is too large for Discord.",
                                        embed=embed
                                    )
                            else:
                                await ctx.send(
                                    "Video is too large to process.",
                                    embed=embed
                                )

            except Exception as e:
                error_emoji = await self.bot.emojis.get("warning", "❌")
                await ctx.send(
                    embed=Embed(
                        description=f"{error_emoji} Failed to fetch trending videos: {str(e)}",
                        color=CONFIG['embed_colors']['error']
                    )
                )

    @commands.hybrid_command(
        name="roblox2discord",
        description="✨ Find a Discord user's linked Roblox account",
        aliases=["r2d"],
    )
    @app_commands.describe(username="The Roblox username to look up")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.check(Permissions.is_donor)
    @commands.check(Permissions.is_donor)
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def roblox2discord_lookup(self, ctx, username: str):
        description = ""
        thumbnail_url = 'https://t0.rbxcdn.com/91d977e12525a5ed262cd4dc1c4fd52b?format=png'

        async def fetch_roblox_id():
            async with self.session.post(
                'https://users.roproxy.com/v1/usernames/users',
                headers={'accept': 'application/json', 'Content-Type': 'application/json'},
                json={'usernames': [username], 'excludeBannedUsers': False}
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None

        try:
            roblox_data = await fetch_roblox_id()

            if roblox_data and roblox_data.get('data'):
                roblox_id = int(roblox_data['data'][0]['id'])
                roblox_name = roblox_data['data'][0]['name']

                cached_discord_id, cached_name, last_updated = await self.dtr_hit_redis(roblox_id)

                if not cached_discord_id:
                    row = await self.dtr_hit_db(roblox_id)
                    if row:
                        cached_discord_id = row['discord_id']
                        last_updated = row['last_updated']
                        await self.dtr_push_redis(cached_discord_id, roblox_id, roblox_name, last_updated)

                discord_av = None
                if cached_discord_id:
                    try:
                        discord_user = await self.bot.fetch_user(int(cached_discord_id))
                        description += f"Discord: [{discord_user}](discord://-/users/{cached_discord_id}) ({cached_discord_id})\n"
                        description += f"<:pointdrl:1318643571317801040> Updated: <t:{int(datetime.datetime.fromisoformat(last_updated).timestamp())}:R>\n"
                        discord_av = discord_user.display_avatar.url
                    except:
                        description += "Could not fetch Discord user (may no longer exist)\n"

                async with self.session.get(f'https://thumbnails.roproxy.com/v1/users/avatar-headshot?userIds={roblox_id}&size=420x420&format=Png&isCircular=false') as thumbnail_response:
                    if thumbnail_response.status == 200:
                        thumbnail_data = await thumbnail_response.json()
                        if thumbnail_data.get('data'):
                            thumbnail_url = thumbnail_data['data'][0].get('imageUrl')

                ropro_discord = None
                try:
                    async with self.session.get(f'https://api.ropro.io/getUserInfoTest.php?userid={roblox_id}') as ropro_response:
                        if ropro_response.status == 200:
                            ropro_data = await ropro_response.json()
                            ropro_discord = ropro_data.get('discord')
                except:
                    pass

                if ropro_discord:
                    description += f"RoPro: **{ropro_discord}**"

                if not description:
                    description = "No linked Discord found for this user."

                if roblox_id and roblox_name:
                    embed = discord.Embed(
                        color=CONFIG['embed_colors']['default']
                    )
                    embed.set_author(name=f"{roblox_name} ({roblox_id})", url=f"https://roblox.com/users/{roblox_id}/profile", icon_url=thumbnail_url)
                    embed.set_thumbnail(url=discord_av if discord_av else thumbnail_url)
                    embed.description = description
                    embed.set_footer(text=f"roblox.com", icon_url="https://git.cursi.ng/roblox_logo.png?v2")

                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Could not find a linked Discord for this Roblox user.")
            else:
                await ctx.send("Could not find a linked Discord for this Roblox user.")

        except Exception as e:
            print(f"Error in roblox2discord lookup: {e}")
            await ctx.send(f"An error occurred while searching for linked Discord.\n{e}")

    @commands.hybrid_command(
        name="discord2roblox",
        description="✨ Find a Discord user's linked Roblox account",
        aliases=["d2r"],
    )
    @app_commands.describe(user="The Discord user to look up (defaults to yourself)")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.check(Permissions.is_donor)
    @commands.check(Permissions.is_donor)
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def discord2roblox(self, ctx, user: Optional[discord.Member] = None):
        target_user = user or ctx.author
        discord_id = str(target_user.id)

        async def fetch_thumbnail(roblox_id):
            thumbnail_url = f"https://thumbnails.roproxy.com/v1/users/avatar-headshot?userIds={roblox_id}&size=420x420&format=Png&isCircular=false"
            async with self.session.get(thumbnail_url) as response:
                if response.status == 200:
                    thumbnail_data = await response.json()
                    if thumbnail_data.get('data'):
                        return thumbnail_data['data'][0].get('imageUrl')
                return 'https://t0.rbxcdn.com/91d977e12525a5ed262cd4dc1c4fd52b?format=png'

        try:
            roblox_id, roblox_name, last_updated = await self.dtr_hit_redis(discord_id)

            if not roblox_name:
                row = await self.dtr_hit_db(int(discord_id))
                if row:
                    roblox_id = row['roblox_id']
                    roblox_name = row['roblox_name']
                    last_updated = row.get('last_updated', 'Unknown')
                    await self.dtr_push_redis(discord_id, roblox_id, roblox_name, last_updated)
                else:
                    url = f"https://api.blox.link/v4/public/discord-to-roblox/{target_user.id}"
                    headers = {"Authorization": CONFIG['BLOXLINK_API_KEY']}

                    async with self.session.get(url, headers=headers) as response:
                        data = await response.json()
                        self.logger.debug(f"Response from Bloxlink: {data}")

                        if response.status == 200 and 'error' not in data:
                            roblox_id = data.get('robloxID')
                            roblox_data = data.get('resolved', {}).get('roblox', {})
                            roblox_name = roblox_data.get('name')
                            
                            if roblox_id and roblox_name:
                                now = datetime.datetime.now().isoformat()
                                await self.dtr_push_redis(discord_id, roblox_id, roblox_name, now)
                                last_updated = now
            
            if roblox_name and roblox_id:
                headshot_url = await fetch_thumbnail(roblox_id)
                
                embed = discord.Embed(
                    color=CONFIG['embed_colors']['default']
                )
                embed.set_author(
                    name=f"{roblox_name} ({roblox_id})",
                    url=f"https://roblox.com/users/{roblox_id}/profile",
                    icon_url=headshot_url
                )
                embed.set_thumbnail(url=headshot_url)
                embed.description = f"Username: **{roblox_name}**\n\n[view profile](https://roblox.com/users/{roblox_id}/profile)"
                    
                embed.set_footer(text=f"roblox.com", icon_url="https://git.cursi.ng/roblox_logo.png?v2")

                await ctx.send(embed=embed)
            else:
                await ctx.send("Could not find a linked Roblox account for this Discord user.")

        except Exception as e:
            print(f"Error in discord2roblox: {e}")
            await ctx.warning(f"Bloxlink could not resolve this user.")

    async def dtr_push_db(self, discord_id: str, roblox_id: int, roblox_name: str):
        await self.bot.db.execute(
            """
            INSERT INTO dtr_mappings (discord_id, roblox_id, roblox_name, last_updated)
            VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
            ON CONFLICT (discord_id, roblox_id) 
            DO UPDATE SET roblox_name = $3, last_updated = CURRENT_TIMESTAMP;
            """,
            discord_id, roblox_id, roblox_name
        )
        await self.dtr_push_redis(discord_id, roblox_id, roblox_name, datetime.datetime.now().isoformat())

    async def dtr_hit_db(self, identifier: Union[int, str]):
        if isinstance(identifier, int):
            row = await self.bot.db.fetchrow(
                "SELECT discord_id, roblox_name, last_updated FROM dtr_mappings WHERE roblox_id = $1",
                identifier
            )
        else:
            row = await self.bot.db.fetchrow(
                "SELECT roblox_id, roblox_name, last_updated FROM dtr_mappings WHERE discord_id = $1",
                identifier
            )
        
        if row:
            row = dict(row)
            if isinstance(identifier, int):
                row["discord_id"] = str(row["discord_id"])
            else:
                row["roblox_id"] = int(row["roblox_id"])
            row["last_updated"] = row["last_updated"].isoformat()
            return row
        return None

    async def dtr_push_redis(self, discord_id: str, roblox_id: int, roblox_name: str, last_updated: str):
        roblox_id = int(roblox_id)
        await self.bot.redis.redis.setex(
            f"dtr:{roblox_id}",
            86400,
            f"{discord_id}:{roblox_name}:{last_updated}"
        )
        await self.bot.redis.redis.setex(
            f"r2d:{discord_id}",
            86400,
            f"{roblox_id}:{roblox_name}:{last_updated}"
        )

    async def dtr_hit_redis(self, identifier: Union[int, str]):
        if isinstance(identifier, int):
            key = f"dtr:{identifier}"
        else:
            key = f"r2d:{identifier}"
        
        cached_data = await self.bot.redis.redis.get(key)
        if cached_data:
            parts = cached_data.split(":")
            if isinstance(identifier, int):
                color=await self.bot.color_manager.resolve(ctx.author.id)
            else:
                return parts[0], parts[1], ":".join(parts[2:])
        return None, None, None

async def setup(bot):
    await bot.add_cog(Social(bot))