#The Iron Fleet's Iron Justice Bot
#Primary intention: Supporting the Iron Fleet's Discord server.
#Secondary intention: gimicks like the profile System
#Author Maxe aka. Cradac

#Version: 2.1 rewrite

import discord
from discord.ext.commands import Bot
from discord.ext import commands
from discord import HTTPException
import asyncio
import sys
import sqlite3
from sqlite3 import Error 
import datetime
import random
import traceback
from cogs.guilds import Guilds
from cogs.member import Members
from cogs.helper import isMod, isAdmin, isGod
from cogs.helper import create_connection

_version = '2.4.1'

print(sys.version)
print(discord.__version__)
print('bot version: {}'.format(_version))


Client = discord.Client()
client = commands.Bot(command_prefix = ["?"], case_insensitive=True, description="This is the Iron Fleet's own bot THE IRON JUSTICE V{} rewrite. For questions please contact Cradac aka. Max.\n#beMoreIron".format(_version))
if len(sys.argv) == 1:
	bot_token = "NDIxMjY4MjA4MzM1NTg1Mjkw.DYK4Mw.aBwGz447sS0NNB5V8yD6Yfi3-Ko"
else:
	bot_token = sys.argv[1]
	sys.stdout = open(datetime.datetime.now().strftime('logs/discord_log_%Y_%m_%d_%H_%M_%S.log'), 'w+')
db_file = "JusticeDB.db"

client.dictGuilds = {}
serverids = [] 

extensions = ["cogs.lfc", "cogs.profile", "cogs.ironfleet", "cogs.misc", "cogs.reactionrole", "cogs.auto_voice"]



##########################################################################################################################################


@client.event
async def on_ready():
	print("Bot is ready!")
	game = discord.Game("the Iron Price | ?help")
	await client.change_presence(status=discord.Status.online, activity=game)
	print("Logged in as: " + client.user.name)
	print("Bot ID: " + str(client.user.id))
	for guild in client.guilds:
		print ("Connected to server: {}".format(guild))
	print("------")
	conn = create_connection(db_file)
	with conn:
		cur = conn.cursor()
		try:
			cur.execute("SELECT guild_id FROM guilds;")
			guilds = cur.fetchall()
			guildIDlist = []
			for guild in guilds:
				guildIDlist.append(int(guild[0]))
			for guild in client.guilds:
				if guild.id not in guildIDlist:
					cur.execute("INSERT INTO guilds VALUES (?,?,'False, False',NULL,NULL)", (guild.id, guild.name))
					conn.commit()
			cur.execute("SELECT * FROM guilds")
			rows = cur.fetchall()
			for row in rows:
				guild_id = int(row[0])
				guild_name = row[1]
				lfc_channels = []
				profile_channels = []
				if row[2] is not None:
					enabled = row[2].split(",")
					enabled_dict = {"lfc" : enabled[0], "profile" : enabled[1]}
				else:
					enabled_dict = {}
				if row[3] is not None and row[3] is not '':
					for el in row[3].split(","):
						lfc_channels.append(int(el))
				if row[4] is not None and row[4] is not '':
					for el in row[4].split(","):
						profile_channels.append(int(el))
				client.dictGuilds[guild_id]=Guilds(guild_name, guild_id, enabled_dict, lfc_channels, profile_channels)
			print("Successfully imported all Guilds.")
		except:
			print("Fatal error or some shit.")
		#for guildID in client.dictGuilds.keys():
		#	print(guildID)
		#for guild in client.dictGuilds.values():
		#	print(guild.guild_name, guild.guild_id, guild.enabled, guild.lfc_channels, guild.profile_channels)

@client.event
async def on_message(message):
	if type(message.channel) is discord.DMChannel:
		return
	guild = message.guild
	log_channel = discord.utils.get(guild.channels, name="message-log")
	if log_channel is None:
		await client.process_commands(message)
		return
	if not message.author.bot:
		embed=discord.Embed(
			color=0xffd700,
			timestamp=datetime.datetime.utcnow(),
			description="in {}:\n{}".format(message.channel.mention, message.content)
		)
		embed.set_author(name=message.author, icon_url=message.author.avatar_url)
		embed.set_footer(text=message.author.id)
		if len(message.attachments) > 0:
			embed.set_image(url = message.attachments[0].url)
		await log_channel.send(embed=embed)
		await client.process_commands(message)

