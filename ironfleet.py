import discord
from discord.ext import commands
import asyncio
import checks
from checks import isGod, isAdmin, isMod

servers=["479300072077787160","421650482176589835"]
def isIronFleet():
    def inServer(ctx):
        if ctx.message.server.id in servers:
            return True
        return False
    return commands.check(inServer)

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



def setup(client):
    client.add_cog(IronFleet(client))