import asyncio
import datetime
from typing import Any, Generator, List, Optional
import discord
from data.config import CONFIG
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Command, CommandOnCooldown, Group, HelpCommand
from discord.ui import View, Button
from discord import Embed, Message
from ..classes.exceptions import InvalidSubCommand
from .context import Context
import inspect


class OnCooldown(Exception):
    pass


async def shorten(text: str, limit: int) -> str:
    try:
        if len(text) >= limit:
            return text[: limit - 3] + "..."
        else:
            return text
    except Exception:
        return text


async def map_check(check):
    if "is_booster" in check.__qualname__:
        return "`Server Booster`"
    elif "trusted" in check.__qualname__:
        return "`Antinuke Admin`"
    elif "guild_owner" in check.__qualname__:
        return "`Server Owner`"
    elif "is_donator" in check.__qualname__:
        return "`Donator`"
    else:
        return None


async def humann_join(
    items: list,
    separator: Optional[str] = ", ",
    markdown: Optional[str] = "",
    replacements: Optional[dict] = None,
    start_content: Optional[str] = "",
    titled: Optional[bool] = False,
) -> str:
    if not items:
        return ""
    
    if len(items) > 1 and items[0].lower() == "send messages":
        items = items[1:]
        
    if replacements:
        items = [i.replace(key, value) for i in items for key, value in replacements.items()]
        
    return f'{start_content}{separator.join(f"{markdown}{item.title() if titled else item}{markdown}" for item in items)}'


def generate(ctx: Context, c: Command, example: str = "", usage=False) -> str:
    params = None
    try:
        if len(c.clean_params.keys()) == 1:
            if "_" in list(c.clean_params.keys())[0]:
                params = " ".join(
                    f"({p})" for p in list(c.clean_params.keys())[0].split("_")
                )
    except Exception:
        pass
    if not params:
        params = " ".join(f"({param})" for param in c.clean_params.keys())
    if usage is True:
        if example != "":
            ex = f"\nExample: {example}```"
        else:
            ex = "```"
        return f"\n```Syntax: {ctx.prefix}{c.qualified_name} {params} {ex}"
    if len(c.qualified_name.lower().split(" ")) > 2:
        m = f" for {c.qualified_name.lower().split(' ')[-1]}s"
    else:
        m = ""
    if "add" in c.qualified_name.lower() or "create" in c.qualified_name.lower():
        if c.brief is None:
            return f"create a new {c.qualified_name.lower().split(' ')[0]}{m}"
    elif "remove" in c.qualified_name.lower() or "delete" in c.qualified_name.lower():
        if c.brief is None:
            return f"delete a {c.qualified_name.lower().split(' ')[0]}{m}"
    elif "clear" in c.qualified_name.lower():
        if c.brief is None:
            return f"clear {c.qualified_name.lower().split(' ')[0]}{m}"
    else:
        if c.brief is None:
            if m == "":
                if c.root_parent is not None:
                    m = f" {c.root_parent.name.lower()}"
            if len(c.clean_params.keys()) == 0:
                n = "view "
            else:
                n = "change "
            return f"{n}the {c.name.lower()}{m}"


def chunks(array: List, chunk_size: int) -> Generator[List, None, None]:
    for i in range(0, len(array), chunk_size):
        yield array[i : i + chunk_size]


async def command_not_found(self, string: str) -> None:
    if string.lower() == "emojis":
        await self.context.send_help(self.context.bot.get_command("emoji list"))
        return
    raise discord.ext.commands.CommandError(
        f"**No command** named **{string}** exists"
    )


