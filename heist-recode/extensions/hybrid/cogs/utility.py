import discord
import time
import base64
import random
import aiohttp
import asyncio
import io
import os
import re
from io import BytesIO
from discord import app_commands, File, Embed, Interaction
from discord.ext import commands
from discord.ext.commands import Cog, hybrid_command
from data.config import CONFIG
from system.classes.permissions import Permissions
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageSequence, ImageEnhance, ImageChops
from typing import Literal
from system.classes.permissions import Permissions

def ListedFonts():
    fonts = []
    for file in os.listdir('fonts/'):
        if (file.endswith('.ttf') or (file.endswith('.otf')) and 'futura' not in file.lower()):
            fonts.append(file)
    return fonts

async def GBytes(image: Image, gif: bool = False) -> File:
    bytes_io = BytesIO()
    await asyncio.to_thread(image.save, bytes_io, format="PNG", optimize=False)
    bytes_io.seek(0)
    return File(bytes_io, filename="heist.gif" if gif else "heist.png")

async def Imgenhance(image: Image) -> Image:
    enhancer = ImageEnhance.Sharpness(image)
    image = await asyncio.to_thread(enhancer.enhance, 2.0)
    enhancer = ImageEnhance.Contrast(image)
    image = await asyncio.to_thread(enhancer.enhance, 1.5)
    enhancer = ImageEnhance.Brightness(image)
    image = await asyncio.to_thread(enhancer.enhance, 1.2)
    return image

async def useravatar(url: str) -> Image:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            image_data = await response.read()
            image_file = BytesIO(image_data)
            avatar = await asyncio.to_thread(Image.open, image_file)
            if avatar.format == 'GIF':
                avatar = await asyncio.to_thread(next, ImageSequence.Iterator(avatar))
            return avatar

async def processed(avatar: Image, color: int, transparency: int, flip: bool, new: bool) -> Image:
    if avatar.mode != 'RGBA':
        im = await asyncio.to_thread(avatar.convert, 'RGBA')
    else:
        im = avatar
    im = await Imgenhance(im)
    width, height = im.size
    gradient = await asyncio.to_thread(Image.new, 'L', (width, 1), color=0xFF)
    for x in range(width):
        await asyncio.to_thread(gradient.putpixel, (x, 0), transparency - x)
    alpha = await asyncio.to_thread(gradient.resize, im.size)
    black_im = await asyncio.to_thread(Image.new, 'RGBA', (width, height), color=color)
    await asyncio.to_thread(black_im.putalpha, alpha.rotate((180 if not flip else 0) if not new else 90))
    gradient_im = await asyncio.to_thread(Image.alpha_composite, im, black_im)
    return gradient_im

async def wrappedtextemoji(text, width):
    lines = []
    current_line = ""
    custom_emoji_pattern = re.compile(r'<:\w+:\d+>')
    other_emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002700-\U000027BF\U0001F1E0-\U0001F1FF]')
    combined_emoji_pattern = re.compile(r'(:\w+:)+')
    word_pattern = re.compile(r'\S+')

    i = 0
    word_count = 0
    other_count = 0

    while i < len(text):
        custom_match = await asyncio.to_thread(custom_emoji_pattern.match, text, i)
        other_match = await asyncio.to_thread(other_emoji_pattern.match, text, i)
        combined_match = await asyncio.to_thread(combined_emoji_pattern.match, text, i)
        word_match = await asyncio.to_thread(word_pattern.match, text, i)
        
        if combined_match:
            emoji_length = 10
            if len(current_line) + emoji_length > width or other_count >= 2:
                lines.append(current_line)
                current_line = combined_match.group() + "\u200B"
                word_count = 0
                other_count = 1
            else:
                current_line += combined_match.group() + "\u200B"
                other_count += 1
            i += len(combined_match.group())
        elif custom_match:
            emoji_length = 1
            if len(current_line) + emoji_length > width or other_count >= 2:
                lines.append(current_line)
                current_line = custom_match.group() + "\u200B"
                word_count = 0
                other_count = 1
            else:
                current_line += custom_match.group() + "\u200B"
                other_count += 1
            i += len(custom_match.group())
        elif other_match:
            emoji_length = 5
            if len(current_line) + emoji_length > width or other_count >= 2:
                lines.append(current_line)
                current_line = other_match.group() + " "
                word_count = 0
                other_count = 1
            else:
                current_line += other_match.group() + " "
                other_count += 1
            i += len(other_match.group())
        elif word_match:
            word_length = len(word_match.group())
            if len(current_line) + word_length > width or word_count >= 10:
                lines.append(current_line)
                current_line = word_match.group() + " "
                word_count = 1
                other_count = 0
            else:
                if current_line:
                    current_line += " "
                current_line += word_match.group()
                word_count += 1
            i += word_length
        else:
            if len(current_line) + 1 > width:
                lines.append(current_line)
                current_line = text[i]
                word_count = 0
                other_count = 0
            else:
                current_line += text[i]
            i += 1

    if current_line:
        lines.append(current_line)
    return "\n".join(lines)

