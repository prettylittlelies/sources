import asyncio
import aiohttp
from aiohttp import web
import io
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageSequence
from imagetext_py import *
import os
import re

routes = web.RouteTableDef()

def ListedFonts():
    fonts = []
    for file in os.listdir('fonts/'):
        if (file.endswith('.ttf') or (file.endswith('.otf')) and 'futura' not in file.lower()):
            fonts.append(file)
    return fonts

async def GBytes(image, gif=False):
    bytes_io = io.BytesIO()
    await asyncio.to_thread(image.save, bytes_io, format="GIF" if gif else "PNG", optimize=False)
    bytes_io.seek(0)
    return bytes_io

async def Imgenhance(image):
    enhancer = ImageEnhance.Sharpness(image)
    image = await asyncio.to_thread(enhancer.enhance, 2.0)
    enhancer = ImageEnhance.Contrast(image)
    image = await asyncio.to_thread(enhancer.enhance, 1.5)
    enhancer = ImageEnhance.Brightness(image)
    image = await asyncio.to_thread(enhancer.enhance, 1.2)
    return image

async def useravatar(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            image_data = await response.read()
            image_file = io.BytesIO(image_data)
            avatar = await asyncio.to_thread(Image.open, image_file)
            if avatar.format == 'GIF':
                avatar = await asyncio.to_thread(next, ImageSequence.Iterator(avatar))
            return avatar

async def processed(avatar, color, transparency, flip, new):
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

@routes.post('/quote')
async def quote(request):
    data = await request.json()
    avatar_url = data['avatar_url']
    content = data['content']
    display_name = data['display_name']
    username = data['username']
    font = data.get('font', 'M PLUS Rounded 1c (mplus).ttf')
    color = data.get('color', 'black')
    contrast = data.get('contrast', False)
    flip = data.get('flip', False)
    new = data.get('new', False)
    blur = data.get('blur', False)
    brightness = data.get('brightness', False)
    pixelate = data.get('pixelate', False)
    solarize = data.get('solarize', False)

    transparency = (280 if color == 'black' else 255) if not new else 315
    color_val, fill = (0xffffff, Paint.Color((0, 0, 0, 255))) if color == 'white' else (0, Paint.Color((255, 255, 255, 255)))
    avatar = await useravatar(avatar_url)
    gradient_im = await processed(avatar, color_val, transparency, flip, new)
    
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
    
    blank = await asyncio.to_thread(Image.new, "RGB", (857 if not new else 592, 450 if not new else 743), color=color_val)
    await asyncio.to_thread(blank.paste, await asyncio.to_thread(gradient_im.resize, (450, 450) if not new else (592, 743)), (0, 0) if not flip else (round(857 / 2 - 20), 0))
    await asyncio.to_thread(gradient_im.close)
    width, height = blank.size
    
    await asyncio.to_thread(FontDB.SetDefaultEmojiOptions, EmojiOptions(parse_discord_emojis=True))
    await asyncio.to_thread(FontDB.LoadFromPath, 'custom-font', f'fonts/{font}')
    cv_font = await asyncio.to_thread(FontDB.Query, 'custom-font')
    cv = await asyncio.to_thread(Canvas, 857 if not new else 592, 450 if not new else 743, Color(0, 0, 0, 0))
    
    x = (width / 2 + (210 if not new else 25)) if not flip else (width / 2 - 210 - 15)
    y = height / 2
    wrapped_text = await wrappedtextemoji(content, width=20)
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
    await asyncio.to_thread(draw_text_wrapped, canvas=cv, x=x, y=y + ((20 + text_height / 2) if not new else 330), ax=0.5, ay=0.5, align=TextAlign.Center, width=display_name_width, text=f"- {display_name}" if not new else display_name, font=cv_font, size=32 if not new else 38, fill=fill)
    await asyncio.to_thread(draw_text_wrapped, canvas=cv, x=x, y=y + ((45 + text_height / 2) if not new else 355), ax=0.5, ay=0.5, align=TextAlign.Center, width=100, text=f"@{username}", font=cv_font, size=22 if not new else 26, fill=Paint.Color((89, 89, 89, 255)))
    await asyncio.to_thread(draw_text_wrapped, canvas=cv, x=(815 if not new else 545) if not flip else 70, y=435 if not new else y + 355, ax=0.5, ay=0.5, align=TextAlign.Center, width=100, text="heist.lol", font=cv_font, size=24, fill=Paint.Color((89, 89, 89, 255)))
    
    if new:
        await asyncio.to_thread(draw_text_wrapped, canvas=cv, x=x, y=y + 135, ax=0.5, ay=0.5, align=TextAlign.Center, width=250, text="" "", font=cv_font, size=225, fill=fill)
        await asyncio.to_thread(draw_text_wrapped, canvas=cv, x=x, y=y + 290, ax=0.5, ay=0.5, align=TextAlign.Center, width=100, text="___________", font=cv_font, size=33, fill=fill)

    text = await asyncio.to_thread(cv.to_image)
    await asyncio.to_thread(blank.paste, text, (0, 0), mask=text)
    
    image_bytes = await GBytes(blank, gif=data.get('gif', False))
    return web.Response(body=image_bytes.getvalue(), content_type='image/gif' if data.get('gif', False) else 'image/png')

async def start_server():
    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    print("Quote server started on http://localhost:8080")
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(start_server())