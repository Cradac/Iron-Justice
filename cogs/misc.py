import discord
from discord.ext import commands
from utils import utils
from utils.storage import Storage
import datetime, math, typing, re, random, asyncio

class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.whois_messages = dict()
        self.prev = '⏪'
        self.next = '⏩'
        self.beginning = '⏮'
        self.end = '⏭'
        self.stop = '⏹'

        self.emojis = [self.beginning, self.prev, self.next, self.end, self.stop]

        self.Storage = Storage()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        if user.bot:
            return
        if reaction.message.id in self.whois_messages.keys() and reaction.emoji in self.emojis:
            await reaction.remove(user)
            users = self.whois_messages.get(reaction.message.id)['users']
            max_page = math.ceil(len(users)/20)
            cur_page = self.whois_messages.get(reaction.message.id)['page']
            page = 1
            role = self.whois_messages.get(reaction.message.id)['role']
            if reaction.emoji == self.beginning:
                embed = self.get_page(users, page, role)
            elif reaction.emoji == self.end:
                page = max_page
                embed = self.get_page(users, page, role)
            elif reaction.emoji == self.next:
                cur_page = self.whois_messages.get(reaction.message.id)['page']
                page = cur_page+1 if cur_page+1 <= max_page else max_page
                embed = self.get_page(users, page, role)
            elif reaction.emoji == self.prev:
                page = cur_page-1 if cur_page-1 >= 1 else 1
                embed = self.get_page(users, page, role)
            elif reaction.emoji == self.stop:
                await self.reaction_menu_timeout(reaction.message, wait=False)
                return
            else:
                return
            await reaction.message.edit(embed=embed)
            


    async def reaction_menu_timeout(self, message: discord.Message, wait: bool = True):
        if wait:
            await asyncio.sleep(300)
        await message.clear_reactions()
        try:
            del self.whois_messages[message.id]
        except KeyError:
            pass

    async def prepare_reaction_menu(self, message: discord.Message):
        for emoji in self.emojis:
            await message.add_reaction(emoji)
        self.client.loop.create_task(self.reaction_menu_timeout(message))

    def get_page(self, users, page, role):
        sumpages = math.ceil(len(users)/20)
        pagestart = (page * 20)-20
        pageend = pagestart + 19
        desctext = f'({str(len(users))} in total)\n'
        for i in range(pagestart, pageend):
            try:
                desctext += users[i].mention + '\n'
            except IndexError:
                break
        embed = utils.createEmbed(title=f'__Users with the role `{role}`:__', description=desctext, colour='iron')
        embed.set_footer(text=f'Page {page}/{sumpages}')
        return embed

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
        users = role.members
        users.sort(key=lambda x: x.name)

                 
        embed = self.get_page(users, page, role)
        msg = await ctx.send(embed=embed)
        await self.prepare_reaction_menu(msg)
        self.whois_messages[msg.id] = {'users': users, 'page': page, 'role': role}


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
        brief='Get the link for the bot\'s commands summary.',
        description='This command retrieves you the link to the command summary of the Iron Justice.',
        usage='?commands'
    )
    async def cmnds(self, ctx):
        embed = utils.createEmbed(author=ctx.author, description='You can view the command documentation of the Iron Justice right [here](https://gist.github.com/Cradac/4544f0cbe9456a637c0d3a85061bda78).', colour='iron')
        await ctx.send(embed=embed)

    @commands.command(
        brief='Get the GitHub repository.',
        description='Get the GitHub Link of the Iron Justice discord bot and stay up to date!',
        usage='?github'
    )
    async def github(self, ctx):
        embed = utils.createEmbed(author=ctx.author, description='Visit the Iron Justice on [GitHub](https://github.com/Cradac/Iron-Justice) and check out the latest additions. Please Star the repository!', colour='iron')
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