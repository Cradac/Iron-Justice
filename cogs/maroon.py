import discord, asyncio, cogs.guilds, math
from discord.ext import commands
from datetime import datetime
from cogs.utils import isAdmin, isMod, isGod, roleSearch, god, memberSearch, create_connection, db_file, isntRogueLegends, if_servers
from operator import itemgetter

#simply adds a message with author id, message id and timestamp into DB


class Maroon(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    def addMessage(self, message:discord.Message):
        conn = create_connection(db_file)
        with conn:
            cur = conn.cursor()
            cur.execute('''INSERT INTO messages VALUES (?,?,?,?)''', (message.author.id, message.created_at,message.id,message.guild.id))
            conn.commit()

    def purge_DB(self):
        conn = create_connection(db_file)
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT datetime as "datetime [timestamp]", messageid FROM messages')
            rows = cur.fetchall()
            for row in rows:
                try: 
                    date = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    date = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')                
                if abs((date-datetime.utcnow()).days) > 30:
                    cur.execute('DELETE FROM messages WHERE messageid={}'.format(row[1]))
                    #delete all messages older than 30 days from DB

            cur.execute('SELECT DISTINCT guildid FROM messages')
            rows = cur.fetchall()
            for row in rows:
                check_guild = self.client.get_guild(row[0])
                if check_guild is None:
                    cur.execute('DELETE FROM messages WHERE guildid={}'.format(row[0]))
                    #delete all messages from guilds the client is no longer part of
            cur.execute('SELECT DISTINCT guildid, authorid FROM messages')
            rows = cur.fetchall()
            for row in rows:
                check_guild = self.client.get_guild(row[0])
                check_member = check_guild.get_member(row[1])
                if check_member is None:
                    cur.execute('DELETE FROM messages WHERE authorid={} and guildid={}'.format(row[1], row[0]))
                    #delete all messages from members who are no longer part of that guild   
            conn.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot and not message.content.startswith(('?', '!')):
            if type(message.channel) is discord.DMChannel:
                print('{}: {}'.format(message.author,message.content))
                return
            elif not type(message.channel) is discord.DMChannel and message.guild.id not in if_servers:     #only record messages in our server
                return
            self.addMessage(message)
            
    @commands.Cog.listener()
    @isntRogueLegends()
    async def on_member_remove(self, member):
        conn = create_connection(db_file)
        with conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM messages WHERE authorid={} and guildid={}'.format(member.id, member.guild.id))
            conn.commit()


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
            cur.execute('SELECT datetime as "datetime [timestamp]" FROM messages WHERE authorid={} AND guildid={} ORDER BY datetime DESC LIMIT 1'.format(member.id, member.guild.id))
            row = cur.fetchone()
            last_message = row[0]
            try:
                last_message = datetime.strptime(last_message, '%Y-%m-%d %H:%M:%S')
            except:
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
            embed.add_field(name="__amount of messages (last 30 days)__", value=amnt, inline=False)
            await ctx.send(embed=embed)

    @isAdmin()
    @isntRogueLegends()
    @commands.command(aliases=["maroon"], brief="Manually invoke the checking routine.", hidden=True)
    async def marooning(self, ctx, role:str=None):
        await ctx.send("**__Checking for inactivity now... This might take a while.__**")
        list_to_check = None
        if role is None:
            list_to_check = ctx.guild.members
        else:
            role = await roleSearch(ctx, self.client, role)
            if role is None:
                return
            list_to_check = role.members
        #PURGING UNUSABLE MESSAGES FROM DB
        self.purge_DB()

        conn = create_connection(db_file)
        with conn:
            cur = conn.cursor()

            #select inactive members
            memberlist = []
            for member in list_to_check:
                if not member.bot:
                    cur.execute('SELECT datetime as "datetime [timestamp]", messageid FROM messages WHERE authorid={} ORDER BY datetime DESC LIMIT 1'.format(member.id))
                    row = cur.fetchone()
                    #Check if each of the members has been inactive for this much
                    comparedate = None
                    joindate = member.joined_at
                    if  row is not None and row[0] is not None:
                        comparedate = row[0] #pick last message as date
                        try: 
                            comparedate = datetime.strptime(comparedate, '%Y-%m-%d %H:%M:%S.%f')
                        except ValueError:
                            comparedate = datetime.strptime(comparedate, '%Y-%m-%d %H:%M:%S')
                    if row is None or row[0] is None:
                        comparedate = joindate #pick the date of the guy joining
                    if comparedate is None:
                        await ctx.send("Something's fucked.")
                    days_gone = abs((comparedate-datetime.utcnow()).days)
                    if days_gone > 30:
                        days_gone = 30
                    if days_gone >= 14: 
                        cur.execute("SELECT Count(*) FROM messages WHERE authorid={} AND guildid={}".format(member.id, ctx.guild.id))
                        row = cur.fetchone()
                        amnt = row[0]
                        member_stats = {'member': member, 'days_gone': days_gone, 'amount_messages': amnt}
                        memberlist.append(member_stats)

            memberlist.sort(key=itemgetter('days_gone'))
            sumpages=math.ceil(len(memberlist)/20)
            for page in range(0, sumpages):
                desctext = ""
                try:
                    for i in range(page*20, page*20+19):
                        current_member = memberlist[i]
                        desctext += "- {} has written {} messages. Last one (over) {} days ago.\n".format(current_member['member'].mention, current_member['amount_messages'], current_member['days_gone'])
                except IndexError:
                    pass
                await ctx.send(desctext)
                await asyncio.sleep(5)

            await ctx.send("**__Finished checking.__**")

    @isAdmin()
    @isntRogueLegends()
    @commands.command(brief="Clean the database of old messages.", hidden=True)
    async def purge(self, ctx):
        await ctx.send('**__Purging the Database of old entries now... This might take a bit.__**')
        self.purge_DB()
        await ctx.send('**__Finished purging__**')
def setup(client):
    client.add_cog(Maroon(client))    