import discord
from discord.ext import commands
from datetime import datetime
from utils import utils
from operator import itemgetter
from utils.storage import Storage
import asyncio, math, typing

#simply adds a message with author id, message id and timestamp into DB

active_fleets = set()

class Activity_Logging(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.Storage = Storage()
    


    @commands.Cog.listener()
    async def on_ready(self):
        global active_fleets
        active_fleets = self.Storage.get_activity_logging_enabled_guilds(self.client)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot and not message.content.startswith(('?', '!', '.')):
            if type(message.channel) is discord.DMChannel:
                print('{}: {}'.format(message.author,message.content))
                return
            elif message.guild in active_fleets:
                self.Storage.add_message(message)
            
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        self.Storage.user_leave_guild(member)


    @utils.isMod()
    @commands.command(
        aliases=['userinfo'],
        name='user-info', 
        brief='Show a players activity.',
        description='This command shows a players activity in chat on this server. The Iron Justice records all messages within the last 30 days.'
    )
    async def user_info(self, ctx, *, member):
        member = await utils.memberSearch(ctx, self.client, member)
        if not member:
            return

        info = self.Storage.get_user_activity(member)

        embed = utils.createEmbed(author=member, colour='iron', guild=ctx.guild)
        embed.set_footer(text="Activity Info", icon_url=ctx.guild.icon_url_as(format='png', size=128))
        timestamp_str = info['timestamp'].strftime(self.Storage.datetime_scheme)
        days_gone = (datetime.utcnow()-info['timestamp']).days
        embed.add_field(name='__joined guild__', value=member.joined_at.strftime('%d %b %Y'), inline=False)
        embed.add_field(name='__last message (UTC TIME)__', value=f'{timestamp_str} ({days_gone} days ago)', inline=False)
        embed.add_field(name='__amount of messages (last 30 days)__', value=info['amnt'], inline=False)
        await ctx.send(embed=embed)

    @utils.isAdmin()
    @commands.command(
        brief='Manually invoke the marooning routine.',
        usage='?maroon [days gone = 14] [role]',
        hidden=True
    )
    async def maroon(self, ctx, compare_days: typing.Optional[int] = 14, role: str = None):
        await ctx.send("**__Checking for inactivity now... This might take a while.__**")
        list_to_check = (await utils.roleSearch(ctx, self.client, role).members if role else ctx.guild.members)
        if not list_to_check:
            return

        # Cleaning up DB
        self.Storage.cleanup_messages(self.client.guilds)

        # getting inactive members
        info_list = list()
        for member in list_to_check:
            if not member.bot:
                m_info = self.Storage.get_user_activity(member)
                comparedate = m_info['timestamp'] or member.joined_at
                m_info['days_gone'] = (datetime.utcnow() - comparedate).days()
                if m_info['days_gone'] > compare_days:
                    info_list.append(m_info)
        
        #output found members
        info_list.sort(key=itemgetter('days_gone'))
        sumpages = math.ceil(len(info_list)/20)
        for page in range(0, sumpages):
            text = ''
            try:
                for i in range(page*20, page*20+19):
                    current_member = info_list[i]
                    text += f'- {current_member["member"].mention} has written {current_member["amnt"]} messages. Last one (over) {current_member["days_gone"]} days ago.\n'
            except IndexError:
                pass
            await ctx.send(text)

        await ctx.send("**__Finished checking.__**")

    @commands.is_owner()
    @commands.command(
        name='clean-db',
        brief='Clean the database of old messages.',
        hidden=True
    )
    async def clean_db(self, ctx):
        await ctx.send('**Cleaning the Database of old entries now... This might take a bit.__**')
        self.Storage.cleanup_messages(self.client.guilds)
        await ctx.send('**__Finished purging__**')


def setup(client):
    client.add_cog(Activity_Logging(client))    