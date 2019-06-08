import discord
import asyncio
from utils.guilds import Guilds
from discord.ext import commands
from datetime import datetime
import sqlite3
from sqlite3 import Error 
god = 116222914327478274
if_servers=[479300072077787160,421650482176589835] #ironfleet servers
rogueID = 455901088164478976
welcome = 479301249351548928 #ironfleet welcome channel
db_file = "JusticeDB.db"

#connecting to db
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None

def isGod():
	def godcheck(ctx):
		if ctx.message.author.id == god:
			return True
		return False
	return commands.check(godcheck)

def isAdmin():
	def admincheck(ctx):
		if ctx.author == ctx.message.guild.owner or ctx.author.id == god:
			return True
		for role in ctx.message.author.roles:
			if role.permissions.administrator:
				return True
		return False
	return commands.check(admincheck)

def isMod():
	def moderatorcheck(ctx):
		for role in ctx.message.author.roles:
			if role.permissions.kick_members:
				return True
		return False
	return commands.check(moderatorcheck)

def matchlfcchannel():
	def does_it_match(ctx):
		lfc_channels =  ctx.bot.dictGuilds[ctx.message.guild.id].lfc_channels
		if ctx.message.channel.id in lfc_channels or not lfc_channels:
			return True
		return False
	return commands.check(does_it_match)
	
def matchprofilechannel():
	def does_it_match(ctx):
		profile_channels = ctx.bot.dictGuilds[ctx.message.guild.id].profile_channels
		if ctx.message.channel.id in profile_channels or not profile_channels:
			return True
		return False
	return commands.check(does_it_match)

def isIronFleet():
    def inServer(ctx):
        if ctx.message.guild.id in if_servers:
            return True
        return False
    return commands.check(inServer)

def isRogueLegends():
    def inServer(ctx):
        if ctx.guild.id == rogueID or ctx.guild.id == 421650482176589835:
            return True
        return False
    return commands.check(inServer)

def isntRogueLegends():
    def inServer(ctx):
        if ctx.guild.id != rogueID:
            return True
        return False
    return commands.check(inServer)

async def memberSearch(ctx, client, name):
		results = []
		resultsdict = {}
		if len(ctx.message.mentions) > 0:
			return ctx.message.mentions[0]
		for member in ctx.guild.members:
			if name.lower() in member.name.lower() or name.lower() in member.display_name.lower():
				results.append(member)
		if len(results) == 0:
			await ctx.send("No member found by that name.")
			return None
		if len(results) == 1:
			return results[0]
		if len(results) > 1:
			def message_check(msg):
				return msg.author == ctx.author
			i = 1
			text = "Which Member?\n"
			for member in results:
				text += "`{}`: `{}`\n".format(i, member)
				resultsdict[i] = member
				i += 1
			await ctx.send(text)
			msg = await client.wait_for('message', timeout=60.0, check=message_check)
			try:
				return resultsdict[int(msg.content)]
			except KeyError:
				await ctx.send("Cancelled command.")
				return None

async def roleSearch(ctx, client, name):
	results = []
	resultsdict = {}
	if len(ctx.message.role_mentions) > 0:
		return ctx.message.role_mentions[0]
	for role in ctx.guild.roles:
		if name.lower() in role.name.lower():
			results.append(role)
	if len(results) == 0:
		await ctx.send("No role found by that name.")
		return None
	if len(results) == 1:
		return results[0]
	if len(results) > 1:
		def message_check(msg):
			return msg.author == ctx.author
		i = 1
		text = "Which role?\n"
		for role in results:
			text += "`{}`: `{}`\n".format(i, role)
			resultsdict[i] = role
			i += 1
		await ctx.send(text)
		msg = await client.wait_for('message', timeout=60.0, check=message_check)
		try:
			return resultsdict[int(msg.content)]
		except KeyError:
			await ctx.send("Cancelled command.")
			return None

def createEmbed(*, title: str = '', description: str = '', colour = None, author: discord.Member = None, guild: discord.Guild = None):
	if colour == 'iron':
		colour = 0xffd700
	elif colour == 'rogue':
		colour = 0x7d0a00
	embed = discord.Embed(
			title = title,
			description=description,
			timestamp = datetime.utcnow()
		)
	if colour:
		embed = discord.Embed(
		title=title,
		description=description,
		timestamp=datetime.utcnow(),
		colour=colour
	)
	if author:
		embed.set_author(name=author, icon_url=author.avatar_url)
	if guild:
		embed.set_footer(text=guild.name, icon_url=guild.icon_url_as(format='png', size=128))
		embed.set_thumbnail(url=guild.icon_url_as(format='png', size=512))

	return embed