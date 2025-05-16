import discord
import asyncio
import discord_ios
from system.Heist import Heist
from system.classes.tiktok import TikTok

bot = Heist()

async def main():
    try:
        await bot.run()
    except KeyboardInterrupt:
        await bot.github.close()
        await bot.tiktok.close()
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())