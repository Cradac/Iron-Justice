import discord
from discord.ext import commands
import asyncio, utils, auto_voice
from storage import Storage


class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.Storage = Storage()

    '''
        Setup goes through all config step one by one 
    '''
    @commands.command()
    async def setup(self, ctx):
        pass

    '''
        config is a command group which over spans `lfc`, `profile` and others.
    '''
    @commands.group(aliases=['settings', 'set', 'configure'])
    async def config(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send('Possible modules to configure are:\n• ' + '\n• '.join(c.name for c in ctx.command.commands))

    @config.command()
    async def lfc(self, ctx, status:bool=None, channels:commands.Greedy[discord.TextChannel]=None):
        if status is not None:
            self.Storage.update_lfc_status(ctx.guild, status)
            if channels:
                self.Storage.add_lfc_channels(ctx.guild, channels)

        # WIZARD
        else:
            def reaction_check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) in ["✅", "❌"]
            # Turn on or off
            msg = await ctx.send('Do you want to enable the `Looking for Crew`-Module? Please react below.')
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            try:
                r = await self.client.wait_for('reaction_add', timeout=30.0, check=reaction_check)
            except asyncio.TimeoutError:
                await ctx.send('Cancelled the Setup.')
            status = str(r[0]) == '✅'
            self.Storage.update_lfc_status(ctx.guild, status)
            s = 'on' if status else 'off'
            await ctx.send(f'The `Looking for Crew`-Module is now turned {s}.')
            
            if status:
                def message_check(msg):
                    return msg.author == ctx.author and msg.content
                # Select channels
                await ctx.send('Please mention all channels you want to enable the module in. If you don\'t want to restrict it to certain channels just type `all`.')
                try:
                    msg = await self.client.wait_for('message', timeout=60.0, check=message_check)
                except asyncio.TimeoutError:
                    await ctx.send('Cancelled the Setup.')
                channels = msg.channel_mentions
                if len(channels) > 0:
                    self.Storage.add_lfc_channels(ctx.guild, msg.channel_mentions)
                    await ctx.send('The `Looking for Crew`-Module can be used in all mentioned channels.')
                else:
                    self.Storage.delete_all_lfc_channels(ctx.guild)
                    await ctx.send('The `Looking for Crew`-Module can be used in all channels.')
            else:
                self.Storage.delete_all_lfc_channels(ctx.guild)

        # Send Settings Embed
        s = 'enabled' if status else 'disabled'
        embed = utils.createEmbed(title='**__`Looking for Crew`-Setup__**', description=f'The module is {s}.', colour='iron')
        ch = '`all`' if len(channels) == 0 else ' '.join(c.mention for c in channels)
        embed.add_field(name='__Channels__', value=ch)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url_as(format='png', size=128))
        embed.set_thumbnail(url=ctx.guild.icon_url_as(format='png', size=512))
        await ctx.send(embed=embed)


    @config.command()
    async def profile(self, ctx, status:bool=None, channels:commands.Greedy[discord.TextChannel]=None):
        if status is not None:
            self.Storage.update_profile_status(ctx.guild, status)
            if channels:
                self.Storage.add_profile_channels(ctx.guild, channels)

        # WIZARD
        else:
            def reaction_check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) in ["✅", "❌"]
            # Turn on or off
            msg = await ctx.send('Do you want to enable the `Profile`-Module? Please react below.')
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            try:
                r = await self.client.wait_for('reaction_add', timeout=30.0, check=reaction_check)
            except asyncio.TimeoutError:
                await ctx.send('Cancelled the Setup.')
            status = str(r[0]) == '✅'
            self.Storage.update_profile_status(ctx.guild, status)
            s = 'on' if status else 'off'
            await ctx.send(f'The `Profile`-Module is now turned {s}.')
            
            if status:
                def message_check(msg):
                    return msg.author == ctx.author and msg.content
                # Select channels
                await ctx.send('Please mention all channels you want to enable the module in. If you don\'t want to restrict it to certain channels just type `all`.')
                try:
                    msg = await self.client.wait_for('message', timeout=60.0, check=message_check)
                except asyncio.TimeoutError:
                    await ctx.send('Cancelled the Setup.')
                channels = msg.channel_mentions
                if len(channels) > 0:
                    self.Storage.add_profile_channels(ctx.guild, msg.channel_mentions)
                    await ctx.send('The `Profile`-Module can be used in all mentioned channels.')
                else:
                    self.Storage.delete_all_profile_channels(ctx.guild)
                    await ctx.send('The `Profile`-Module can be used in all channels.')
            else:
                self.Storage.delete_all_profile_channels(ctx.guild)

        # Send Settings Embed
        s = 'enabled' if status else 'disabled'
        embed = utils.createEmbed(title='**__`Profile`-Setup__**', description=f'The module is {s}.', colour='iron')
        ch = '`all`' if len(channels) == 0 else ' '.join(c.mention for c in channels)
        embed.add_field(name='__Channels__', value=ch)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url_as(format='png', size=128))
        embed.set_thumbnail(url=ctx.guild.icon_url_as(format='png', size=512))
        await ctx.send(embed=embed)

    @config.command()
    async def auto_voice(self, ctx, channel:discord.VoiceChannel):
        self.Storage.update_auto_voice_channel(ctx.guild, channel)
        await ctx.send(f'Set the channel `{channel.name}` as Auto-Voice Channel.')

    @auto_voice.error
    async def auto_voice_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Voice channel could not be found. Either use the channel ID or the full name.')

    '''
        Command Group to add and remove names to the voice channel list.
        Default removes all added names and uses the default name list.
    '''

    @commands.group()
    async def auto_voice_names(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send('Possible subcommands to invoke are:\n• ' + '\n• '.join(c.name for c in ctx.command.commands))
    
    @auto_voice_names.command()
    async def get(self, ctx):
        l = self.Storage.get_auto_voice_names(ctx.guild)
        l = l if len(l) > 0 else auto_voice.channel_names
        embed = utils.createEmbed(title='__**List of voice channel names**__', description='• ' + '\n• '.join(l), colour='iron', author=ctx.author)
        await ctx.send(embed=embed)

    @auto_voice_names.command()
    async def add(self, ctx, *names):
        names = ' '.join(name.strip() for name in names).split(',')
    
    @auto_voice_names.command(aliases=['remove'])
    async def delete(self, ctx, *names):
        names = ' '.join(name.strip() for name in names).split(',')

    @auto_voice_names.command()
    async def default(self, ctx):
        pass

         
    

 

def setup(client):
    client.add_cog(Settings(client))