class CogConverter(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        cogs = [i for i in ctx.bot.cogs]
        for cog in cogs:
            if cog.lower() == argument.lower():
                return ctx.bot.cogs.get(cog)
        return None


class HelpPaginator(discord.ui.View):
    def __init__(self, embeds: List[discord.Embed], author_id: int):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.author_id = author_id
        self.current = 0
        self.page_counter = discord.ui.Button(
            label=f"Page 1/{len(embeds)}", 
            style=discord.ButtonStyle.gray,
            disabled=True
        )
        self.add_item(self.page_counter)

    @discord.ui.button(emoji="<:left:1367895503530098730>", style=discord.ButtonStyle.blurple)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("This menu is not for you!", ephemeral=True)
            
        self.current = max(0, self.current - 1)
        self.page_counter.label = f"Page {self.current + 1}/{len(self.embeds)}"
        await interaction.response.edit_message(embed=self.embeds[self.current], view=self)

    @discord.ui.button(emoji="<:right:1367895496437530755>", style=discord.ButtonStyle.blurple) 
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("This menu is not for you!", ephemeral=True)
            
        self.current = min(len(self.embeds) - 1, self.current + 1)
        self.page_counter.label = f"Page {self.current + 1}/{len(self.embeds)}"
        await interaction.response.edit_message(embed=self.embeds[self.current], view=self)

    @discord.ui.button(emoji="<:cancel:1367897395417059338>", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("This menu is not for you!", ephemeral=True)

        await interaction.message.delete()

    async def on_timeout(self):
        """Disable all buttons when the view times out"""
        for item in self.children:
            item.disabled = True
        try:
            message = self.message
            await message.edit(view=self)
        except:
            pass


class Help(HelpCommand):
    async def send_bot_help(self, mapping):
        total_commands = len(
            [
                c
                for c in self.context.bot.walk_commands()
                if c.cog_name
                and c.cog_name.lower()
                not in ["git", "jishaku", "errors"]
            ]
        )
        embed = discord.Embed(
            description=f"⚙️ {self.context.author.mention}: For help, visit our [website](https://heist.lol/commands) to view {total_commands} commands",
            color=CONFIG['colors']['default'],
        )
        return await self.context.send(embed=embed)
        
    async def send_cog_help(self, cog):
        return

    def subcommand_not_found(self, command, string):
        if isinstance(command, Group) and len(command.all_commands) > 0:
            raise InvalidSubCommand(
                f'**Command** "{command.qualified_name}" has **no subcommand named** `{string}`'
            )
        raise InvalidSubCommand(
            f'**Command** "{command.qualified_name}" **has** `no subcommands.`'
        )

    async def send_group_help(self, group):
        embed: Embed = Embed(
            color=CONFIG['colors']['default'], 
            timestamp=datetime.datetime.now()
        )
        ctx = self.context
        embeds = []
        commands_ = [c for c in group.walk_commands()]
        commands_.insert(0, group)

        for i, command in enumerate(commands_, start=1):
            try:
                await command.can_run(ctx)

                perms = getattr(command, 'perms', ["send_messages"])

                if hasattr(command, 'checks'):
                    for check in command.checks:
                        if hasattr(check, 'permissions'):
                            perms.extend(p.replace('_', ' ') for p in check.permissions.keys())
                        elif hasattr(check, 'predicate') and hasattr(check.predicate, 'permissions'):
                            perms.extend(p.replace('_', ' ') for p in check.predicate.permissions.keys())

                if command.cog_name and command.cog_name.lower() == "premium":
                    if isinstance(perms, list):
                        perms = perms.copy()
                        perms.append("Donator")
                    else:
                        perms = ["Donator"]

                embed = Embed(color=0x6E879C, timestamp=datetime.datetime.now())
                embed.title = f"{'Group Command: ' if isinstance(command, Group) else 'Command: '}{command.qualified_name}"

                description = command.description or command.help
                description = description if description else generate(ctx, command)
                embed.description = description
                
                embeds.append(embed)
                
            except Exception as e:
                continue

        if not embeds:
            return await ctx.send("No accessible commands in this group.")

        paginator = HelpPaginator(embeds, self.context.author.id)
        initial_message = await self.context.send(embed=embeds[0], view=paginator)
        paginator.message = initial_message
        return initial_message

    def get_example(self, command):
        if len(command.clean_params.keys()) == 0:
            return ""
        ex = f"{self.context.prefix}{command.qualified_name} "
        for key, value in command.clean_params.items():
            if "user" in repr(value).lower() or "member" in repr(value).lower():
                ex += "@babycosmin "
            elif "role" in repr(value).lower():
                ex += "@own"
            elif "image" in repr(value).lower() or "attachment" in repr(value).lower():
                ex += "[attachment] "
            elif "channel" in repr(value).lower():
                ex += "#msg"
            elif key.lower() == "reason":
                ex += "idk i felt like it"
            else:
                ex += f"<{key}> "
        return ex

    def get_usage(self, command):
        if len(command.clean_params.keys()) == 0:
            return ""
        usage = f"{self.context.prefix}{command.qualified_name} "
        for key, value in command.clean_params.items():
            usage += f"<{key}> "
        return usage

    async def command_not_found(self, string):
        if string.lower() == "emojis":
            command = self.context.bot.get_command("emoji list")
            if command:
                return await self.send_command_help(command)
        raise commands.CommandNotFound(f"No command named '{string}' was found.")

    async def send_error_message(self, error):
        embed = discord.Embed(
            title="Command Not Found",
            description=str(error),
            color=CONFIG['colors']['error']
        )
        await self.context.send(embed=embed)

    async def send_command_help(self, command):
        embed = Embed(
            color=CONFIG['colors']['default'], 
            timestamp=datetime.datetime.now()
        )
        try:
            if command.qualified_name == "help":
                embed.title = "Command: help"
                embed.description = "View extended help for commands"
                embed.add_field(name="Aliases", value="commands, h", inline=True)
                embed.add_field(name="Parameters", value="command", inline=True)
                embed.add_field(name="Information", value="n/a", inline=True)
                embed.add_field(
                    name="Usage",
                    value="```No syntax has been set for this command```",
                    inline=False,
                )
                embed.set_author(
                    name=self.context.author.display_name,
                    icon_url=self.context.author.display_avatar.url,
                )
                embed.set_footer(text="Page 1/1 (1 entry) ∙ Module: Information")
                return await self.context.send(embed=embed)
        except Exception:
            pass

        embed.set_author(
            name=self.context.author.display_name,
            icon_url=self.context.author.display_avatar.url,
        )

        ctx = self.context
        perms = set()
        perms.add("send messages")

        if hasattr(command, 'perms'):
            cmd_perms = command.perms
            if isinstance(cmd_perms, list):
                perms.update(p.replace('_', ' ') for p in cmd_perms)
            else:
                perms.add(str(cmd_perms).replace('_', ' '))

        if hasattr(command, 'checks'):
            for check in command.checks:
                if hasattr(check, 'permissions'):
                    perms.update(p.replace('_', ' ') for p in check.permissions.keys())
                elif hasattr(check, 'predicate') and hasattr(check.predicate, 'permissions'):
                    perms.update(p.replace('_', ' ') for p in check.predicate.permissions.keys())
                elif hasattr(check, '__closure__') and check.__closure__:
                    for cell in check.__closure__:
                        value = cell.cell_contents
                        if isinstance(value, dict):
                            for k in value.keys():
                                perms.add(k.replace('_', ' '))

        if command.cog_name and command.cog_name.lower() == "premium":
            perms.add("Donator")

        embed.title = f"{'Group Command: ' if isinstance(command, Group) else 'Command: '}{command.qualified_name}"
        description = command.description or command.help
        description = description if description else generate(ctx, command)
        embed.description = description

        aliases = ", ".join(command.aliases) if command.aliases else "none"
        embed.add_field(name="Aliases", value=aliases, inline=True)

        params = ", ".join(command.clean_params.keys()).replace("_", ", ")
        embed.add_field(name="Parameters", value=params if params else "none", inline=True)

        _checks = await asyncio.gather(*(map_check(c) for c in command.checks))
        checks = list(dict.fromkeys(filter(None, _checks)))

        warning_emoji = await self.context.bot.emojis.get('warning')
        permissions = sorted(list(perms))
        permissions_text = "".join(f"{warning_emoji} {perm.title()}\n" for perm in permissions)
        information_text = "".join(f"{warning_emoji} {c}\n" for c in checks)

        info_value = f"{permissions_text}{information_text}".strip()

        if info_value:
            embed.add_field(
                name="Information",
                value=info_value,
                inline=True,
            )

        example = command.example.replace(",", ctx.prefix) if hasattr(command, 'example') and command.example else self.get_example(command)
        embed.add_field(name="Usage", value=generate(ctx, command, example, True), inline=False)

        cog_name = command.extras.get("cog_name", command.cog_name)
        if cog_name:
            embed.set_footer(text=f"Module: {cog_name.replace('.py','')}")

        return await ctx.send(embed=embed)
