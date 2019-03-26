import discord
from discord.ext import commands
import asyncio
import cogs.guilds
from cogs.checks import matchlfcchannel

class LFC:
    def __init__(self, client):
        self.client = client

    async def auto_remove(self, member, role):
        await asyncio.sleep(3600)
        await member.remove_roles(role)
    
    @matchlfcchannel()
    @commands.command(aliases=["lfg"],brief="Sets LFC status.", description=">>>'Looking for Crew':\nThis gives you the 'Looking for Crew' role. You can be tagged with it and tag others.\nYou can only use this in the LFC Channel.\nType !nlfc once you're in a crew to avoid getting LFC notifications.\n\nAliases:")
    async def lfc(self, ctx):
        guild=ctx.message.guild
        author=ctx.message.author
        try:
            for it_role in guild.roles:
                if role.name.lower() == 'lfc' or role.name.lower() == 'looking for crew':
                    role = it_role
                    break
        except:
            await ctx.send("There is no LFC role defined. Please contact an admin.")
            return
        if role in author.roles:
            await ctx.send("You are already *looking for a crew*.")
        else:
            await author.add_roles(role)
            self.client.loop.create_task(self.auto_remove(author,role))
            await ctx.send("{}: {} is now *looking for a crew*.".format(role.mention, author.mention))

    @matchlfcchannel()
    @commands.command(aliases=["nlfg"], brief="Removes LFC status.", description=">>>No longer 'Looking for Crew':\nThis removes the 'Looking for Crew' role.\nIf you are looking for a crew again use '!lfc'.\n\nAliases:")
    async def nlfc(self, ctx):
        guild=ctx.message.guild
        author=ctx.message.author
        role=discord.utils.get(guild.roles,name="lfc")
        if role in author.roles:
            await author.remove_roles(role)
            await ctx.send("You are no longer *looking for a crew*.")

def setup(client):
    client.add_cog(LFC(client))