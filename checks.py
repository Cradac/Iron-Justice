import discord
from guilds import Guilds
from discord.ext import commands
god = "116222914327478274"



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



# def isMod(usr):
# 	for role in usr.roles:
# 		if role.permissions.kick_members:
# 			return True
# 	return False

# def isAdmin(usr):
# 	for role in usr.roles:
# 		if role.permissions.administrator:
# 			return True
# 	return False

# def isGod(usr):
# 	if usr.id == god:
# 		return True
# 	return False