@client.event
async def on_message_edit(before, after):
	await client.process_commands(after)

@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CheckFailure) or isinstance(error, commands.CommandNotFound):
		pass
	else:
		try:
			raise error
		except Exception as error:
			tb = traceback.format_exc()
			print(error, tb)

@client.event
async def on_guild_join(guild):
	await guild.owner.send("Hey! I am the Iron Fleet's Iron Justice Bot, specifically for Discord Servers of *Sea of Thieves* Fleets. If you have any questions write a message `Cradac | Max#2614` or type `?help [command|module]`.\nTo set up the bot for your server type `?setup` (best in an admin-exclusive room) and go through the installation wizard. \n**Please ensure the bot has sufficient rights, at least for the setup!**\nYou can set up a message logger by createing a channel called `#message-log`. The bot must be able to see and write in it. This channels should be at least Moderator exclusive!\nEnjoy!")
	conn = create_connection(db_file)
	await guild.create_role(name="lfc", mentionable=True, colour=discord.Color(0xFFFFFF))
	with conn:
		cur = conn.cursor()
		cur.execute("INSERT INTO guilds VALUES (?,?,'False,False',NULL,NULL)", (guild.id, guild.name))

##########################################################################################################################################

@isAdmin()
@client.command(hidden=True, brief="This command takes you through a small install wizard for this bot.", description="This command takes you through a small install wizard for this bot.")
async def setup(ctx):
	lfc_channels=[]
	profile_channels=[]
	lfc_channels_para = ""
	profile_channels_para = ""
	lfc_enabled = True
	profile_enabled = True
	
	def reaction_check(reaction, user):
		return user == ctx.message.author and str(reaction.emoji) in ["✅", "❌"]

	def message_check(msg):
		return msg.author == ctx.author and msg.content

	

	await ctx.send("Starting the setup of this bot now. **You can stop at any point by typing `cancel`.**")
	msg = await ctx.send("Do you want to enable the 'Looking For Crew'-Helper?\n **Please react below.**")
	await msg.add_reaction("✅")
	await msg.add_reaction("❌")
	try:
		reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=reaction_check)
	except asyncio.TimeoutError:
		await ctx.send("Cancelled the Setup.")
	
	if str(reaction.emoji) == "✅":
		lfc_enabled = True
		await ctx.send("LFC Module is enabled.")
	elif str(reaction.emoji) == "❌":
		lfc_enabled = False
		await ctx.send("LFC Module is disabled.")
	else:
		await ctx.send("Canceled Setup.")
		return

	if lfc_enabled:
		await ctx.send("In which channels should the LFC commands be usable? **Please tag one or multiple channels you want it enabled in.\nType `all` to have it enabled in all channels.**")
		msg = await client.wait_for('message', timeout=60.0, check=message_check)
		if msg.content.lower() == "all":
			pass
		elif msg.content.lower() == "cancel":
			await ctx.send("Canceled Setup.")
			return
		for ch in msg.channel_mentions:
			lfc_channels.append(ch.id)
		for val in lfc_channels:
			lfc_channels_para += str(val) + ','
		lfc_channels_para = lfc_channels_para[:-1]
	
	msg = await ctx.send("Do you want to enable the 'Profile'-Functions?\n **Please react below.**")
	await msg.add_reaction("✅")
	await msg.add_reaction("❌")
	try:
		reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=reaction_check)
	except asyncio.TimeoutError:
		await ctx.send("Cancelled the Setup.")

	if str(reaction.emoji) == "✅":
		profile_enabled = True
		await ctx.send("Profile Module is enabled.")
	elif str(reaction.emoji) == "❌":
		profile_enabled = False
		await ctx.send("Profile Module is disabled.")
	else:
		await ctx.send("Canceled Setup.")
		return

	if profile_enabled:
		await ctx.send("In which channels should the Profile commands be usable?** Please tag one or multiple channels you want it enabled in.\nType `all` to have it enabled in all channels.**")
		msg = await client.wait_for('message', check=message_check)
		if msg.content.lower() == "all":
			pass
		elif msg.content.lower() == "cancel":
			await ctx.send("Canceled Setup.")
			return
		for ch in msg.channel_mentions:
			profile_channels.append(ch.id)

		for val in profile_channels:
			profile_channels_para += str(val) + ','
		profile_channels_para = profile_channels_para[:-1]
	
	enabled = {"lfc" : lfc_enabled, "profile" : profile_enabled}
	guild_id = ctx.message.guild.id
	guild_name = ctx.message.guild.name

	enabled_para = ""
	for val in enabled.values():
		enabled_para += str(val) + ','
	enabled_para = enabled_para[:-1]

	conn = create_connection(db_file)
	with conn:
		cur = conn.cursor()
		cur.execute("SELECT guild_id FROM guilds;")
		guilds = cur.fetchall()
		guildIDlist = []
		for guild in guilds:
			guildIDlist.append(int(guild[0]))
		if ctx.message.guild.id not in guildIDlist:
			guild = ctx.message.guild
			cur.execute("INSERT INTO guilds VALUES (?,?,NULL,NULL,NULL)", (guild.id, guild.name))
		try:
			print((guild_id, guild_name, enabled_para, lfc_channels_para, profile_channels_para))
			cur.execute("UPDATE guilds SET guild_id='{}', guild_name='{}', enabled='{}', lfc_channels='{}', profile_channels='{}' WHERE guild_id='{}';".format(guild_id, guild_name, enabled_para, lfc_channels_para, profile_channels_para, guild_id))
			conn.commit()
			client.dictGuilds[guild_id]=Guilds(guild_name, guild_id, enabled, lfc_channels, profile_channels)
			await ctx.send("Setup complete!")
		except:
		 	await ctx.send("Something went terribly wrong.")

