import inspect
from discord.ext import commands

class JishakuCommandString(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enforce_quotes()

    def enforce_quotes(self):
        for name, cmd in self.bot.commands.items():
            if not name.startswith("jsk"):
                continue
            original = cmd.callback

            async def wrapped(ctx, *args, **kwargs):
                sig = inspect.signature(original)
                for param in sig.parameters.values():
                    if param.name in kwargs:
                        arg = kwargs[param.name]
                        if isinstance(arg, str) and (not arg.startswith('"') or not arg.endswith('"')):
                            return await ctx.send("Wrap the command string in quotes.")
                await original(ctx, *args, **kwargs)

            cmd.callback = wrapped

async def setup(bot):
    await bot.add_cog(JishakuCommandString(bot))