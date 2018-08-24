import discord
from discord.ext import commands
import asyncio
import sqlite3
from sqlite3 import Error 
from checks import isGod, isAdmin, isMod, isIronFleet
from checks import create_connection, db_file



class IronFleet:
    def __init__(self, client):
        self.client = client
    
    @isIronFleet()
    @isMod()
    @commands.command(pass_context=True, hidden=True, aliases=["member"])
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
            cur.commit()




def setup(client):
    client.add_cog(IronFleet(client))