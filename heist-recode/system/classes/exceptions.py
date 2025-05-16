from typing import Any

from discord.ext.commands import CommandError

class InvalidSubCommand(CommandError):
    def __init__(self: "InvalidSubCommand", message: str, **kwargs: Any):
        super().__init__(message)


