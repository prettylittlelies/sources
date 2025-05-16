import discord
import os
import asyncio
from discord import ui, app_commands
from discord.ext.commands import (Cog, command, is_owner, group, hybrid_command)
from data.config import CONFIG
from system.classes.db import Database
from system.classes.paginator import Paginator

class Admin(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
    
    async def cog_load(self):
        """Initialize database connection when cog loads"""
        await self.db.initialize()
    
    async def cog_unload(self):
        """Clean up database connection when cog unloads"""
        if self.db.pool:
            self.db.pool.close()
            await self.db.pool.wait_closed()
    
    async def cog_check(self, ctx):
        return ctx.author.id in CONFIG['owners']

    @group(name='admin')
    @is_owner()
    async def admin(self, ctx):
        """Administrative commands group"""

#test
    @admin.command(name='emojis')
    async def update_emojis(self, ctx, action: str = 'update'):
        """Emoji manager for the bot. (admin)"""
        if action.lower() != 'update':
            return await ctx.send('Invalid action. Use: ,add-emojis update')
        
        emoji_path = './emojis'
        if not os.path.exists(emoji_path):
            return await ctx.send('❌ Emojis directory not found!')
        
        status_msg = await ctx.send('🔄 Processing emojis...')
        
        try:
            existing_emojis = await self.bot.fetch_application_emojis()
            existing_emoji_names = [emoji.name for emoji in existing_emojis]
        except discord.HTTPException as e:
            return await status_msg.edit(content=f'❌ Failed to fetch existing emojis: {e}')
        
        async with self.db.pool.acquire() as conn:
            added = 0
            skipped = 0
            failed = 0
            
            for filename in os.listdir(emoji_path):
                if filename.endswith(('.png', '.gif', '.jpg', '.jpeg', '.webp', '.svg')):
                    name = os.path.splitext(filename)[0].lower()
                    
                    if name in existing_emoji_names:
                        skipped += 1
                        continue
                    
                    try:
                        with open(os.path.join(emoji_path, filename), 'rb') as f:
                            emoji_data = f.read()
                            
                        uploaded_emoji = await self.bot.create_application_emoji(
                            name=name,
                            image=emoji_data
                        )
                        
                        await conn.execute(
                            "INSERT INTO emojis (name, dname) VALUES ($1, $2)",
                            name, f"<:{uploaded_emoji.name}:{uploaded_emoji.id}>"
                        )
                        added += 1
                        await asyncio.sleep(1.5)
                        
                    except discord.HTTPException as e:
                        failed += 1
                        self.bot.logger.error(f"Failed to upload emoji {name}: {e}")
                        continue
        
        result = f"✅ Process complete!\nAdded: {added}\nSkipped: {skipped}"
        if failed > 0:
            result += f"\nFailed: {failed}"
            
        await status_msg.edit(content=result)

    @command(name='restart')
    async def restart_bot(self, ctx):
        """Restarts the bot using PM2. (admin)"""
        try:
            msg = await ctx.send("🔄 Restarting bot...")
            os.system("pm2 restart heistv2")
            await msg.edit(content="✅ Restart command sent successfully!")
        except Exception as e:
            await ctx.send(f"❌ Failed to restart: {str(e)}")
        
    @admin.command(name='pages')
    async def test_pages(self, ctx):
        """Test command showing paginator functionality. (admin)"""
        
        embeds = []
        for i in range(1, 6):
            embed = discord.Embed(
                title=f"Test Page {i}",
                description=f"This is a test page #{i}\n\nThis demonstrates the paginator functionality.",
                color=CONFIG['embed_colors']['default']
            )
            embed.add_field(name="Page Number", value=f"{i}/5", inline=False)       
            embed.set_footer(text=f"Requested by {ctx.author}")
            embeds.append(embed)

        paginator = Paginator(
            bot=self.bot,
            embeds=embeds,
            destination=ctx.channel,
            invoker=ctx.author.id,
            timeout=100
        )

        left_emoji = await self.bot.emojis.get('left') if callable(getattr(self.bot.emojis.get('left'), '__await__', None)) else self.bot.emojis.get('left')
        right_emoji = await self.bot.emojis.get('right') if callable(getattr(self.bot.emojis.get('right'), '__await__', None)) else self.bot.emojis.get('right')
        delete_emoji = await self.bot.emojis.get('cancel') if callable(getattr(self.bot.emojis.get('cancel'), '__await__', None)) else self.bot.emojis.get('cancel')
            
        paginator.add_button("back", emoji=left_emoji)
        paginator.add_button("next", emoji=right_emoji)
        paginator.add_button("delete", emoji=delete_emoji, style=discord.ButtonStyle.danger)

        await paginator.start()


async def setup(bot):
    await bot.add_cog(Admin(bot))