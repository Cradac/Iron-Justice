import discord
import asyncio
from discord.ext import commands
from datetime import datetime
from utils import storage

god = 116222914327478274


storage.Storage = Storage()

def isAdmin():
	def admincheck(ctx):
		if ctx.author == ctx.message.guild.owner or ctx.author.id == god:
			return True
		if ctx.author.guild_permissions.administrator:
			return True
		return False
	return commands.check(admincheck)

def isMod():
	def moderatorcheck(ctx):
		if ctx.author.guild_permissions.manage_messages:
			return True
		return False
	return commands.check(moderatorcheck)

def matchLFCChannel():
	def does_channel_match(ctx):
		lfc_settings = Storage.get_lfc_settings(ctx.guild)
		if lfc_settings['status'] and ctx.channel in lfc_settings['channels']:
			return True
		return False
	return commands.check(does_channel_match)
	
def matchProfileChannel():
	def does_channel_match(ctx):
		profile_settings = Storage.get_profile_settings(ctx.guild)
		if profile_settings['status'] and ctx.channel in profile_settings['channels']:
			return True
		return False
	return commands.check(does_channel_match)

def isIronFleet():
    def inServer(ctx):
        if ctx.message.guild.id == 479300072077787160:
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
			await ctx.send('No member found by that name.')
			return None
		if len(results) == 1:
			return results[0]
		if len(results) > 1:
			def message_check(msg):
				return msg.author == ctx.author
			i = 1
			text = 'Which Member?\n'
			for member in results:
				text += f'`{i}`: `{member}`\n'
				resultsdict[i] = member
				i += 1
			await ctx.send(text)
			msg = await client.wait_for('message', timeout=60.0, check=message_check)
			try:
				return resultsdict[int(msg.content)]
			except KeyError:
				await ctx.send('Cancelled command.')
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
		await ctx.send('No role found by that name.')
		return None
	if len(results) == 1:
		return results[0]
	if len(results) > 1:
		def message_check(msg):
			return msg.author == ctx.author
		i = 1
		text = 'Which role?\n'
		for role in results:
			text += f'`{i}`: `{role}`\n'
			resultsdict[i] = role
			i += 1
		await ctx.send(text)
		msg = await client.wait_for('message', timeout=60.0, check=message_check)
		try:
			return resultsdict[int(msg.content)]
		except KeyError:
			await ctx.send('Cancelled command.')
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