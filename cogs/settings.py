import discord
from discord.ext import commands
import asyncio

class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client

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
            await ctx.send('Possible modules to configure are:' + '\n• '.join(c.name for c in ctx.command.commands))
        pass

    @config.command()
    async def lfc(self, ctx, status:bool=None, channels:commands.Greedy[discord.TextChannel]=None):
        pass

    @config.command()
    async def profile(self, ctx, status:bool=None, channels:commands.Greedy[discord.TextChannel]=None):
        pass

    @config.command()
    async def auto_voice(self, ctx, channel:discord.VoiceChannel):
        pass

    '''
        Command Group to add and remove names to the voice channel list.
        Default removes all added names and uses the default name list.
    '''

    @commands.group()
    async def auto_voice_names(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send('Possible subcommands to invoke are:' + '\n• '.join(c.name for c in ctx.command.commands))
        pass
    
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