import discord
from discord.ext import commands
from utils import utils
from utils.storage import Storage
import datetime, math, typing, re, random

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
        users.sort(key=lambda x: x.name)
        sumpages = math.ceil(len(users)/20)
        page = sumpages if page > sumpages else page          
        pagestart = (page * 20)-20
        pageend = pagestart + 19
        desctext = f'({str(len(users))} in total)\n'
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
        brief='Assign a member a new discord name.',
        description='Use this to assign a new discord name to one member.',
        usage='?nick <user> <new name>'
    )
    async def nick(self, ctx, member, *, new_name : str):
        member = await utils.memberSearch(ctx, self.client, member)
        if not member:
            return
        await member.edit(nick=new_name)
        await ctx.send(f'{member.mention} is now called \'{new_name}\'.')


    @commands.command(
        brief='Get this Guild\'s invitelink.',
        description='This sends you a PM the invite link to this Guild.',
        usage='?invite'
    )
    async def invite(self, ctx):
        try:
            link = await ctx.guild.invites()
            link = link[0]
        except:
            print(ctx.guild.channels)
            link = await ctx.guild.channels[0].create_invite(max_age=86400, reason=f'{ctx.author} requested an invite link.')
        await ctx.author.send(f'Use this link to invite people to {ctx.guild.name}\'s Discord Server: {link.url}')


    @commands.is_owner()
    @commands.command(
        hidden=True,
        description='SQL commands. Die.',
        usage='?sql <query>'
    )
    async def sql(self, ctx, *, query: str):
        r = self.Storage.execute_query_many(query, commit=True)
        await ctx.send(f'Executed SQL Query `{query}` successfully.\nResult:')
        await ctx.send(r)


    @commands.is_owner()
    @commands.command(
        hidden=True,
        brief='Message all guild owners.',
        description='Cradac can use this to message all guild owners.',
        usage='?announce <message>'
    )
    async def announce(self, ctx, *, message):
        for guild in self.client.guilds:
            await guild.owner.send(message)
            

    @commands.command(
        name='commands',
        brief='Get the GitHub link of this bot.',
        description='This command shows you the Github link of the Iron Justice.',
        usage='?commands'
    )
    async def cmnds(self, ctx):
        embed = utils.createEmbed(author=ctx.author, description='You can view the command documentation of the Iron Justice right [here](https://gist.github.com/Cradac/4544f0cbe9456a637c0d3a85061bda78).', colour='iron')
        await ctx.send(embed=embed)

    @commands.command(
        brief='Roll dice.',
        description='Use this command to roll one or more N sided dice.\n\
            X: amount of dice, default 1\n\
            N: number of sides on die, default 6\n\
            Y: modifier to add/substract',
        usage='?roll XdN+Y'
    )
    async def roll(self, ctx, arg:str = None):
        if not arg:
            amnt, sides, modifier = 1, 6, 0
        else:
            if not 'd' in arg:
                embed = utils.createEmbed(title='Wrong Syntax', description='The Syntax is wrong. Try something similar to this: `1d6+1`, `2d10`, `d20`', colour='error', author=ctx.author)
                await ctx.send(embed=embed)
            rslt = arg.split('d', 1)
            if rslt[0] == '':
                amnt = 1
                rest = rslt[1]
            else:
                amnt = int(rslt[0])
                rest = rslt[1]

            if '+' in rest:
                sides, modifier = rest.split('+', 1)
            elif '-' in rest:
                sides, modifier = rest.split('-', 1)
                modifier = int(modifier)
                modifier *= -1
            else:
                sides = rest
                modifier = 0
        results = list()
        sides, modifier = int(sides), int(modifier)
        for _ in range(amnt):
            results.append(random.randint(1, sides))
        result = sum(results) + modifier
        embed = utils.createEmbed(title=f'You rolled {amnt} d{sides}.', description=f'Result: {result}\nIndividual rolls:\n{", ".join(f"`{r}`" for r in results)}', author=ctx.author, colour='iron')
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command(
        hidden=True,
        brief='List all guilds featuring the Iron Justice',
        description='',
        usage='?guildlist'
    )
    async def guildlist(self, ctx):
        embed = utils.createEmbed(title='__List of Guilds__', description='\n'.join(f'{guild} `{guild.id}`' for guild in self.client.guilds), colour='iron')
        await ctx.send(embed=embed)
            




def setup(client):
    client.add_cog(Misc(client))