import discord
from discord.ext import commands
from utils import utils
from datetime import datetime


class IronFleet(commands.Cog):
    def __init__(self, client):
        self.client = client

    @utils.isIronFleet()
    @utils.isMod()
    @commands.command(
        hidden=True,
        brief='This roles grant a member basic recruit status.',
        description='To use this command tag a member or type his full name. His `Prospective Recruit` role will be removed and he will receive the ranks of `Recruit`.',
        usage='?recruit <member>'
    )
    async def recruit(self, ctx, *, member):
        member = await utils.memberSearch(ctx, self.client, member)
        if member is None:
            return
        guild_roles = ctx.message.guild.roles
        recruit_role = discord.utils.get(guild_roles, name='Recruit')
        canread_role = discord.utils.get(guild_roles, name='Prospective Recruit')
        await member.add_roles(recruit_role, reason='Recruit Command')
        await member.remove_roles(canread_role, reason='Recruit Command')
        await ctx.message.delete()
        rr_channel = discord.utils.get(ctx.guild.channels, id=479313811518652417)
        await ctx.send(f'{member.mention} is now an Ironborn Recruit! *What is dead may never die!*\nHead over to {rr_channel.mention} to get your games assigned.')



def setup(client):
    client.add_cog(IronFleet(client))