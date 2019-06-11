import discord
from discord.ext import commands
import asyncio
import sqlite3
from sqlite3 import Error 
from utils.utils import isGod, isAdmin, isMod, isIronFleet, memberSearch
from utils.utils import create_connection, db_file, welcome, if_servers
from datetime import datetime


class IronFleet(commands.Cog):
    def __init__(self, client):
        self.client = client

    @isIronFleet()
    @isMod()
    @commands.command(
        hidden=True,
        brief='This roles grant a member basic recruit status.',
        description='To use this command tag a member or type his full name. His `Prospective Recruit` role will be removed and he will receive the ranks of `Recruit`.',
        usage='?recruit <member>'
    )
    async def recruit(self, ctx, *, member):
        member = await memberSearch(ctx, self.client, member)
        if member is None:
            return
        guild_roles = ctx.message.guild.roles
        recruit_role = discord.utils.get(guild_roles, name='Recruit')
        canread_role = discord.utils.get(guild_roles, name='Prospective Recruit')
        await member.add_roles(recruit_role, reason='Recruit Command')
        await asyncio.sleep(3)
        await member.remove_roles(canread_role, reason='Recruit Command')
        await ctx.message.delete()
        rr_channel = discord.utils.get(ctx.guild.channels, id=479313811518652417)
        await ctx.send(f'{member.mention} is now an Ironborn Recruit! *What is dead may never die!*\nHead over to {rr_channel.mention} to get your games assigned.')

    @commands.command(
        aliases=['invite'],
        brief='Get this Guild\'s invitelink.',
        description='This sends you a PM the invite link to this Guild.'
    )
    async def invite(self, ctx):
        try:
            link = ctx.guild.invites[0]
        except:
            link = ctx.guild.channels[0].create_invite(max_age=86400, reason=f'{ctx.author} requested an invite link.')
        await ctx.author.send(f'Use this link to invite people to {ctx.guild.name}\'s Discord Server: {link.url}')

def setup(client):
    client.add_cog(IronFleet(client))