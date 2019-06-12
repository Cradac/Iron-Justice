import discord
from discord.ext import commands
from utils import utils
from utils.storage import Storage
import datetime, math, typing

class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.Storage = Storage()


    @commands.command(
        brief='Get a list of all members of a role.',
        description='Get a list of members who are in a certain role.\n\
            Please wrap role names with spaces in quotation marks.',
        usage='?whois <role> [page=1]'
    )
    async def whois(self, ctx, *, rolename: str, page: typing.Optional[int]=1 ):
        role = await utils.roleSearch(ctx, self.client, rolename)
        if not role:
            return
        users = list()
        for member in ctx.guild.members:
            if role in member.roles:
                users.append(member)
        users.sort()
        sumpages = math.ceil(len(users)/20)
        page = sumpages if page > sumpages else page          
        pagestart = (page * 20)-20
        pageend = pagestart + 19
        desctext = "({} in total)\n".format(str(len(users)))
        for i in range(pagestart, pageend):
            try:
                desctext += users[i].mention + '\n'
            except IndexError:
                break

        embed = utils.createEmbed(title=f'__Users with the role `{role}`:__', description=desctext, colour='iron', author=ctx.author)
        embed.set_footer(text=f'Page {page}/{sumpages}')
        await ctx.send(embed=embed)


    @utils.isMod()
    @commands.command(
        hidden=True,
        usage='?nick <user> <new name>'
    )
    async def nick(self, ctx, member, *, new_name : str):
        member = await utils.memberSearch(ctx, self.client, member)
        if not member:
            return
        await member.edit(nick=new_name)
        await ctx.send(f'{member.mention} is now called \'{new_name}\'.')


    @commands.is_owner()
    @commands.command(
        hidden=True,
        usage='?sql <query>'
    )
    async def sql(self, ctx, *, query: str):
        r = self.Storage.execute_query_many(query, commit=True)
        await ctx.send(f'Executed SQL Query `{query}` successfully.\nResult:')
        await ctx.send(r)


    @commands.command(
        brief='Get this Guild\'s invitelink.',
        description='This sends you a PM the invite link to this Guild.'
    )
    async def invite(self, ctx):
        try:
            link = ctx.guild.invites[0]
        except:
            print(ctx.guild.channels)
            link = await ctx.guild.channels[0].create_invite(max_age=86400, reason=f'{ctx.author} requested an invite link.')
        await ctx.author.send(f'Use this link to invite people to {ctx.guild.name}\'s Discord Server: {link.url}')


def setup(client):
    client.add_cog(Misc(client))