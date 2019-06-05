import discord, asyncio, cogs.guilds
from discord.ext import commands
from random import choice
from cogs.utils import isMod, isAdmin, isGod, createEmbed


channel_names = ['Silence', 'Iron Victory', 'Leviathan', 'Kraken\'s Kiss', 'Reaper\'s Wind', 'Black Wind', ' Sea Bitch', 'Silence', 'Noble Lady', 'Red God\'s Wrath', 'Shrike', 'Shade', 'Ghost', 'Slaver\'s Scream', 'Sea Song', 'Thunderer', 'Nighflyer', 'Silverfin', 'Black Wind', 'Great Kraken']
created_channels = []

class AutoVoice(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel is not None and after.channel.name == "Get a Ship!":                #Joined Get Ship Voice
            category = self.client.get_channel(after.channel.category_id)
            if len(channel_names) == 0:
                name = "Iron Fleet Ship"
            else:
                name = choice(channel_names)
                channel_names.remove(name)
            pos = len(category.channels)-1
            voice_channel = await category.create_voice_channel(name, reason='Created ship channel.')
            await voice_channel.edit(position=pos, reason='Moved Ship Channel.')
            created_channels.append(voice_channel)
            await member.move_to(voice_channel, reason='Moved to created channel.')
        
        if before.channel in created_channels and len(before.channel.members) == 0:               #Left any of the created Voice Channels
            try:
                await before.channel.delete(reason='Ship unmanned.')
            except discord.errors.NotFound:
                pass
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
        embed.set_thumbnail(url=ctx.guild.icon_url_as(format='png', size=1024))
        await ctx.send(embed=embed)



def setup(client):
    client.add_cog(AutoVoice(client))