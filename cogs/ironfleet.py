import discord
from discord.ext import commands
import asyncio
import sqlite3
from sqlite3 import Error 
from cogs.checks import isGod, isAdmin, isMod, isIronFleet, memberSearch
from cogs.checks import create_connection, db_file



class IronFleet:
    def __init__(self, client):
        self.client = client
    
    @isIronFleet()
    @isMod()
    @commands.command(hidden=True, aliases=["member"], brief="This roles grant a player basic member status.", description=">>>add Membership\nTo use this command tag a member or type his full name. His 'Stowaway' role will be removed and he will receive the ranks of 'Member' and 'Fledgling'.\n\nAliases:")
    async def membership(self, ctx, *member):
        member = await memberSearch(ctx, self.client, " ".join(member))
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
    @commands.command(aliases=["invite"], brief="Get this Discord's invitelink.", description=">>>Invite Link\nThis sends a message with the invite link to the Iron Fleet's Discord.\n\nAliases:")
    async def invitelink(self, ctx):
        await ctx.message.author.send("Use this link to invite people to the Iron Fleet's Discord: https://discord.gg/cSZPMF7")
       

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
    

def setup(client):
    client.add_cog(IronFleet(client))