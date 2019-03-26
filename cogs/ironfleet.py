import discord
from discord.ext import commands
import asyncio
import sqlite3
from sqlite3 import Error 
from cogs.checks import isGod, isAdmin, isMod, isIronFleet, memberSearch
from cogs.checks import create_connection, db_file



class IronFleet(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @isIronFleet()
    @isMod()
    @commands.command(hidden=True, aliases=["member"], brief="This roles grant a player basic member status.", description=">>>add Membership\nTo use this command tag a member or type his full name. His 'Stowaway' role will be removed and he will receive the ranks of 'Member' and 'Fledgling'.\n\nAliases:")
    async def membership(self, ctx, *member):
        member = await memberSearch(ctx, self.client, " ".join(member))
        if member is None:
            return
        guild = ctx.message.guild
        for role in guild.roles:
            if role.name == "Member":
                role_member = role
            if role.name == "Fledgling":
                role_fledge = role
        await member.edit(roles=[role_member, role_fledge])
        await ctx.message.delete()
        await ctx.send("{} is now a true Ironborn! *What is dead may never die!*".format(member.mention))

    @isIronFleet()
    @isMod()
    @commands.command(hidden=True, aliases=["recruit"], brief="This roles grant a player basic recruit status.", description=">>>add Recruit Rank\nTo use this command tag a member or type his full name. His 'Stowaway' role will be removed and he will receive the ranks of 'Recruit'.\n\nAliases:")
    async def recruitment(self, ctx, *member):
        member = await memberSearch(ctx, self.client, " ".join(member))
        if member is None:
            return
        guild_roles = ctx.message.guild.roles
        recruit_role = discord.utils.get(guild_roles, name='Recruit')
        await member.add_role(recruit_role)
        await ctx.message.delete()
        await ctx.send("{} is now an Ironborn Recruit! *What is dead may never die!*".format(member.mention))

    @isIronFleet()
    @commands.command(aliases=["invite"], brief="Get this Discord's invitelink.", description=">>>Invite Link\nThis sends a message with the invite link to the Iron Fleet's Discord.\n\nAliases:")
    async def invitelink(self, ctx):
        await ctx.message.author.send("Use this link to invite people to the Iron Fleet's Discord: https://discord.gg/cSZPMF7")

def setup(client):
    client.add_cog(IronFleet(client))