async def quoter(message: discord.Message, font: str, color: Literal['white', 'black'] = None, contrast: bool = None, flip: bool = None, gif: bool = None, new: bool = None, blur: bool = None, brightness: bool = None, pixelate: bool = None, solarize: bool = None) -> Image:
    transparency = (280 if color == 'black' else 255) if not new else 315
    color, fill = (0xffffff, Paint.Color((0, 0, 0, 255))) if color == 'white' else (0, Paint.Color((255, 255, 255, 255)))
    avatar = await useravatar(message.author.display_avatar.url)
    gradient_im = await processed(avatar, color, transparency, flip, new)
    if contrast:    
        gradient_im = await asyncio.to_thread(gradient_im.convert, 'L')
    if blur:
        gradient_im = await asyncio.to_thread(gradient_im.filter, ImageFilter.GaussianBlur(10))
    if brightness:
        enhancer = ImageEnhance.Brightness(gradient_im)
        gradient_im = await asyncio.to_thread(enhancer.enhance, 1.5)
    if pixelate:
        width, height = gradient_im.size
        gradient_im = await asyncio.to_thread(gradient_im.resize, (width // 10, height // 10), resample=Image.NEAREST)
        gradient_im = await asyncio.to_thread(gradient_im.resize, (width, height), resample=Image.NEAREST)
    if solarize:
        gradient_im = await asyncio.to_thread(ImageOps.solarize, gradient_im)
    
    blank = await asyncio.to_thread(Image.new, "RGB", (857 if not new else 592, 450 if not new else 743), color=color)
    await asyncio.to_thread(blank.paste, await asyncio.to_thread(gradient_im.resize, (450, 450) if not new else (592, 743)), (0, 0) if not flip else (round(857 / 2 - 20), 0))
    await asyncio.to_thread(gradient_im.close)
    width, height = blank.size
    
    await asyncio.to_thread(FontDB.SetDefaultEmojiOptions, EmojiOptions(parse_discord_emojis=True))
    await asyncio.to_thread(FontDB.LoadFromPath, 'custom-font', f'fonts/{font}')
    cv_font = await asyncio.to_thread(FontDB.Query, 'custom-font')
    cv = await asyncio.to_thread(Canvas, 857 if not new else 592, 450 if not new else 743, Color(0, 0, 0, 0))
    
    x = (width / 2 + (210 if not new else 25)) if not flip else (width / 2 - 210 - 15)
    y = height / 2
    wrapped_text = await wrappedtextemoji(message.clean_content, width=20)
    wrap_width = 400
    font_size = 50 if not new else 65
    
    while font_size > 1:
        text_width, text_height = await asyncio.to_thread(text_size_multiline,
            lines=await asyncio.to_thread(text_wrap,
                text=wrapped_text,
                width=wrap_width,
                size=font_size,
                wrap_style=WrapStyle.Character,
                draw_emojis=True,
                font=cv_font
            ),
            size=font_size,
            font=cv_font,
            draw_emojis=True
        )
        if text_width <= 400 and text_height <= (335 if not new else 175):
            break
        font_size -= 2
    
    if len(wrapped_text) <= 10:
        font_size = min(60, font_size)
    elif len(wrapped_text) <= 20:
        font_size = min(50, font_size)
    
    await asyncio.to_thread(draw_text_wrapped, canvas=cv, x=x, y=y if not new else y + 200, ax=0.5, ay=0.5, align=TextAlign.Center, width=wrap_width, wrap_style=WrapStyle.Character, line_spacing=0.925, text=wrapped_text, font=cv_font, size=font_size, fill=fill, draw_emojis=True)
    display_name_width = 400
    await asyncio.to_thread(draw_text_wrapped, canvas=cv, x=x, y=y + ((20 + text_height / 2) if not new else 330), ax=0.5, ay=0.5, align=TextAlign.Center, width=display_name_width, text=f"- {message.author.display_name}" if not new else message.author.display_name, font=cv_font, size=32 if not new else 38, fill=fill)
    await asyncio.to_thread(draw_text_wrapped, canvas=cv, x=x, y=y + ((45 + text_height / 2) if not new else 355), ax=0.5, ay=0.5, align=TextAlign.Center, width=100, text=f"@{message.author.name}", font=cv_font, size=22 if not new else 26, fill=Paint.Color((89, 89, 89, 255)))
    await asyncio.to_thread(draw_text_wrapped, canvas=cv, x=(815 if not new else 545) if not flip else 70, y=435 if not new else y + 355, ax=0.5, ay=0.5, align=TextAlign.Center, width=100, text="heist.lol", font=cv_font, size=24, fill=Paint.Color((89, 89, 89, 255)))
    
    if new:
        await asyncio.to_thread(draw_text_wrapped, canvas=cv, x=x, y=y + 135, ax=0.5, ay=0.5, align=TextAlign.Center, width=250, text="" "", font=cv_font, size=225, fill=fill)
        await asyncio.to_thread(draw_text_wrapped, canvas=cv, x=x, y=y + 290, ax=0.5, ay=0.5, align=TextAlign.Center, width=100, text="___________", font=cv_font, size=33, fill=fill)

    text = await asyncio.to_thread(cv.to_image)
    await asyncio.to_thread(blank.paste, text, (0, 0), mask=text)
    return blank

class Buttons(discord.ui.View):
    EMOJIS = {
        "color": "<:color:1316896978931683408>",
        "contrast": "<:contrast:1316896854956314755>",
        "flip": "<:flip:1316896847096315954>",
        "gif": "<:gif:1325499192097116201>",
        "new": "<:new:1316896960917016607>",
        "blur": "<:blur:1316897646480461885>",
        "brightness": "<:brightness:1316897642114187324>",
        "pixelate": "<:pixel:1316897638620336148>",
        "solarize": "<:solarize:1316896942382387231>",
        "remove": "<:trash:1316896912372400201>"
    }

    def __init__(self, ctx, author):
        super().__init__(timeout=240)
        self.interaction = ctx
        self.author = author
        self.lock = asyncio.Lock()
        self.font = 'M PLUS Rounded 1c (mplus).ttf'
        self.is_gif = False
        self.color_active = False
        self.contrast_active = False
        self.flip_active = False
        self.new_active = False
        self.blur_active = False
        self.brightness_active = False
        self.pixelate_active = False
        self.solarize_active = False
        self._update_font_select()

    def _update_font_select(self):
        self.select_font.options = [
            discord.SelectOption(
                label=font,
                value=font,
                emoji="<:blarrow:1341204214273146902>" if font == self.font else None,
                default=font == self.font
            )
            for font in ListedFonts()
        ]

    async def authorCheck(self, interaction):
        if self.author != interaction.user:
            await interaction.response.send_message(f"Only {self.author.mention} can use this button.", ephemeral=True)
            return False
        return True

    async def UpdateImage(self, interaction):
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    'avatar_url': str(self.message.author.display_avatar.url),
                    'content': self.message.clean_content,
                    'display_name': self.message.author.display_name,
                    'username': self.message.author.name,
                    'font': self.font,
                    'color': 'white' if self.color_active else 'black',
                    'contrast': self.contrast_active,
                    'flip': self.flip_active,
                    'new': self.new_active,
                    'blur': self.blur_active,
                    'brightness': self.brightness_active,
                    'pixelate': self.pixelate_active,
                    'solarize': self.solarize_active,
                    'gif': self.is_gif
                }
                async with session.post('http://localhost:8080/quote', json=data) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        filename = 'quote.gif' if self.is_gif else 'quote.png'
                        file = discord.File(io.BytesIO(image_data), filename=filename)
                        if interaction.response.is_done():
                            await interaction.edit_original_response(attachments=[file], view=self)
                        else:
                            await interaction.response.edit_message(attachments=[file], view=self)
                    else:
                        await interaction.followup.send("Failed to generate quote", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}", ephemeral=True)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        try:
            await self.interaction.edit_original_response(view=self)
        except:
            pass

    @discord.ui.select(placeholder="Select a font...", options=[])
    async def select_font(self, interaction, select):
        if not await self.authorCheck(interaction):
            return
        self.font = select.values[0]
        self._update_font_select()
        await self.UpdateImage(interaction)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji=EMOJIS["color"])
    async def color(self, interaction, button):
        if not await self.authorCheck(interaction):
            return
        self.color_active = not self.color_active
        button.style = discord.ButtonStyle.blurple if self.color_active else discord.ButtonStyle.grey
        await self.UpdateImage(interaction)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji=EMOJIS["contrast"])
    async def contrast(self, interaction, button):
        if not await self.authorCheck(interaction):
            return
        self.contrast_active = not self.contrast_active
        button.style = discord.ButtonStyle.blurple if self.contrast_active else discord.ButtonStyle.grey
        await self.UpdateImage(interaction)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji=EMOJIS["flip"])
    async def flip(self, interaction, button):
        if not await self.authorCheck(interaction):
            return
        self.flip_active = not self.flip_active
        button.style = discord.ButtonStyle.blurple if self.flip_active else discord.ButtonStyle.grey
        await self.UpdateImage(interaction)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji=EMOJIS["gif"])
    async def gif(self, interaction, button):
        if not await self.authorCheck(interaction):
            return
        self.is_gif = not self.is_gif
        button.style = discord.ButtonStyle.blurple if self.is_gif else discord.ButtonStyle.grey
        await self.UpdateImage(interaction)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji=EMOJIS["new"])
    async def new(self, interaction, button):
        if not await self.authorCheck(interaction):
            return
        self.new_active = not self.new_active
        button.style = discord.ButtonStyle.blurple if self.new_active else discord.ButtonStyle.grey
        await self.UpdateImage(interaction)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji=EMOJIS["blur"])
    async def blur(self, interaction, button):
        if not await self.authorCheck(interaction):
            return
        self.blur_active = not self.blur_active
        button.style = discord.ButtonStyle.blurple if self.blur_active else discord.ButtonStyle.grey
        await self.UpdateImage(interaction)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji=EMOJIS["brightness"])
    async def brightness(self, interaction, button):
        if not await self.authorCheck(interaction):
            return
        self.brightness_active = not self.brightness_active
        button.style = discord.ButtonStyle.blurple if self.brightness_active else discord.ButtonStyle.grey
        await self.UpdateImage(interaction)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji=EMOJIS["pixelate"])
    async def pixelate(self, interaction, button):
        if not await self.authorCheck(interaction):
            return
        self.pixelate_active = not self.pixelate_active
        button.style = discord.ButtonStyle.blurple if self.pixelate_active else discord.ButtonStyle.grey
        await self.UpdateImage(interaction)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji=EMOJIS["solarize"])
    async def solarize(self, interaction, button):
        if not await self.authorCheck(interaction):
            return
        self.solarize_active = not self.solarize_active
        button.style = discord.ButtonStyle.blurple if self.solarize_active else discord.ButtonStyle.grey
        await self.UpdateImage(interaction)

    @discord.ui.button(emoji=EMOJIS["remove"], style=discord.ButtonStyle.grey)
    async def remove_quote(self, interaction, button):
        if not await self.authorCheck(interaction):
            return
        async with self.lock:
            await interaction.response.defer()
            await interaction.delete_original_response()

