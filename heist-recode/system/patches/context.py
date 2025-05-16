from __future__ import annotations

import contextlib
from copy import copy
from typing import Any, Coroutine, Dict, List, Optional, Union

import discord
from data.config import CONFIG
from discord import AllowedMentions, Embed, File, Member, Message, User
from discord.ext.commands import (Command, CommandError, Group, UserInputError)
from discord.ext.commands import Context as DefaultContext
from discord.ui import View
from discord.utils import cached_property
from loguru import logger

TUPLE = tuple()
BLACKLIST = ("url", "icon_url", "type", "inline", "image", "thumbnail", "name")


async def alter_context(
    ctx: Context, *, author: Optional[Union[Member, User]] = None, **kwargs: Any
):
    message = copy(ctx.message)
    message._update(**kwargs)
    if author:
        message.author = author
    return await ctx.bot.get_context(message)


class ParameterParser:
    def __init__(self: "ParameterParser", ctx: "Context") -> None:
        self.context = ctx

    def get(self: "ParameterParser", param: str, **kwargs: Dict[str, Any]) -> Any:
        self.context.message.content = self.context.message.content.replace(" —", " --")

        parameters = [param] + list(kwargs.get("aliases", []))

        sliced = self.context.message.content.split()

        for parameter in parameters:
            if kwargs.get("require_value", True) is False:
                if f"-{parameter}" not in sliced and f"--{parameter}" not in sliced:
                    return kwargs.get("default", None)
                return True

            try:
                index = sliced.index(f"--{parameter}")
            except ValueError:
                logger.info(f"{parameter} raised value error")
                continue

            if kwargs.get("no_value", False) is True:
                return True

            result = []
            for word in sliced[index + 1 :]:
                if word.startswith("-"):
                    break
                result.append(word)

            if not (result := " ".join(result).replace("\\n", "\n").strip()):
                return kwargs.get("default", None)

            if choices := kwargs.get("choices"):
                choice = tuple(
                    choice for choice in choices if choice.lower() == result.lower()
                )
                if not choice:
                    raise CommandError(f"Invalid choice for parameter `{parameter}`.")
                result = choice[0]

            if converter := kwargs.get("converter"):
                if hasattr(converter, "convert"):
                    try:
                        result = self.context.bot.loop.create_task(
                            converter().convert(self.context, result)
                        )
                    except Exception as e:
                        logger.info(f"{parameter} failed to convert due to {e}")
                else:
                    try:
                        result = converter(result)
                    except Exception:
                        raise CommandError(f"Invalid value for parameter `{param}`.")

            if isinstance(result, int):
                if result < kwargs.get("minimum", 1):
                    raise CommandError(
                        f"The **minimum input** for parameter `{param}` is `{kwargs.get('minimum', 1)}`"
                    )
                if result > kwargs.get("maximum", 100):
                    raise CommandError(
                        f"The **maximum input** for parameter `{param}` is `{kwargs.get('maximum', 100)}`"
                    )

            return result

        return kwargs.get("default", None)


