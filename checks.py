import discord
from guilds import Guilds
from discord.ext import commands
import sqlite3
from sqlite3 import Error 
god = "116222914327478274"
crimson_id = "231187226288062464"
servers=["479300072077787160","421650482176589835"]
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

def isCrimson():
	def crimsoncheck(ctx):
		if ctx.message.author.id == crimson_id:
			return True
		return False
	return commands.check(crimsoncheck)


def matchlfcchannel():
	def does_it_match(ctx):
		if ctx.message.channel.id in ctx.bot.dictGuilds[ctx.message.server.id].lfc_channels:
			return True
		return False
	return commands.check(does_it_match)
	
def matchprofilechannel():
	def does_it_match(ctx):
		if ctx.message.channel.id in ctx.bot.dictGuilds[ctx.message.server.id].profile_channels:
			return True
		return False
	return commands.check(does_it_match)


def isIronFleet():
    def inServer(ctx):
        if ctx.message.server.id in servers:
            return True
        return False
    return commands.check(inServer)
