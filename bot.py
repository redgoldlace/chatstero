import functools
import random
import re

import markovify
import toml

from discord import AllowedMentions, Intents
from discord.ext import commands

with open("config.toml", "r", encoding="utf-8", errors="ignore") as toml_file:
    CONFIG = toml.load(toml_file)

EMOJI_REGEX = "<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>"

with open("markov.txt", "r", encoding="utf-8", errors="ignore") as markov_file:
    model = markovify.NewlineText(markov_file.read(), state_size=5, retain_original=False)
    model.compile(inplace=True)

intents = Intents(
    emojis=True,
    guilds=True,
    messages=True
)


class Chatstero(commands.Bot):

    def _generate_markov(self, ctx: commands.Context):
        result = model.make_sentence(test_output=False)
        result = re.sub("<@(!?)([0-9]*)>", ctx.author.mention, result)
        result = re.sub("@[a-zA-Z0-9_]*", ctx.author.mention, result)
        result = re.sub("<#([0-9]*)>", lambda _: random.choice(ctx.guild.channels).mention, result)
        result = re.sub(EMOJI_REGEX, lambda _: str(random.choice(self.emojis)), result)

        return result

    async def generate_markov(self, ctx: commands.Context):
        func = functools.partial(self._generate_markov, ctx)
        result = await self.loop.run_in_executor(None, func)
        await ctx.send(result, allowed_mentions=AllowedMentions.none())

    async def on_message(self, message):
        if self.user in message.mentions:
            ctx = await self.get_context(message)
            await self.generate_markov(ctx)


bot = Chatstero("", intents=intents)
bot.run(CONFIG["token"])