class Context(DefaultContext):
    def __init__(self, *args, **kwargs):
        self.aliased: Optional[bool] = False
        self.response = None
        self.lastfm = None
        super().__init__(*args, **kwargs)

    def style(self, embed: Embed, color: Optional[int] = None) -> Embed:
        if not embed.color or embed.color.value == self.bot.color:
            embed.color = color or self.bot.color
        return embed

    @property
    def __parameter_parser(self):
        return ParameterParser(self)

    @cached_property
    def parameters(self) -> Dict[str, Any]:
        return {
            name: self.__parameter_parser.get(name, **config)
            for name, config in self.command.parameters.items()
        }

    async def fill_lastfm(self, coroutine: Coroutine):
        self.lastfm = await coroutine

    async def confirmation(
        self,
        message: str,
        yes,
        no=None,
        view_author: Optional[Union[discord.Member, discord.User]] = None,
    ):
        async def default_no(interaction: discord.Interaction):
            embed = interaction.message.embeds[0]
            embed.description = "Aborting this action!"
            return await interaction.response.edit_message(embed=embed, view=None)

        if not no:
            no = default_no

        view = Confirmation(view_author.id if view_author else self.author.id, yes, no)
        view.message = await self.normal(message, view=view)

    async def display_prefix(
        self, only_one: Optional[bool] = True
    ) -> Union[str, tuple]:
        user_prefix = await self.bot.db.fetchval(
            """SELECT prefix FROM user_config WHERE user_id = %s""", (self.author.id,)
        )
        server_prefix = await self.bot.db.fetchval(
            """SELECT prefix FROM config WHERE guild_id = %s""", (self.guild.id,)
        )
        if not server_prefix:
            server_prefix = ","
        if not only_one:
            return (server_prefix, user_prefix)
        if user_prefix:
            if self.message.content.strip().startswith(user_prefix):
                return user_prefix
        return server_prefix

    async def send_help(self, option: Optional[Union[Command, Group]] = None):
        try:
            from .help import Help

            if option is None:
                if command := self.command:
                    if command.name != "help":
                        option = command
            h = Help()
            h.context = self
            if not option:
                return await h.send_bot_help(None)
            elif isinstance(option, Group):
                option = (
                    self.bot.get_command(option) if isinstance(option, str) else option
                )
                return await h.send_group_help(option)
            else:
                option = (
                    self.bot.get_command(option) if isinstance(option, str) else option
                )
                return await h.send_command_help(option)
        except Exception as exception:
            return await self.bot.errors.handle_exceptions(self, exception)

    async def get_reskin(self) -> Optional[tuple]:
        """Fetch reskin data for the user from the database."""
        result = await self.bot.db.fetchrow(
            "SELECT username, avatar_url, color FROM reskin WHERE user_id = %s",
            (self.author.id,),
        )
        if not result:
            return None
        return result["username"], result["avatar_url"], result["color"]

    async def get_invocation_embed(self):
        """Fetch invocation embed code for the command from the database."""
        try:
            embed_code = await self.bot.db.fetchval(
                """SELECT code FROM invocation WHERE guild_id = %s AND command = %s""",
                (self.guild.id, self.command.qualified_name.lower()),
            )
            return embed_code
        except Exception:
            return None

    async def confirm(self, message: str, **kwargs: Any):
        view = ConfirmView(self)
        message = await self.fail(message, view=view, **kwargs)

        await view.wait()
        with contextlib.suppress(discord.HTTPException):
            await message.delete()

        if view.value is False:
            raise UserInputError("Prompt was denied.")
        return view.value

    async def success(self, text: str, *args: Any, **kwargs: Any) -> Message:
        emoji = await self.bot.emojis.get('success', "<:success:1367925770395320380>")
        color = CONFIG['embed_colors']['success']
        embed = Embed(color=color, description=f"{emoji} {self.author.mention}: {text}")
        if footer := kwargs.pop("footer", None):
            if isinstance(footer, tuple):
                embed.set_footer(text=footer[0], icon_url=footer[1])
            else:
                embed.set_footer(text=footer)
        if author := kwargs.pop("author", None):
            if isinstance(author, tuple):
                embed.set_author(name=author[0], icon_url=author[1])
            else:
                embed.set_author(name=author)
        if delete_after := kwargs.get("delete_after"):
            delete_after = delete_after
        else:
            delete_after = None
        if kwargs.get("return_embed", False) is True:
            return embed
        return await self.send(
            embed=embed,
            delete_after=delete_after,
            view=kwargs.pop("view", None),
            **kwargs,
        )

    async def fail(self, text: str, *args: Any, **kwargs: Any) -> Message:
        emoji = self.bot.emojis.get('warning')
        color = self.bot.config["colors"]["fail"]
        embed = Embed(color=color, description=f"{emoji} {self.author.mention}: {text}")
        if footer := kwargs.pop("footer", None):
            if isinstance(footer, tuple):
                embed.set_footer(text=footer[0], icon_url=footer[1])
            else:
                embed.set_footer(text=footer)
        if author := kwargs.pop("author", None):
            if isinstance(author, tuple):
                embed.set_author(name=author[0], icon_url=author[1])
            else:
                embed.set_author(name=author)
        if delete_after := kwargs.get("delete_after"):
            delete_after = delete_after
        else:
            delete_after = None
        if kwargs.get("return_embed", False) is True:
            return embed
        return await self.send(
            embed=embed,
            delete_after=delete_after,
            view=kwargs.pop("view", None),
            **kwargs,
        )

    async def normal(self, text: str, *args: Any, **kwargs: Any) -> Message:
        color = self.bot.config["colors"].get("bleed", 0x2B2D31)
        embed = Embed(
            color=color,
            description=f"{kwargs.pop('emoji', '')} {self.author.mention}: {text}",
        )

    async def reply(self: "Context", *args: Any, **kwargs: Any) -> Message:
        if kwargs.pop("mention", True) is False:
            kwargs["allowed_mentions"] = AllowedMentions(replied_user=False)
        return await super().reply(*args, **kwargs)

    async def translate_embed(self, embed: discord.Embed, target: str):
        data = embed.to_dict()

        for key, value in data.items():
            if key in BLACKLIST:
                continue
            if isinstance(value, (list, set)):
                for val in value:
                    if isinstance(val, dict):
                        for k, v in val.items():
                            if isinstance(v, str):
                                data[key][value.index(val)][k] = (
                                    await self.bot.services.translation.translate(
                                        v,
                                        target_language=target,
                                        return_translation=True,
                                    )
                                )
            elif isinstance(value, dict):
                for k, v in value.items():
                    if k in BLACKLIST:
                        continue
                    data[key][k] = await self.bot.services.translation.translate(
                        v, target_language=target, return_translation=True
                    )
            elif isinstance(value, str):
                data[key] = await self.bot.services.translation.translate(
                    value, target_language=target, return_translation=True
                )
        return discord.Embed.from_dict(data)

    async def send(self: "Context", *args: Any, **kwargs: Any) -> Message:
        language = await self.bot.db.fetchval(
            """SELECT language FROM config WHERE guild_id = $1""", self.guild.id
        )
        embeds: List[Embed] = kwargs.get("embeds", [])
        if embed := kwargs.get("embed"):
            embeds.append(embed)
        if language:
            for embed in embeds:
                embeds[embeds.index(embed)] = await self.translate_embed(
                    embeds[0], language
                )

        content = kwargs.get("content", args[0] if len(args) > 0 else None)
        if content:
            if language:
                args = []
                kwargs["content"] = await self.bot.services.translation.translate(
                    content, target_language=language, return_translation=True
                )

        if self.interaction:
            for embed in embeds:
                self.style(embed, self.bot.color)

            try:
                kwargs.pop("delete_after", None)
                await self.interaction.response.send_message(*args, **kwargs)
                return await self.interaction.original_response()
            except Exception:
                kwargs.pop("delete_after", None)
                return await self.interaction.followup.send(*args, **kwargs)

        if patch := kwargs.pop("patch", None):
            kwargs.pop("reference", None)

            if args:
                kwargs["content"] = args[0]

            return await patch.edit(**kwargs)
        else:
            reskin = await self.get_reskin()
            color = reskin.color if reskin else None

            for embed in embeds:
                self.style(embed, color)

            if not reskin:
                return await super().send(*args, **kwargs)
            else:
                try:
                    webhook = next(
                        (
                            w
                            for w in await self.channel.webhooks()
                            if w.user.id == self.bot.user.id
                        ),
                    )
                except StopIteration:
                    webhook = await self.channel.create_webhook(
                        name=f"{self.bot.user.name} - reskin"
                    )

                kwargs["username"] = reskin.username
                kwargs["avatar_url"] = reskin.avatar_url
                kwargs["wait"] = True
                kwargs.pop("delete_after", None)
                return await webhook.send(*args, **kwargs)

    async def alternative_paginate(
        self,
        embeds: list,
        message: Optional[discord.Message] = None,
        invoker_lock: Optional[bool] = True,
    ):
        from ..classes.paginator import Paginator

        for i in embeds:
            if not isinstance(i, discord.Embed):
                break
            if not i.color:
                i.color = self.bot.color
        if invoker_lock is True:
            paginator = Paginator(self.bot, embeds, self, invoker=self.author.id)
        else:
            paginator = Paginator(self.bot, embeds, self)
        if len(embeds) > 1:
            paginator.add_button(
                "prev",
                emoji="<:left:1367925762954498129>",
                style=discord.ButtonStyle.blurple,
            )
            paginator.add_button(
                "next",
                emoji="<:right:1367925719270948896>",
                style=discord.ButtonStyle.blurple,
            )
            paginator.add_button(
                "goto",
                emoji=":file_folder:",
                style=discord.ButtonStyle.grey,
            )
            paginator.add_button(
                "delete",
                emoji="<:cancel:1367925747313803346>",
                style=discord.ButtonStyle.red,
            )
        elif len(embeds) == 1:
            paginator.add_button(
                "delete",
                emoji="<:cancel:1367925747313803346>",
                style=discord.ButtonStyle.red,
            )
        else:
            raise discord.ext.commands.errors.CommandError(
                "No Embeds Supplied to Paginator"
            )
        if message:
            await message.edit(view=paginator, embed=embeds[0])
            paginator.page = 0
            return
        return await paginator.start()

    async def paginate(
        self,
        embed: Union[discord.Embed, list],
        rows: Optional[list] = None,
        numbered: Optional[bool] = False,
        per_page: int = 10,
        type: str = "entry",
        plural_type: str = "entries",
    ):
        from system.classes.builtins import chunk_list, plural

        embeds = []
        if isinstance(embed, list):
            return await self.alternative_paginate(embed)
        if rows:
            if isinstance(rows[0], discord.Embed):
                embeds.extend(rows)
                return await self.alternative_paginate(embeds)
            else:
                if numbered and not rows[0].startswith("`1`"):
                    rows = [f"`{i}` {row}" for i, row in enumerate(rows, start=1)]
                if len(rows) > per_page:
                    chunks = chunk_list(rows, per_page)
                    for i, chunk in enumerate(chunks, start=1):
                        rows = [f"{c}\n" for c in chunk]
                        embed = embed.copy()
                        embed.description = "".join(r for r in rows)
                        embed.set_footer(
                            text=f"Page {i}/{len(chunks)} ({plural(rows).do_plural(f'{type.title()}|{plural_type}') if not type.endswith('d') else type})"
                        )
                        embeds.append(embed)
                    try:
                        del chunks
                    except Exception:
                        pass
                    return await self.alternative_paginate(embeds)
                else:
                    embed.description = "".join(f"{r}\n" for r in rows)
                    # t = plural(len(rows)):type.title()
                    embed.set_footer(
                        text=f"Page 1/1 ({plural(rows).do_plural(f'{type.title()}|{plural_type}') if not type.endswith('d') else type})"
                    )
                    """if you want to disable page numbers on non view based responses just hash out the line above lol"""
                    return await self.send(embed=embed)


