import discord
from discord.ext import commands
import asyncio
from utils import utils
from utils.storage import Storage

Utils = utils.Utils()

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
    
    @Utils.matchLFCChannel()
    @commands.command(
        brief='Sets the user into `Looking for Crew` status for 2 hours.',
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


    @Utils.matchLFCChannel()
    @commands.command(
        brief='Removes the `Looking for Crew` status manually.',
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