import discord
from discord.ext import commands
import asyncio
import cogs.guilds
from cogs.helper import matchlfcchannel

class LFC(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def auto_remove(self, user_id, guildlist):
        await asyncio.sleep(5)
        for tup in guildlist:
            try:
                await tup[0].get_member(user_id).remove_roles(tup[1])
            except:
                continue
    
    @matchlfcchannel()
    @commands.command(aliases=["lfg"],brief="Sets LFC status.", description=">>>'Looking for Crew':\nThis gives you the 'Looking for Crew' role. You can be tagged with it and tag others.\nYou can only use this in the LFC Channel.\nType ?nlfc once you're in a crew to avoid getting LFC notifications.\n\nAliases:")
    async def lfc(self, ctx):
        author=ctx.message.author
        role = None
        guildlist = []
        for it_role in ctx.guild.roles:
            if it_role.name.lower() == 'lfc' or it_role.name.lower() == 'looking for crew':
                role = it_role
                break
        #break if already LFC
        if role in author.roles:
            await ctx.send("You are already *looking for a crew*.")
            return
        await ctx.send("{}: {} is now *looking for a crew*.".format(role.mention, author.mention))

        #iterate through all guilds and try to add LFC
        for guild in self.client.guilds:
            for it_role in guild.roles:
                if it_role.name.lower() == 'lfc' or it_role.name.lower() == 'looking for crew':
                    role = it_role
                    break
            member = guild.get_member(author.id)
            if member is None:
                continue
            try:
                await member.add_roles(role)
            except discord.errors.Forbidden:
                continue
            guildlist.append((guild, role))
        self.client.loop.create_task(self.auto_remove(author.id,guildlist))


    @matchlfcchannel()
    @commands.command(aliases=["nlfg"], brief="Removes LFC status.", description=">>>No longer 'Looking for Crew':\nThis removes the 'Looking for Crew' role.\nIf you are looking for a crew again use '?lfc'.\n\nAliases:")
    async def nlfc(self, ctx):
        author=ctx.message.author
        for it_role in ctx.guild.roles:
            if it_role.name.lower() == 'lfc' or it_role.name.lower() == 'looking for crew':
                role = it_role
                break
        #break if not LFC
        if role not in author.roles:
            return
        await ctx.send("You are no longer *looking for a crew*.")

        for guild in self.client.guilds:
            for it_role in guild.roles:
                if it_role.name.lower() == 'lfc' or it_role.name.lower() == 'looking for crew':
                    role = it_role
                    break
            member = guild.get_member(author.id)
            if member is None:
                continue
            try:
                await member.remove_roles(role)
            except discord.errors.Forbidden:
                continue

def setup(client):
    client.add_cog(LFC(client))