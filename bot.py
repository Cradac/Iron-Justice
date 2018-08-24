#The Iron Fleet's Iron Justice Bot
#Primary intention: Supporting the Iron Fleet's Discord server.
#Secondary intention: gimicks like the profile System
#Author Maxe aka. Cradac

#Version: 2.0 SNAPSHOT

import discord
from discord.ext.commands import Bot
from discord.ext import commands
from discord import HTTPException
import asyncio
#import re
import sys
import sqlite3
from sqlite3 import Error 
import datetime
import random
import traceback
from guilds import Guilds
from member import Members
from checks import isMod, isAdmin, isGod
from ironfleet import servers


Client = discord.Client()
client = commands.Bot(command_prefix = ["?", "!"], description="This is the Iron Fleet's own bot THE IRON JUSTICE V2.0. For questions please contact Cradac aka. Max.\n#beMoreIron")
#bot_token = sys.argv[1]
bot_token = "NDIxMjY4MjA4MzM1NTg1Mjkw.DYK4Mw.aBwGz447sS0NNB5V8yD6Yfi3-Ko"
god = "116222914327478274"
welcome = "479301249351548928"
db_file = "JusticeDB.db"

client.dictGuilds = {}

extensions = ["lfc", "profile", "ironfleet"]

#connecting to db
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None

##########################################################################################################################################


@client.event
async def on_ready():
	print("Bot is ready!")
	await client.change_presence(game=discord.Game(name="the Iron Price"))
	print("Logged in as: " + client.user.name)
	print("Bot ID: "+client.user.id)
	for server in client.servers:
		print ("Connected to server: {}".format(server))
	print("------")
	conn = create_connection(db_file)
	with conn:
		cur = conn.cursor()
		try:
			cur.execute("SELECT * FROM guilds")
			rows = cur.fetchall()
			for row in rows:
				guild_id = row[0]
				guild_name = row[1]
				lfc_channels = []
				profile_channels = []
				enabled = row[2].split(",")
				enabled_dict = {"lfc" : enabled[0], "profile" : enabled[1]}
				for el in row[3].split(","):
					lfc_channels.append(el)
				for el in row[4].split(","):
					profile_channels.append(el)
				client.dictGuilds[guild_id]=Guilds(guild_name, guild_id, enabled_dict, lfc_channels, profile_channels)
			print("Successfully imported all Guilds.")
		except:
			print("Fatal error or some shit.")
		# for guildID in dictGuilds.keys():
		# 	print(guildID)
		# for guild in dictGuilds.values():
		# 	print(guild.guild_name, guild.guild_id, guild.enabled, guild.lfc_channels, guild.profile_channels)

@client.event
async def on_message(message):
	server=message.server
	log_channel = discord.utils.get(server.channels, name="message-log")
	if message.author.id != client.user.id and not message.author.bot:
		await client.send_message(log_channel, "{}`{}` just said in {}: *'{}'*".format(message.author.name, message.author.id, message.channel.mention, message.clean_content.replace("@","")))
		for att in message.attachments:
			await client.send_message(log_channel, att.get("url"))
		#command=message.content.lower().split()[0]
		#message.content=command+message.content[len(command):]
		await client.process_commands(message)

@client.event
async def on_command_error(ctx, error):
    if not isinstance(error, commands.errors.CheckFailure) or not isinstance(error, commands.errors.CommandNotFound):
        try:
            raise error
        except Exception as error:
            tb = traceback.format_exc()
            print(error, tb)
    else:
        pass

@client.event
async def on_server_join(server):
	client.send_message(server.owner, "Hey! I am the Iron Fleet's iron Justice Bot, specifically for Discord Servers of Sea of Thieves Fleets. If you have any questions write a message `Cradac | #2614`.\nTo set up the bot for your server type `!setup` (best in an admin-exclusive room) and go through the installation wizard. \n**Please ensure the bot has sufficient right, at least for the setup!**\n Enjoy!")
	conn = create_connection(db_file)
	with conn:
		cur = conn.cursor()
		cur.execute("INSERT INTO guilds VALUES (?,?,NULL,NULL,NULL)", (server.id, server.name))

