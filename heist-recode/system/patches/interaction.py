from contextlib import suppress
import discord
from data.config import CONFIG

class Interaction(discord.Interaction):
    def __init__(self):
        super().__init__()

    async def success(self, text, **kwargs):
        emoji = kwargs.pop("emoji", self.bot.emojis.get('success'))
        color = CONFIG['embed_colors']['success']
        embed = discord.Embed(
            color=color, description=f"{emoji} {self.user.mention}: {text}"
        )
        if footer := kwargs.get("footer"):
            if isinstance(footer, tuple):
                embed.set_footer(text=footer[0], icon_url=footer[1])
            else:
                embed.set_footer(text=footer)
        if author := kwargs.get("author"):
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
        with suppress(discord.InteractionResponded):
            await self.response.defer(
                ephemeral=True,
            )

        return await self.followup.send(
            embed=embed,
            **kwargs,
            ephemeral=True,
        )

    async def normal(self, text, **kwargs):
        color = self.client.config["colors"]["bleed"]
        embed = discord.Embed(
            color=color,
            description=f"{kwargs.pop('emoji', '')} {self.user.mention}: {text}",
        )
        if footer := kwargs.get("footer"):
            if isinstance(footer, tuple):
                embed.set_footer(text=footer[0], icon_url=footer[1])
            else:
                embed.set_footer(text=footer)
        if author := kwargs.get("author"):
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
        with suppress(discord.InteractionResponded):
            await self.response.defer(
                ephemeral=True,
            )
        return await self.followup.send(embed=embed, **kwargs)

    async def fail(self, text, **kwargs):
        emoji = kwargs.pop("emoji", self.bot.emojis.get('warning'))
        color = CONFIG['embed_colors']['error']
        embed = discord.Embed(
            color=color, description=f"{emoji} {self.user.mention}: {text}"
        )
        if footer := kwargs.get("footer"):
            if isinstance(footer, tuple):
                embed.set_footer(text=footer[0], icon_url=footer[1])
            else:
                embed.set_footer(text=footer)
        if author := kwargs.get("author"):
            if isinstance(author, tuple):
                embed.set_author(name=author[0], icon_url=author[1])
            else:
                embed.set_author(name=author)
        if kwargs.get("return_embed", False) is True:
            return embed
        return await self.followup.send(embed=embed, **kwargs, ephemeral=True)

    async def warning(self, text, **kwargs):
        emoji = kwargs.pop("emoji", self.bot.emojis.get('warning'))
        color = self.client.config["colors"]["warning"]
        embed = discord.Embed(
            color=color,
            description=f"{emoji or ''} {self.user.mention}: {text}",
        )
        if footer := kwargs.get("footer"):
            if isinstance(footer, tuple):
                embed.set_footer(text=footer[0], icon_url=footer[1])
            else:
                embed.set_footer(text=footer)
        if author := kwargs.get("author"):
            if isinstance(author, tuple):
                embed.set_author(name=author[0], icon_url=author[1])
            else:
                embed.set_author(name=author)
        if kwargs.get("return_embed", False) is True:
            return embed
        with suppress(discord.InteractionResponded):
            await self.response.defer(
                ephemeral=True,
            )
        return await self.followup.send(
            embed=embed,
            **kwargs,
            ephemeral=True,
        )


discord.Interaction.success = Interaction.success
discord.Interaction.warning = Interaction.warning
discord.Interaction.normal = Interaction.normal
discord.Interaction.fail = Interaction.fail
