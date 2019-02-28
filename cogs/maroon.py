import discord, asyncio, cogs.guilds, math
from discord.ext import commands
from datetime import datetime
from cogs.checks import isAdmin, isMod, isGod, roleSearch, god, memberSearch, create_connection, db_file, isntRogueLegends
from operator import itemgetter

#simply adds a message with author id, message id and timestamp into DB
def addMessage(message:discord.Message):
	conn = create_connection(db_file)
	with conn:
		cur = conn.cursor()
		cur.execute('''INSERT INTO messages VALUES (?,?,?,?)''', (message.author.id, message.created_at,message.id,message.guild.id))
		conn.commit()

class Maroon:
    def __init__(self, client):
        self.client = client
    @isntRogueLegends()
    async def on_message(self, message):
        if not message.author.bot and not message.content.startswith(('?', '!')):
            addMessage(message)

    @isntRogueLegends()
    @isMod()
    @commands.command(aliases=["userinfo", "info"], name="user-info", brief="Show a players activity.", description=">>>Play Activity\nThis command shows a players activity in chat on this server. The Justice records all messages within the last 90 days.\n")
    async def user_info(self, ctx, *member):
        member = await memberSearch(ctx, self.client, " ".join(member))
        if member is None:
            return
        conn = create_connection(db_file)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT Count(*) FROM messages WHERE authorid={} AND guildid={}".format(member.id, member.guild.id))
            row = cur.fetchone()
            amnt = row[0] 
            if amnt == 0:
                await ctx.send("`{}` hasn't sent any messages yet!".format(member))
                return
                #helper if no messages yet
            #gets amount of messages in the last 90 days
            cur.execute('SELECT datetime "[timestamp]" FROM messages WHERE authorid={} AND guildid={} ORDER BY datetime DESC LIMIT 1'.format(member.id, member.guild.id))
            row = cur.fetchone()
            last_message = row[0]
            last_message = datetime.strptime(last_message, '%Y-%m-%d %H:%M:%S.%f')
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

    @isAdmin()
    @isntRogueLegends()
    @commands.command(aliases=["maroon"], brief="Manually invoke the checking routine.", hidden=True)
    async def marooning(self, ctx):
        conn = create_connection(db_file)
        await ctx.send("**__Checking for inactivity now... This might take a while.__**")
        with conn:
            cur = conn.cursor()
            memberlist = []
            for member in ctx.guild.members:
                if not member.bot:
                    cur.execute('SELECT datetime "[timestamp]", messageid FROM messages WHERE authorid={} ORDER BY datetime DESC LIMIT 1'.format(member.id))
                    row = cur.fetchone()
                    #Check if each of the members has been inactive for this much
                    comparedate = None
                    hourzero = datetime(2019, 3, 1)
                    joindate = member.joined_at
                    if  row is not None and row[0] is not None:
                        comparedate = row[0] #pick last message as date
                        comparedate = datetime.strptime(comparedate, '%Y-%m-%d %H:%M:%S.%f')
                    elif hourzero > joindate:
                        comparedate = hourzero #pick bot starting as date
                    else:
                        comparedate = joindate #pick the date of the guy joining

                    days_gone = abs((comparedate-datetime.utcnow()).days)
                    if days_gone >= 14: 
                        cur.execute("SELECT Count(*) FROM messages WHERE authorid={} AND guildid={}".format(member.id, ctx.guild.id))
                        row = cur.fetchone()
                        amnt = row[0]
                        member_stats = {'member': member, 'days_gone': days_gone, 'amount_messages': amnt}
                        memberlist.append(member_stats)

            cur.execute('SELECT datetime "[timestamp]", messageid FROM messages')
            rows = cur.fetchall()
            for row in rows:
                date = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')
                if abs((date-datetime.utcnow()).days) > 90:
                    cur.execute('DELETE * FROM messages WHERE messageid={} AND guildid={}'.format(row[1], ctx.guild.id))
                    #delete all messages older than 90 days from DB
            conn.commit()
            memberlist.sort(key=itemgetter('days_gone'))
            sumpages=math.ceil(len(memberlist)/20)
            for page in range(0, sumpages-1):
                title = "Member inactivity"
                desctext = ""
                for i in range(page*20, page*20+19):
                    current_member = memberlist[i]
                    desctext += "- {} has written {} messages. Last one {} days ago.\n".format(current_member['member'], current_member['amount_messages'], current_member['days_gone'])
                emb=discord.Embed(color=0xffd700, timestamp=datetime.datetime.utcnow(), title=title, description=desctext)
                emb.set_footer(text="Page {}/{}".format(page, sumpages))
                await ctx.send(embed=emb)

            await ctx.send("**__Finished checking.__**")

def setup(client):
    client.add_cog(Maroon(client))    