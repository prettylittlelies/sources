import discord

from .command import *
from .context import *
from .help import Help, map_check
from .interaction import *
from .warning import warning as ctx_warning, success as ctx_success
from .perms import premium, requires_perms

discord.TextChannel.warning = warning
discord.ext.commands.Context.warning = ctx_warning
discord.ext.commands.Context.success = ctx_success
discord.Thread.warning = warning

