import discord, asyncio, cogs.guilds
from discord.ext import commands
from random import choice
from cogs.helper import isMod, isAdmin, isGod, createEmbed


channel_names = ['Silence', 'Iron Victory', 'Leviathan', 'Kraken\'s Kiss', 'Reaper\'s Wind']
created_channels = []

class AutoVoice(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel.name == "Get Ship!":                #Joined Get Ship Voice
            category = self.client.get_channel(after.channel.category_id)
            if len(channel_names == 0):
                name = "Iron Fleet Ship"
            else:
                name = choice(channel_names)
                channel_names.remove(name)
            voice_channel = await category.create_voice(name, reason='Created ship channel.', position=len(category.channels)-1)
            created_channels.append(voice_channel)
            member.move_to(voice_channel, reason='Moved to created channel.')

        elif before.channel in created_channels and after.channel is None and len(before.channel.members) == 1:               #Left any of the created Voice Channels
            await before.channel.delete()
            created_channels.remove(before.channel)
            channel_names.append(before.channel.name)

    @isAdmin()
    @commands.command()
    async def channels(self, ctx):
        embed = createEmbed(author=ctx.author, colour='iron')
        available_names = ''
        for name in channel_names:
            available_names += f'- {name}\n'
        if available_names == '':
            available_names = 'None available.'
        embed.add_field(name='__Available Ship Names:__', value=available_names)
        used_names = ''
        for channel in created_channels:
            used_names += f'- {channel.name}\n'
        if used_names == '':
            used_names = 'None used.'
        embed.add_field(name='__Used Ship Names:__', value=used_names)
        await ctx.send(embed=embed)


