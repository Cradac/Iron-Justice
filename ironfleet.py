import discord
from discord.ext import commands
import asyncio
import sqlite3
from sqlite3 import Error 
from checks import isGod, isAdmin, isMod, isIronFleet, isCrimson, crimson_id
from checks import create_connection, db_file



class IronFleet:
    def __init__(self, client):
        self.client = client
    
    @isIronFleet()
    @isMod()
    @commands.command(pass_context=True, hidden=True, aliases=["member"], brief="This roles grant a player basic member status.", description="mod-command:Membership\nTo use this command tag a member or type his full name. His 'Stowaway' role will be removed and he will receive the ranks of 'Member' and 'Fledgling'.\n\n aliases:")
    async def membership(self, ctx, member):
        server = ctx.message.server
        msg = ctx.message
        if len(msg.mentions) != 0:
            member = msg.mentions[0]
        else:
            member = discord.utils.get(ctx.message.server.members, name=member)
        for role in server.roles:
            if role.name == "Member":
                role_member = role
            if role.name == "Fledgling":
                role_fledge = role
        await self.client.replace_roles(member, role_member, role_fledge)
        await self.client.say("Gave {} the ranks of a basic member.".format(member.mention))

    @isIronFleet()
    @commands.command(pass_context=True, aliases=["invite", "link"], brief="Get this Discord's invitelink.", description=">>>Invite Link\nThis sends a message with the invite link to the Iron Fleet's Discord.\n\nAliases:")
    async def invitelink(self, ctx):
        await self.client.send_message(ctx.message.author, "Use this link to invite people to the Iron Fleet's Discord: https://discord.gg/ttNYzkQ")

    @isGod()
    @commands.command(pass_context=True, hidden=True)
    async def serverid(self, ctx):
        await self.client.say("Server ID: `{}`".format(ctx.message.server.id))

    @isGod()
    @commands.command(hidden=True)
    async def sql(self, *query : str):
        conn = create_connection(db_file)
        with conn:
            cur = conn.cursor()
            cur.execute(query)
            conn.commit()

    @isCrimson()
    @isIronFleet()
    @commands.command(pass_context=True, hidden=True)
    async def crewup(self, ctx, *name : str):
        member = ctx.message.mentions[0]
        await self.client.add_roles(member, discord.utils.get(ctx.message.server.roles, id="482646954829152256"))
        await self.client.send_message(ctx.message.server.get_member(crimson_id), "{} just joined your crew!".format(member.mention))
    
    @isAdmin()
    @commands.command(pass_context=True, hidden=True)
    async def leave_server(self, ctx):
        server = ctx.message.server
        await self.client.leave_server(server)
        print("Left Server {} ({}).".format(server.name, server.id))
    






def setup(client):
    client.add_cog(IronFleet(client))