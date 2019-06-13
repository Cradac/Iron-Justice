#The Iron Fleet's Iron Justice Bot
#Primary intention: Supporting the Iron Fleet's Discord server.
#Secondary intention: gimicks like the profile System
#Author Maxe aka. Cradac

#Version: 3.0.0a rewrite

import discord
from discord.ext import commands
import sys
from datetime import datetime
import traceback
from utils import utils

_version = '3.0.0a'

print(sys.version)
print(discord.__version__)
print('bot version: {}'.format(_version))


Client = discord.Client()
client = commands.Bot(command_prefix = ['?'], case_insensitive=True, description=f'This is the Iron Fleet\'s own bot THE IRON JUSTICE V{_version} rewrite. For questions please contact Cradac | Max#2614.\n#beMoreIron', help_command=None)
if len(sys.argv) == 1:
	bot_token = 'NDIxMjY4MjA4MzM1NTg1Mjkw.DYK4Mw.aBwGz447sS0NNB5V8yD6Yfi3-Ko'
else:
	bot_token = sys.argv[1]
	sys.stdout = open(datetime.now().strftime('logs/discord_log_%Y_%m_%d_%H_%M_%S.log'), 'w+')


extensions = ['activity_logging', 'auto_voice', 'ironfleet', 'lfc', 'misc', 'profile', 'settings', 'welcome']


##########################################################################################################################################


@client.event
async def on_ready():
	print('Bot is ready!')
	game = discord.Game('the Iron Price | ?help')
	await client.change_presence(status=discord.Status.online, activity=game)
	print('Logged in as: ' + client.user.name)
	print('Bot ID: ' + str(client.user.id))
	for guild in client.guilds:
		print (f'Connected to server: {guild}')
	print('------')

	

@client.event
async def on_message(message):
	if type(message.channel) is discord.DMChannel:
		return
	log_channel = discord.utils.get(message.guild.channels, name="message-log")
	if not log_channel :
		await client.process_commands(message)
		return
	if not message.author.bot:
		jump_to_message = f'[Jump](https://discordapp.com/channels/{message.guild.id}/{message.channel.id}/{message.id})'
		embed = utils.createEmbed(description=f'in {message.channel.mention}:\n{message.content}\n{jump_to_message}', colour='iron', author=message.author)
		embed.set_footer(text=message.author.id)
		if len(message.attachments) > 0:
			embed.set_image(url=message.attachments[0].url)
		await log_channel.send(embed=embed)
		await client.process_commands(message)

@client.event
async def on_message_edit(before, after):
	await client.process_commands(after)

@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CheckFailure) or isinstance(error, commands.CommandNotFound):
		pass
	elif isinstance(error, commands.BadArgument):
		embed = utils.createEmbed(
			description=f'Error: There was an error with the command arguments.\n\nUsage:\n`{ctx.command.usage}`',
			colour='error',
			author=ctx.author)
		await ctx.send(embed=embed)
	elif isinstance(error, commands.MissingRequiredArgument):
		embed = utils.createEmbed(
			description=f'Error: Your are missing an argument.\n\nUsage:\n`{ctx.command.usage}`',
			colour='error',
			author=ctx.author)
		await ctx.send(embed=embed)
	else:
		try:
			embed = utils.createEmbed(
				title='An error eccured',
				description=f'\
				**{type(error)}**\n\
				```{error}```\n\n\
				[Jump](https://discordapp.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id})',
				author=ctx.author,
				colour='error'
			)
			embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url_as(format='png', size=128))
			app = await client.application_info()
			await app.owner.send(embed=embed)
			raise error
		except Exception as error:
			tb = traceback.format_exc()
			print(error, tb)


##########################################################################################################################################

@client.command(hidden=True, brief='Pong!')
async def ping(ctx):
	await ctx.send('Pong! `({} ms)`'.format(round(client.latency, 2)))

@client.command(hidden=True, brief='Version Info')
async def version(ctx):
	await ctx.send(f'\
		bot version: `{_version}`\n\
		discord.py version: `{discord.__version__}`\n\
		system info: `{sys.version}`')

@client.command(brief='Help Command.')
async def help(ctx, *, name: str = None):
	if name:
		embed = utils.createEmbed(colour='iron')
		command = client.get_command(name=name)
		cog = client.get_cog(name=name)
		if cog:
			embed.title = f'__Module: {cog.qualified_name}__'
			txt = ''
			for command in cog.get_commands():
				txt += f'{client.command_prefix[0]}{command.name} - {command.brief}\n'
			embed.add_field(name='Commands', value=txt, inline=False)
		elif command:
			embed.title = f'__Command: {client.command_prefix[0]}{command.name}__'
			embed.add_field(name='Description', value=command.description, inline=False)
			embed.add_field(name='Usage', value=command.usage, inline=False)
			if len(command.aliases) > 0:
				embed.add_field(name='Aliases', value=', '.join(f'`{a}`' for a in command.aliases), inline=False)
			embed.set_footer(text=f'Module: {command.cog_name}')
		else:
			embed = utils.createEmbed(colour='error', description='Error: Command or Cog not found.', author=ctx.author)

	else:
		embed = utils.createEmbed(title='__Commands__', description='For a documentation of all commands go [here](link-to-commands.md).', colour='iron')
		for name, cog in client.cogs.items():
			commands = cog.get_commands()
			if len(commands) > 0:
				txt = ''
				for command in commands:
					if command.hidden:
						continue
					txt += f'{client.command_prefix[0]}{command.name} - {command.brief}\n'
				if txt != '':
					embed.add_field(name=name, value=txt, inline=False)
			else:
				continue
	await ctx.send(embed=embed)



##########################################################################################################################################

@commands.is_owner()
@client.command(hidden=True)
async def kill(ctx):
	print('Bot shutting down...')
	await client.close()


@commands.is_owner()
@client.command(hidden=True)
async def load(ctx, extension_name: str):
	try:
		extension_name = f'cogs.{extension_name}'
		client.load_extension(extension_name)
	except (AttributeError, ImportError) as e:
		print(f'{type(e).__name__}: {e}')
		return
	print(f'`{extension_name}` loaded.')

@commands.is_owner()
@client.command(hidden=True)
async def unload(ctx, extension_name: str):
	extension_name = f'cogs.{extension_name}'
	client.unload_extension(extension_name)
	print(f'`{extension_name}` unloaded.')

@commands.is_owner()
@client.command(hidden=True)
async def reload(ctx, extension_name: str):
	try:
		extension_name = f'cogs.{extension_name}'
		client.unload_extension(extension_name)
		client.load_extension(extension_name)
	except (AttributeError, ImportError) as e:
		print(f'{type(e).__name__}: {e}')
		return
	print(f'`{extension_name}` reloaded.')

if __name__ == "__main__":
	for extension in extensions:
		try:
			client.load_extension(f'cogs.{extension}')
			print(f'Loaded Extension {extension} on boot-up.')
		except Exception as e:
			exc = f'{type(e).__name__}: {e}'
			print(f'Failed to load extension {extension}\n{exc}')

client.run(bot_token)

