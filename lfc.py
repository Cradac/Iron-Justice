import discord
from discord.ext import commands
import asyncio
import guilds
from checks import matchlfcchannel

class LFC:
    def __init__(self, client):
        self.client = client

    async def auto_remove(self, member, role):
        await asyncio.sleep(10800)
        await self.client.remove_roles(member,role)
    
    @matchlfcchannel()
    @commands.command(pass_context=True, aliases=["lfg"],brief="Sets LFC status.", description=">>>'Looking for Crew':\nThis gives you the 'Looking for Crew' role. You can be tagged with it and tag others.\nYou can only use this in the LFC Channel.\nType !nlfc once you're in a crew to avoid getting LFC notifications.\n\nAliases:")
    async def lfc(self, ctx):
        server=ctx.message.server
        author=ctx.message.author
        #if ctx.message.channel.name == "looking-for-crew":
        role=discord.utils.get(server.roles,name="lfc")
        if role in author.roles:
            await self.client.say("You are already *looking for a crew*.")
        else:
            await self.client.add_roles(author, role)
            self.client.loop.create_task(self.auto_remove(author,role))
            await self.client.say("<@&{}>: {} is now *looking for a crew*.".format(role.id, author.mention))

    @matchlfcchannel()
    @commands.command(pass_context=True, aliases=["nlfg"], brief="Removes LFC status.", description=">>>No longer 'Looking for Crew':\nThis removes the 'Looking for Crew' role.\nIf you are looking for a crew again use '!lfc'.\n\nAliases:")
    async def nlfc(self, ctx):
        server=ctx.message.server
        author=ctx.message.author
        role=discord.utils.get(server.roles,name="lfc")
        if role in author.roles:
            await self.client.remove_roles(author, role)
            await self.client.say("You are no longer *looking for a crew*.")

def setup(client):
    client.add_cog(LFC(client))