@client.event
async def on_member_join(member):
	if not member.server.id in servers:
		return
	welcome_channel = discord.utils.get(member.server.channels, id=welcome)
	rules_channel = discord.utils.get(member.server.channels, id="479301263461449768")
	info_channel = discord.utils.get(member.server.channels, id="479313811518652417")
	intro_channel = discord.utils.get(member.server.channels, id="481455365192548363")

	member_count = str(len(member.server.members))
	maintext = "Excelsior! It seems **{}** has drunkenly washed ashore onto The Iron Islands!  Our forces have reached {} strong!\nIf you come for Sea of Thieves please head [here](https://www.seaofthieves.com/forum/topic/30248/the-iron-fleet-official-recruitment-thread-economy-wages-market-gambling-rpg-discord-community/1) to apply on the offcial forum!".format(member.display_name, member_count)
	embed=discord.Embed(
		color=0xffd700,
		description=maintext,
		timestamp=datetime.datetime.utcnow()
	)
	if member.avatar_url == "":
		embed.set_author(name=member.display_name,icon_url=member.default_avatar_url)
	else:
		embed.set_author(name=member.display_name,icon_url=member.avatar_url)
	print(member.name, member.display_name)
	embed.set_thumbnail(url="https://i.imgur.com/od8TIcs.png")
	footertext = "#{} Ironborn".format(member_count)
	embed.set_footer(text=footertext, icon_url="https://i.imgur.com/od8TIcs.png") #482296103740375051
	rules = f"Please take a moment to read our {rules_channel.mention} and {info_channel.mention}."
	embed.add_field(name="__Rules and Info__", value=rules)
	embed.add_field(name="__Pinned Messages__", value="After you enter the server, please check out the pinned messages in each channel for explicit rule lists and channel specific bot commands. This will give you an idea of all we have to offer! If you're unsure of anything, feel free to ask anyone!")
	jointext = f"If you'd like to join our ranks, please leave a message in {intro_channel.mention} with the following information.\n\n--**Gamertag:**\n--**Age:**\n--**Platform:**\n--**Other** *(anything else about yourself you'd like to share)*"
	embed.add_field(name="__Join us!__", value=jointext)
	await client.send_message(welcome_channel, embed=embed)

@client.event
async def on_member_remove(member):
	if not member.server.id in servers:
		return
	channel = discord.utils.get(member.server.channels, id=welcome)
	await client.send_message(channel, "Oh my, **{}** lost their senses during a storm and drowned. Not worthy of being called an Ironborn! What is dead may never die!".format(member.display_name))

##########################################################################################################################################


@isAdmin()
@client.command(pass_context=True, hidden=True, brief="This command takes you through a small install wizard for this bot.", description="This command takes you through a small install wizard for this bot.")
async def setup(ctx):
	lfc_channels=[]
	profile_channels=[]
	lfc_channels_para = ""
	profile_channels_para = ""
	
	await client.say("Starting the setup of this bot now. **You can stop at any point by typing 'cancel' or reacting with any odd Emoji to the current Question.**")
	msg = await client.say("Do you want to enable the 'Looking For Crew'-Helper?\n **Please react below.**")
	await client.add_reaction(msg, "✅")
	await client.add_reaction(msg, "❌")
	lfc_enabled = await client.wait_for_reaction(["✅","❌"], user=ctx.message.author, message=msg)
	if lfc_enabled.reaction.emoji == "✅":
		lfc_enabled = True
		await client.say("LFC Module is enabled.")
	elif lfc_enabled.reaction.emoji == "❌":
		lfc_enabled = False
		await client.say("LFC Module is disabled.")
	else:
		await client.say("Canceled Setup.")
		return

	if lfc_enabled:
		await client.say("In which channels should the LFC commands be usable? **Please tag one or multiple channels you want it enabled in.**")
		msg = await client.wait_for_message(author=ctx.message.author)
		if msg.content.lower() == "cancel" or len(msg.channel_mentions) == 0:
			await client.say("Canceled Setup.")
			return
		for ch in msg.channel_mentions:
			lfc_channels.append(ch.id)
		for val in lfc_channels:
			lfc_channels_para += val + ','
		lfc_channels_para = lfc_channels_para[:-1]
	
	msg = await client.say("Do you want to enable the 'Profile'-Functions?\n **Please react below.**")
	await client.add_reaction(msg, "✅")
	await client.add_reaction(msg, "❌")
	profile_enabled = await client.wait_for_reaction(["✅","❌"], user=ctx.message.author, message=msg)
	if profile_enabled.reaction.emoji == "✅":
		profile_enabled = True
		await client.say("Profile Module is enabled.")
	elif profile_enabled.reaction.emoji == "❌":
		profile_enabled = False
		await client.say("Profile Module is disabled.")
	else:
		await client.say("Canceled Setup.")
		return

	if profile_enabled:
		await client.say("In which channels should the Profile commands be usable?** Please tag one or multiple channels you want it enabled in.**")
		msg = await client.wait_for_message(author=ctx.message.author)
		if msg.content.lower() == "cancel" or len(msg.channel_mentions) == 0:
			await client.say("Canceled Setup.")
			return
		for ch in msg.channel_mentions:
			profile_channels.append(ch.id)

		for val in profile_channels:
			profile_channels_para += val + ','
		profile_channels_para = profile_channels_para[:-1]
	
	enabled = {"lfc" : lfc_enabled, "profile" : profile_enabled}
	guild_id = ctx.message.server.id
	guild_name = ctx.message.server.name

	enabled_para = ""
	for val in enabled.values():
		enabled_para += str(val) + ','
	enabled_para = enabled_para[:-1]

	conn = create_connection(db_file)
	with conn:
		cur = conn.cursor()
		try:
			print((guild_id, guild_name, enabled_para, lfc_channels_para, profile_channels_para))
			cur.execute("UPDATE guilds SET guild_id='{}', guild_name='{}', enabled='{}', lfc_channels='{}', profile_channels='{}' WHERE guild_id='{}';".format(guild_id, guild_name, enabled_para, lfc_channels_para, profile_channels_para, guild_id))
			client.dictGuilds[guild_id]=Guilds(guild_name, guild_id, enabled, lfc_channels, profile_channels)
			await client.say("Setup complete!")
		except:
		 	await client.say("Something went terribly wrong.")

