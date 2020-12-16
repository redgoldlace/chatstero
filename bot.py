import functools
import random
import re

import markovify
import toml

from discord import AllowedMentions, Client, Intents
from discord.ext import commands


ALLOWED_MENTIONS = AllowedMentions.none()
INTENTS = Intents(emojis=True, guilds=True, messages=True)

EMOJI_REGEX = re.compile("<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>")
CHANNEL_REGEX = re.compile("<#([0-9]*)>")
USER_MENTION = re.compile("<@(!?)([0-9]*)>|@[a-zA-Z0-9_]*")


with open("config.toml", "r", encoding="utf-8", errors="ignore") as toml_file:
    CONFIG = toml.load(toml_file)

with open("markov.txt", "r", encoding="utf-8", errors="ignore") as markov_file:
    model = markovify.NewlineText(markov_file.read(), state_size=5, retain_original=False)
    model.compile(inplace=True)


class Chatstero(Client):
    def __init__(self):
        super().__init__(allowed_mentions=ALLOWED_MENTIONS, intents=INTENTS)

    def _generate_markov(self, message: discord.Message):
        sentence = model.make_sentence(test_output=False)

        no_mentions = re.sub(USER_MENTION, message.author.mention, sentence)
        channels = re.sub(CHANNEL_REGEX, random.choice(message.guild.channels).mention, no_mentions)
        result = re.sub(EMOJI_REGEX, str(random.choice(self.emojis)), channels)

        return result

    async def generate_markov(self, message: discord.Message):
        func = functools.partial(self._generate_markov, message)
        result = await self.loop.run_in_executor(None, func)
        return result

    async def on_message(self, message: discord.Message):
        if self.user in message.mentions:
            result = await self.generate_markov(message)
            await message.channel.send(result)

        elif message.guild and message.channel.name == "crabversation":
            result = await self.generate_markov(message)
            await message.channel.send(result)      


bot = Chatstero()
bot.run(CONFIG["token"])
