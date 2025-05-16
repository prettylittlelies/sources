from typing import Any

from discord.ext import commands

from .context import Context


def has_permissions(**permissions: Any):
    async def predicate(ctx: Context):
        fake = permissions.pop("fake", True)
        if isinstance(ctx, int):
            return [
                permission for permission, value in permissions.items() if value is True
            ]

        if ctx.author.id in ctx.bot.owner_ids:
            return True

        if ctx.author.guild_permissions.administrator:
            return True
        fake_permissions = []
        if fake:
            roles = [r.id for r in ctx.author.roles if r.is_assignable()]
            if len(roles) > 0:
                data = await ctx.bot.db.fetch(
                    """SELECT permissions FROM fake_permissions WHERE guild_id = $1 AND role_id = ANY($2)""",
                    ctx.guild.id,
                    roles,
                )
                for fake_perm in data:
                    fake_permissions.extend([d.lower() for d in fake_perm])
        missing_permissions = []
        for permission in permissions:
            if (
                getattr(ctx.author.guild_permissions, permission) is not True
                and permission.lower() not in fake_permissions
            ):
                missing_permissions.append(permission)
        if missing_permissions:
            raise commands.MissingPermissions(missing_permissions)
        return True

    return commands.check(predicate)


commands.has_permissions = has_permissions