class Utility(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.ctx_quote = app_commands.ContextMenu(
            name='Quote Message',
            callback=self.quotemessage_context,
        )
        self.bot.tree.add_command(self.ctx_quote)

    async def cog_unload(self):
        if self.session and not self.session.closed:
            await self.session.close()
        self.bot.tree.remove_command(self.ctx_quote.name, type=self.ctx_quote.type)

    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def quotemessage_context(self, interaction: Interaction, message: discord.Message):
        await self._process_quote(interaction, message)

    @commands.command(name="quotemessage", aliases=["qm", "quote"])
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def quote_command(self, ctx, message: discord.Message = None):
        if not message and hasattr(ctx, 'message') and ctx.message.reference:
            message = ctx.message.reference.resolved
        if not message:
            await ctx.send("Please reply to a message to quote it.")
            return
        await self._process_quote(ctx, message)

    async def _process_quote(self, ctx, message):
        try:
            if not message.content:
                error_msg = "You cannot quote this message (no text content)."
                if isinstance(ctx, discord.Interaction):
                    await ctx.response.send_message(error_msg, ephemeral=True)
                else:
                    await ctx.send(error_msg)
                return

            if isinstance(ctx, discord.Interaction):
                await ctx.response.defer()
            else:
                async with ctx.typing():
                    pass

            view = Buttons(ctx, author=ctx.user if isinstance(ctx, discord.Interaction) else ctx.author)
            view.message = message

            async with aiohttp.ClientSession() as session:
                data = {
                    'avatar_url': str(message.author.display_avatar.url),
                    'content': message.clean_content,
                    'display_name': message.author.display_name,
                    'username': message.author.name,
                    'font': view.font
                }
                async with session.post('http://localhost:8080/quote', json=data) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        file = discord.File(io.BytesIO(image_data), filename='quote.png')
                        if isinstance(ctx, discord.Interaction):
                            await ctx.followup.send(file=file, view=view)
                        else:
                            await ctx.send(file=file, view=view)
                    else:
                        error_msg = "Failed to generate quote"
                        if isinstance(ctx, discord.Interaction):
                            await ctx.followup.send(error_msg, ephemeral=True)
                        else:
                            await ctx.send(error_msg)
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            if isinstance(ctx, discord.Interaction):
                await ctx.followup.send(error_msg, ephemeral=True)
            else:
                await ctx.send(error_msg)

    @hybrid_command(
        name="tts",
        description="Convert text to audio",
        aliases=["texttospeech"]
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True) 
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def tospeech(self, ctx, *, text: str):
        if not text:
            return await ctx.send("No text provided to convert to speech.")
        
        invalid_chars = {'.', ',', '/', '\\'} 
        if set(text) <= invalid_chars:
            return await ctx.send("No audio could be generated. Invalid character.")

        if len(text) > 300:
            return await ctx.send("Text too long. Maximum 300 characters allowed.")

        start_time = time.time()
        headers = {'Content-Type': 'application/json'}
        selected_voice = 'en_us_001'
        json_data = {'text': text, 'voice': selected_voice}

        async with self.session.post(
            'https://tiktok-tts.weilnet.workers.dev/api/generation', 
            headers=headers, 
            json=json_data
        ) as response:
            data = await response.json()

            if 'data' not in data or data['data'] is None:
                return await ctx.send("API did not return anything. Please try again later.")

            audio = base64.b64decode(data['data'])
            audio_buffer = BytesIO(audio)
            audio_buffer.seek(0)
            rnum = random.randint(100, 999)
            filename = f"tts_{rnum}.mp3"

            end_time = time.time()
            duration = end_time - start_time

            embed = Embed(
                description=f"🔊 Audio generated in `{duration:.2f}s`.", 
                color=await self.bot.color_manager.resolve(ctx.author.id)
            )

            file = File(audio_buffer, filename)

            if ctx.guild and ctx.guild.me.guild_permissions.embed_links:
                await ctx.send(f"Prompt: {text}", embed=embed, file=file)
            else:
                await ctx.send(f"Prompt: {text}", file=file, embed=embed,)

    @hybrid_command(
        name="blur",
        description="Blur an image",
        aliases=["blurimage"]
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True) 
    @app_commands.describe(image="The image to blur", togif="Make the image a gif?")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def blur(self, ctx, image: discord.Attachment = None, togif: bool = False):
        """Blur an image"""
        if not image:
            if ctx.message.reference and ctx.message.reference.resolved:
                ref_msg = ctx.message.reference.resolved
                if ref_msg.attachments:
                    image = ref_msg.attachments[0]
                elif hasattr(ref_msg, 'embeds') and ref_msg.embeds and ref_msg.embeds[0].image:
                    img_url = ref_msg.embeds[0].image.url
                    async with self.session.get(img_url) as resp:
                        if resp.status == 200:
                            image_data = await resp.read()
                            image = discord.Attachment(
                                data=io.BytesIO(image_data),
                                filename="image.png",
                                size=len(image_data),
                                url=img_url,
                                proxy_url=img_url,
                                height=0,
                                width=0,
                                content_type="image/png",
                                description=""
                            )
            
            if not image:
                return await ctx.send("Please provide an image to blur.")

        if not image.content_type or not image.content_type.startswith('image/'):
            return await ctx.send("The attachment must be an image.")

        async with ctx.typing():
            try:
                img_data = await image.read()
                img_bytes = io.BytesIO(img_data)
                
                if togif or image.filename.lower().endswith('.gif'):
                    frames = []
                    img = Image.open(img_bytes)
                    
                    try:
                        for frame in ImageSequence.Iterator(img):
                            frame_copy = frame.copy()
                            blurred_frame = frame_copy.filter(ImageFilter.GaussianBlur(radius=5))
                            frames.append(blurred_frame)
                    except Exception as e:
                        return await ctx.send(f"Error processing GIF frames: {str(e)}")
                    
                    output = io.BytesIO()
                    frames[0].save(
                        output, 
                        format='GIF', 
                        save_all=True, 
                        append_images=frames[1:], 
                        duration=img.info.get('duration', 100), 
                        loop=0
                    )
                    output.seek(0)
                    filename = "heist.gif"
                else:
                    img = Image.open(img_bytes)
                    blurred_img = img.filter(ImageFilter.GaussianBlur(radius=5))
                    
                    output = io.BytesIO()
                    blurred_img.save(output, format='PNG')
                    output.seek(0)
                    filename = "heist.png"
                
                file = discord.File(output, filename=filename)
                await ctx.send(file=file)
            except Exception as e:
                await ctx.warning(f"An error occurred: {str(e)}")

    @hybrid_command(
        name="speechbubble",
        description="Add a speech bubble to an image",
        aliases=["bubble"]
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True) 
    @app_commands.describe(image="The image to add a speech bubble to", togif="Make the image a gif?")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def speechbubble(self, ctx, image: discord.Attachment = None, togif: bool = False):
        try:
            if not image:
                if ctx.message.reference and ctx.message.reference.resolved:
                    ref_msg = ctx.message.reference.resolved
                    if ref_msg.attachments:
                        image = ref_msg.attachments[0]
                    elif hasattr(ref_msg, 'embeds') and ref_msg.embeds and ref_msg.embeds[0].image:
                        img_url = ref_msg.embeds[0].image.url
                        async with self.session.get(img_url) as resp:
                            if resp.status == 200:
                                image_data = await resp.read()
                                image = discord.Attachment(
                                    data=io.BytesIO(image_data),
                                    filename="image.png",
                                    size=len(image_data),
                                    url=img_url,
                                    proxy_url=img_url,
                                    height=0,
                                    width=0,
                                    content_type="image/png",
                                    description=""
                                )
                
                if not image:
                    return await ctx.send("Please provide an image to add a speech bubble to.")

            if not image.content_type or not image.content_type.startswith('image/'):
                return await ctx.send("The attachment must be an image.")

            async with ctx.typing():
                async with self.session.get(image.url) as resp:
                    if resp.status != 200:
                        return await ctx.send(f"Failed to download image. Status code: {resp.status}")
                    
                    image_data = io.BytesIO()
                    async for chunk in resp.content.iter_chunked(8192):
                        image_data.write(chunk)
                    image_data.seek(0)

                img = await asyncio.to_thread(Image.open, image_data)
                original_format = await asyncio.to_thread(lambda: img.format)
                is_gif = original_format == 'GIF'

                if is_gif:
                    frames = await asyncio.to_thread(lambda: [frame.copy().convert('RGBA') for frame in ImageSequence.Iterator(img)])
                    durations = await asyncio.to_thread(lambda: [frame.info.get('duration', 100) for frame in ImageSequence.Iterator(img)])
                else:
                    frames = [await asyncio.to_thread(img.convert, "RGBA")]

                speech_bubble_path = os.path.join("data", "assets", "speech_bubble.png")
                if not await asyncio.to_thread(os.path.exists, speech_bubble_path):
                    return await ctx.send("Speech bubble asset not found.")

                speech_bubble = await asyncio.to_thread(Image.open, speech_bubble_path)
                speech_bubble = await asyncio.to_thread(speech_bubble.convert, "RGBA")

                processed_frames = []
                for frame in frames:
                    resized_bubble = await asyncio.to_thread(lambda: speech_bubble.resize(frame.size, Image.Resampling.LANCZOS))
                    split_channels = await asyncio.to_thread(resized_bubble.split)
                    bubble_data = split_channels[3]

                    result = await asyncio.to_thread(Image.new, "RGBA", frame.size, (0, 0, 0, 0))
                    await asyncio.to_thread(lambda: result.paste(frame, (0, 0)))
                    await asyncio.to_thread(lambda: result.putalpha(ImageChops.subtract(result.split()[3], bubble_data)))
                    processed_frames.append(result)

                output = io.BytesIO()
                if is_gif or (togif and len(processed_frames) > 1):
                    await asyncio.to_thread(
                        lambda: processed_frames[0].save(
                            output,
                            format='GIF',
                            save_all=True,
                            append_images=processed_frames[1:],
                            duration=durations if is_gif else 100,
                            loop=0
                        )
                    )
                    file_extension = "gif"
                else:
                    save_format = 'PNG' if original_format == 'JPEG' else original_format
                    await asyncio.to_thread(processed_frames[0].save, output, format=save_format)
                    file_extension = "gif" if togif else save_format.lower()

                output.seek(0)
                await ctx.send(file=discord.File(output, filename=f'heist.{file_extension}'))

        except Exception as e:
            await ctx.warning(f"An error occurred: {str(e)}")

    @hybrid_command(
        name="caption",
        description="Add a caption to an image",
        aliases=["addcaption"]
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True) 
    @app_commands.describe(
        image="Image to add a caption to", 
        caption="The caption to add to the image", 
        togif="Make the image a gif?"
    )
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def caption(self, ctx, image: discord.Attachment = None, caption: str = None, togif: bool = False):
        """Add a caption to an image"""
        if not image:
            if ctx.message.reference and ctx.message.reference.resolved:
                ref_msg = ctx.message.reference.resolved
                if ref_msg.attachments:
                    image = ref_msg.attachments[0]
                    if not caption and ref_msg.content:
                        caption = ref_msg.content
                elif hasattr(ref_msg, 'embeds') and ref_msg.embeds and ref_msg.embeds[0].image:
                    img_url = ref_msg.embeds[0].image.url
                    async with self.session.get(img_url) as resp:
                        if resp.status == 200:
                            image_data = await resp.read()
                            image = discord.Attachment(
                                data=io.BytesIO(image_data),
                                filename="image.png",
                                size=len(image_data),
                                url=img_url,
                                proxy_url=img_url,
                                height=0,
                                width=0,
                                content_type="image/png",
                                description=""
                            )
                    if not caption and ref_msg.content:
                        caption = ref_msg.content
            
            if not image:
                return await ctx.send("Please provide an image to add a caption to.")

        if not caption:
            return await ctx.send("Please provide a caption for the image.")

        if not image.content_type or not image.content_type.startswith('image/'):
            return await ctx.send("The attachment must be an image.")

        async with ctx.typing():
            try:
                img_data = await image.read()
                img_bytes = io.BytesIO(img_data)
                
                try:
                    font_path = "fonts/Arial.ttf"
                    font_size = 30
                    font = ImageFont.truetype(font_path, font_size)
                except Exception:
                    font = ImageFont.load_default()
                
                if togif or image.filename.lower().endswith('.gif'):
                    frames = []
                    img = Image.open(img_bytes)
                    
                    dummy_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
                    text_width, text_height = dummy_draw.textsize(caption, font=font)
                    text_width = max(text_width + 20, img.width)
                    caption_height = text_height + 20
                    
                    for frame in ImageSequence.Iterator(img):
                        frame_copy = frame.copy().convert("RGBA")
                        
                        new_height = frame_copy.height + caption_height
                        new_frame = Image.new("RGBA", (max(text_width, frame_copy.width), new_height), (255, 255, 255, 255))
                        draw = ImageDraw.Draw(new_frame)
                        text_x = (new_frame.width - text_width) // 2 + 10
                        draw.text((text_x, 10), caption, fill=(0, 0, 0, 255), font=font)
                        frame_x = (new_frame.width - frame_copy.width) // 2
                        new_frame.paste(frame_copy, (frame_x, caption_height), frame_copy)
                        
                        frames.append(new_frame)
                    
                    output = io.BytesIO()
                    frames[0].save(
                        output, 
                        format='GIF', 
                        save_all=True, 
                        append_images=frames[1:], 
                        duration=img.info.get('duration', 100), 
                        loop=0
                    )
                    output.seek(0)
                    filename = "heist.gif"
                else:
                    img = Image.open(img_bytes).convert("RGBA")
                    
                    dummy_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
                    text_width, text_height = dummy_draw.textsize(caption, font=font)
                    text_width = max(text_width + 20, img.width)
                    caption_height = text_height + 20
                    
                    new_height = img.height + caption_height
                    new_img = Image.new("RGBA", (max(text_width, img.width), new_height), (255, 255, 255, 255))
                    draw = ImageDraw.Draw(new_img)
                    text_x = (new_img.width - text_width) // 2 + 10
                    draw.text((text_x, 10), caption, fill=(0, 0, 0, 255), font=font)
                    img_x = (new_img.width - img.width) // 2
                    new_img.paste(img, (img_x, caption_height), img)
                    
                    output = io.BytesIO()
                    new_img.save(output, format='PNG')
                    output.seek(0)
                    filename = "heist.png"
                
                file = discord.File(output, filename=filename)
                await ctx.send(file=file)
            except Exception as e:
                await ctx.warning(f"An error occurred: {str(e)}")

    @hybrid_command(
        name="imagetogif",
        description="Convert an image to a GIF",
        aliases=["img2gif", "togif"]
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True) 
    @app_commands.describe(image="The image to convert to a GIF")
    @app_commands.check(Permissions.is_blacklisted)
    @commands.check(Permissions.is_blacklisted)
    async def imagetogif(self, ctx, image: discord.Attachment = None):
        if not image:
            if ctx.message.reference and ctx.message.reference.resolved:
                ref_msg = ctx.message.reference.resolved
                if ref_msg.attachments:
                    image = ref_msg.attachments[0]
                elif hasattr(ref_msg, 'embeds') and ref_msg.embeds and ref_msg.embeds[0].image:
                    img_url = ref_msg.embeds[0].image.url
                    async with self.session.get(img_url) as resp:
                        if resp.status == 200:
                            image_data = await resp.read()
                            image = discord.Attachment(
                                data=io.BytesIO(image_data),
                                filename="image.png",
                                size=len(image_data),
                                url=img_url,
                                proxy_url=img_url,
                                height=0,
                                width=0,
                                content_type="image/png",
                                description=""
                            )
            
            if not image:
                return await ctx.send("Please provide an image to convert to GIF.")

        if not image.content_type or not image.content_type.startswith('image/'):
            return await ctx.send("The attachment must be an image.")

        if image.filename.lower().endswith('.gif'):
            return await ctx.send("The image is already a GIF.")

        try:
            gif_filename = image.filename.rsplit('.', 1)[0] + '.gif'
            file = discord.File(await image.read(), filename=gif_filename)
            await ctx.send(file=file)
        except Exception as e:
            await ctx.warning(f"An error occurred: {str(e)}")

async def setup(bot):
    await bot.add_cog(Utility(bot))