@isMod()
@client.command(pass_context=True, hidden=True, brief="Bans a member by ID.", description=">>>Ban\n Ban a member just by user ID.\n\n Usage:")
async def ban(ctx, banID):
	member = discord.utils.get(ctx.message.server.members, id=banID)
	await client.ban(member, 7)
	await client.say("Just banned '{}'`{}`".format(member.name, member.id))

@isAdmin()
@client.command(pass_context=True, hidden=True)
async def id(ctx, mention):
	memberName = ctx.message.mentions[0].display_name
	memberID = ctx.message.mentions[0].id
	await client.say("{}'s ID is `{}`".format(memberName, memberID))

@client.command(pass_context=True, brief="Return every member of a role.", description=">>>Who is\nGet a list of members who are in a certain role.\n\nAliases:")
async def whois(ctx, *rolename):
	rolename = " ".join(rolename)
	role = discord.utils.get(ctx.message.server.roles, name=rolename)
	if role == None:
		client.say("This is not a valid role name.")
		return
	users = ""
	members = ctx.message.server.members
	for member in members:
		if role in member.roles:
			users += "%s\n" % member.mention
	if len(users) > 1000:
		client.say("There are too many users in this role. Try another.")
		return
	title = "Users with the role '%s'" % role.name
	emb=discord.Embed(color=0xffd700, timestamp=datetime.datetime.utcnow(), title=title, description=users)
	if member.avatar_url == "":
		emb.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.default_avatar_url)
	else:
		emb.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
	emb.set_footer()
	await client.say(embed=emb)

##########################################################################################################################################

@isGod()
@client.command(pass_context=True, hidden=True)
async def kill(ctx):
	print("Bot shutting down...")
	await client.close()
@isGod()
@client.command(pass_context=True, hidden=True)
async def load(ctx, extension_name : str):
	try:
		client.load_extension(extension_name)
	except (AttributeError, ImportError) as e:
		print("{}: {}".format(type(e).__name__, str(e)))
		return
	print("'{}' loaded.".format(extension_name))

@isGod()
@client.command(pass_context=True, hidden=True)
async def unload(ctx, extension_name : str):
	client.unload_extension(extension_name)
	print("'{}' unloaded.".format(extension_name))

if __name__ == "__main__":
	for extension in extensions:
		try:
			client.load_extension(extension)
			print('Loaded Extension {} on boot-up.'.format(extension))
		except Exception as e:
			exc = '{}: {}'.format(type(e).__name__, e)
			print('Failed to load extension {}\n{}'.format(extension, exc))

async def connect():
	print("Logging in...")
	while not client.is_closed:
		try:
			await client.start(bot_token)
		except:
			await asyncio.sleep(5)
		
client.loop.run_until_complete(connect())
