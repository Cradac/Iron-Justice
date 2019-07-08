import discord, asyncio, utils
from discord.ext import commands
from random import choice
from utils.utils import auto_voice_channel_names as channel_names
from utils.storage import Storage


class AutoVoice(commands.Cog, name='Auto-Voice'):
    def __init__(self, client):
        self.client = client

        self.Storage = Storage()

        self.created_channels = []

    @commands.Cog.listener()
    async def on_voice_state_update(self, user: discord.Member, before, after):
        if after.channel:
            auto_voice_channel = self.Storage.get_auto_voice_channel(user.guild)
            if after.channel == auto_voice_channel:                                 #Joined Get Ship Voice
                category = self.client.get_channel(after.channel.category_id)
                names = self.Storage.get_auto_voice_names(user.guild)
                names = channel_names if len(names) == 0 else names
                name = choice(names)
                pos = auto_voice_channel.position + 1
                voice_channel = await category.create_voice_channel(name, reason='Created ship channel.', position=pos)
                await voice_channel.edit(position=pos, reason='Moved Ship Channel.')
                self.created_channels.append(voice_channel)
                await user.move_to(voice_channel, reason='Moved to created channel.')
        
        if before.channel in self.created_channels and len(before.channel.members) == 0:               #Left any of the created Voice Channels
            try:
                await before.channel.delete(reason='Ship unmanned.')
            except discord.errors.NotFound:
                pass
            self.created_channels.remove(before.channel)

def setup(client):
    client.add_cog(AutoVoice(client))