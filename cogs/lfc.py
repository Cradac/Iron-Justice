import discord
from discord.ext import commands
import asyncio
import utils.guilds
from utils.utils import matchlfcchannel
from utils.storage import Storage

class LFC(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.Storage = Storage()


    async def auto_remove(self, user: discord.User):
        await asyncio.sleep(7200)
        for guild in self.Storage.get_lfc_enabled_guilds(self.client):
            if user in guild.members:
                role = self.Storage.get_lfc_role(guild)
                try:
                    await guild.get_member(user.id).remove_roles(role)
                except discord.Forbidden:
                    continue

    '''async def auto_remove(self, user_id, guildlist, ctx):
        await asyncio.sleep(7200)
        for tup in guildlist:
            try:
                if ctx.bot.dictGuilds[tup[0].id].enabled['lfc']:
                    await tup[0].get_member(user_id).remove_roles(tup[1])
            except:
                continue'''
    
    @matchlfcchannel()
    @commands.command(
        brief='Sets the user into LFC status for 2 hours.',
        description='This command gives the user the set `Looking for Crew` role. \n\
            You can only use this command in the set channels.\n\
            Type ?nlfc once you\'re in a crew to avoid getting further notifications.\n\
            The role will be automatically removed after 2 hours.',
        usage='?lfc'
    )
    async def lfc(self, ctx):
        local_role = self.Storage.get_lfc_role(ctx.guild)
        if local_role not in ctx.author.roles:
            user = self.client.get_user(ctx.author.id)
            for guild in self.Storage.get_lfc_enabled_guilds(self.client):
                if user in guild.members:
                    role = self.Storage.get_lfc_role(guild)
                    try:
                        await guild.get_member(user.id).add_roles(role)
                    except discord.Forbidden:
                        continue
            await ctx.send(f'{local_role.mention}, {ctx.author.mention} is now looking for crew.')
            self.client.loop.create_task(self.auto_remove(user))


    @matchlfcchannel()
    @commands.command(
        brief="Removes LFC status.",
        description='This removes the `Looking for Crew` status.\n\
            If you are looking for a crew again use `?lfc`.',
        usage='?nlfc'
    )
    async def nlfc(self, ctx):
        local_role = self.Storage.get_lfc_role(ctx.guild)
        if local_role in ctx.author.roles:
            user = self.client.get_user(ctx.author.id)
            for guild in self.Storage.get_lfc_enabled_guilds(self.client):
                if user in guild.members:
                    role = self.Storage.get_lfc_role(guild)
                    try:
                        await guild.get_member(user.id).remove_roles(role)
                    except discord.Forbidden:
                        continue
            await ctx.send(f'{ctx.author.mention}, you are no longer looking for a crew.')

def setup(client):
    client.add_cog(LFC(client))