@client.command(hidden=True, brief="Pong!")
async def ping(ctx):
	await ctx.send('Pong! `({} ms)`'.format(round(client.latency, 2)))

@client.command(hidden=True, brief="Version Info")
async def version(ctx):
	await ctx.send('\
bot version: `{}`\n\
discord.py version: `{}`\n\
system info: `{}`\n\
		'.format(_version, discord.__version__, sys.version))

##########################################################################################################################################

@isGod()
@client.command(hidden=True)
async def kill(ctx):
	print("Bot shutting down...")
	await client.close()
@isGod()
@client.command(hidden=True)
async def load(ctx, extension_name : str):
	try:
		extension_name = "cogs.{}".format(extension_name)
		client.load_extension(extension_name)
	except (AttributeError, ImportError) as e:
		print("{}: {}".format(type(e).__name__, str(e)))
		return
	print("'{}' loaded.".format(extension_name))

@isGod()
@client.command(hidden=True)
async def unload(ctx, extension_name : str):
	extension_name = "cogs.{}".format(extension_name)
	client.unload_extension(extension_name)
	print("'{}' unloaded.".format(extension_name))

@isGod()
@client.command(hidden=True)
async def reload(ctx, extension_name : str):
	try:
		extension_name = "cogs.{}".format(extension_name)
		client.unload_extension(extension_name)
		client.load_extension(extension_name)
	except (AttributeError, ImportError) as e:
		print("{}: {}".format(type(e).__name__, str(e)))
		return
	print("'{}' reloaded.".format(extension_name))

if __name__ == "__main__":
	for extension in extensions:
		try:
			client.load_extension(extension)
			print('Loaded Extension {} on boot-up.'.format(extension))
		except Exception as e:
			exc = '{}: {}'.format(type(e).__name__, e)
			print('Failed to load extension {}\n{}'.format(extension, exc))

client.run(bot_token)

