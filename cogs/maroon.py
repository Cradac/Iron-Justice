import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import cogs.guilds
from cogs.checks import isAdmin, isMod, isGod, roleSearch, god, memberSearch, create_connection, db_file

#simply adds a message with author id, message id and timestamp into DB
def addMessage(message:discord.Message):
	conn = create_connection(db_file)
	with conn:
		cur = conn.cursor()
		cur.execute('''INSERT INTO messages VALUES (?,?,?)''', (message.author.id, message.created_at,message.id,))
		conn.commit()

class Maroon:
    def __init__(self, client):
        self.client = client

    async def on_message(self, message):
        if not message.author.bot:
            addMessage(message)
        await self.client.process_commands(message)

    @isGod()
    @commands.command(hidden=True)
    async def create_table(self, ctx):
        conn = create_connection(db_file)
        with conn:
            cur = conn.cursor()
            cur.execute('CREATE TABLE messages (\
                        authorid  INTEGER,\
                        datetime  TIMESTAMP,\
                        messageid INTEGER\
                        );')

    @isMod()
    @commands.command(aliases=["userinfo", "info"], name="user-info", brief="Show a players activity.", description=">>>Play Activity\nThis command shows a players activity in chat on this server. The Justice records all messages within the last 90 days.\n")
    async def user_info(self, ctx, *member):
        member = await memberSearch(ctx, self.client, " ".join(member))
        if member is None:
            return
        conn = create_connection(db_file)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT Count(*) FROM messages WHERE authorid={}".format(member.id))
            row = cur.fetchone()
            amnt = row[0] 
            if amnt == 0:
                await ctx.send("`{}` hasn't sent any messages yet!".format(member))
                return
                #helper if no messages yet
            #gets amount of messages in the last 90 days
            cur.execute('SELECT datetime "[timestamp]" FROM messages WHERE authorid={} ORDER BY datetime DESC LIMIT 1'.format(member.id))
            row = cur.fetchone()
            last_message = row[0]
            last_message_formatted = last_message.strftime("%b %d %Y - %H:%M:%S")
            #formatting timestamp into readable format
            embed = discord.Embed(colour=discord.Colour(0x7d0a00), timestamp=datetime.utcnow())
            embed.set_author(name=member.name,icon_url=member.avatar_url)
            guild = ctx.message.guild
            icon = guild.icon_url_as(format='png', size=1024)
            embed.set_footer(text="Activity Info", icon_url=icon)
            days_gone=abs((last_message-datetime.utcnow()).days)
            #calculating days gone
            last_message_text="{} ({} days ago)".format(last_message_formatted, days_gone)
            embed.add_field(name="__last message (UTC time)__", value=last_message_text, inline=False) 
            embed.add_field(name="__amount of messages (last 90 days)__", value=amnt, inline=False)
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Maroon(client))    