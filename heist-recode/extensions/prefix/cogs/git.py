import subprocess
from discord.ext.commands import (Cog, group, is_owner)
from system.patches import Context

class Git(Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @group(
        name="git",
        description="commands to update bot code",
        aliases=["repo", "github"],
    )
    @is_owner()
    async def github(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
    
    @github.command(
        name="pull",
        description="pull latest commits",
        example=",git pull",
    )
    @is_owner()
    async def pull(self, ctx: Context):
        try:
            output = subprocess.check_output(["git", "pull", "origin", "main"])
            await ctx.send(f"output:\n```{output.decode('utf-8')}```")
        except subprocess.CalledProcessError as e:
            await ctx.send(f"Error: {e.output.decode('utf-8')}")

async def setup(bot):
    await bot.add_cog(Git(bot))