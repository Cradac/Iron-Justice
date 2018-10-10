import discord
from discord.ext import commands
import asyncio
import sqlite3
from sqlite3 import Error 
from checks import isGod, isAdmin, isMod, isIronFleet#, isCrimson, crimson_id
from checks import create_connection, db_file
from checks import isGod, isAdmin, isMod, isIronFleet



class IronFleet:
    def __init__(self, client):
        self.client = client
    
    @isIronFleet()
    @isMod()
    @commands.command(hidden=True, aliases=["member"], brief="This roles grant a player basic member status.", description=">>>add Membership\nTo use this command tag a member or type his full name. His 'Stowaway' role will be removed and he will receive the ranks of 'Member' and 'Fledgling'.\n\nAliases:")
    async def membership(self, ctx, member:discord.Member):
        guild = ctx.message.guild
        for role in guild.roles:
            if role.name == "Member":
                role_member = role
            if role.name == "Fledgling":
                role_fledge = role
        await member.edit(roles=[role_member, role_fledge])
        await ctx.send("Gave {} the ranks of a basic member.".format(member.mention))

    @isIronFleet()
    @commands.command(aliases=["invite", "link"], brief="Get this Discord's invitelink.", description=">>>Invite Link\nThis sends a message with the invite link to the Iron Fleet's Discord.\n\nAliases:")
    async def invitelink(self, ctx):
        await ctx.message.author.send("Use this link to invite people to the Iron Fleet's Discord: https://discord.gg/cSZPMF7")

    @isGod()
    @commands.command(hidden=True)
    async def serverid(self, ctx):
        await ctx.send("Guild ID: `{}`".format(ctx.message.guild.id))

    @isGod()
    @commands.command(hidden=True)
    async def sql(self, *query : str):
        conn = create_connection(db_file)
        with conn:
            cur = conn.cursor()
            cur.execute(query)
            conn.commit()
    @isAdmin()
    @commands.command(hidden=True)
    async def nickname(self, ctx, member, *newname : str):
        newname = (" ").join(newname)
        member = ctx.message.mentions[0]
        await self.client.change_nickname(member, newname)
        print("{} is now called {}".format(member.name, newname))
    

    '''
    @isCrimson()
    @isIronFleet()
    @commands.command(hidden=True)
    async def crewup(self, ctx, *name : str):
        member = ctx.message.mentions[0]
        await self.client.add_roles(member, discord.utils.get(ctx.message.guild.roles, id=482646954829152256))
        await self.client.send_message(ctx.message.guild.get_member(crimson_id), "{} just joined your crew!".format(member.mention))
'''






def setup(client):
    client.add_cog(IronFleet(client))