DefaultContext.paginate = Context.paginate
DefaultContext.alternative_paginate = Context.alternative_paginate


class ConfirmView(View):
    def __init__(self, ctx: Context):
        super().__init__()
        self.value = False
        self.ctx: Context = ctx
        self.bot: discord.Client = ctx.bot

    @discord.ui.button(
        emoji="<:success:1367925770395320380>", style=discord.ButtonStyle.green
    )
    async def approve(self, interaction: discord.Interaction, _: discord.Button):
        """Approve the action"""

        self.value = True
        self.stop()

    @discord.ui.button(emoji="<:cancel:1367925747313803346>", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, _: discord.Button):
        """Decline the action"""

        self.value = False
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.ctx.author.id:
            return True
        else:
            await interaction.warning(
                "You aren't the **author** of this embed",
            )
            return False


class Confirmation(View):
    def __init__(
        self,
        author_id: int,
        yes,
        no,
    ):
        super().__init__()
        self.agree = discord.ui.Button(label="Yes", style=discord.ButtonStyle.green)
        self.disagree = discord.ui.Button(label="No", style=discord.ButtonStyle.red)
        self.agree.callback = yes
        self.disagree.callback = no
        self.author_id = author_id
        self.add_item(self.agree)
        self.add_item(self.disagree)

    async def interaction_check(self, interaction: discord.Interaction):
        exp = interaction.user.id == self.author_id
        if not exp:
            await interaction.response.defer(ephemeral=True)

        return exp

    def stop(self):
        for child in self.children:
            child.disabled = True

        return super().stop()

    async def on_timeout(self):
        self.stop()
        embed = self.message.embeds[0]
        embed.description = "Time's up!"
        return await self.message.edit(embed=embed, view=self)
