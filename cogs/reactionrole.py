import discord
from discord.ext import commands
import asyncio
import sqlite3
from sqlite3 import Error
from datetime import datetime
import cogs.guilds
from cogs.utils import isAdmin,roleSearch,create_connection,db_file

class ReactionRole(commands.Cog):
	def __init__(self, client):
		self.client = client
	

	@isAdmin()
	@commands.group(brief="Module for Reactionroles", aliases=["rr"])
	async def reactionrole(self, ctx):
		if ctx.invoked_subcommand is None:
			conn = create_connection(db_file)
			with conn:
				guild = ctx.guild
				cur = conn.cursor()
				cur.execute('SELECT id,messageid,channelid,emoji,roleid FROM reactionroles WHERE guildid={}'.format(guild.id))
				rows = cur.fetchall()
				if len(rows) == 0:
					embed = discord.Embed(
					color=0xffd700,
					timestamp=datetime.utcnow(),
					title="__all reactionroles for this server__",
					description="There are no reactionroles set for this server, yet."
					)
				else:
					embed = discord.Embed(
						color=0xffd700,
						timestamp=datetime.utcnow(),
						title="__all reactionroles for this server__"
					)
				icon = guild.icon_url_as(format='png', size=512)
				embed.set_footer(text=guild.name, icon_url=icon)
				for row in rows:
					id = row[0]
					channel = self.client.get_channel(int(row[2]))
					message = await channel.get_message(int(row[1]))
					emoji = row[3]
					role =  guild.get_role(int(row[4]))
					deleted = False
					if channel is None or role is None or message is None:
						cur.execute("DELETE * FROM reactionroles WHERE id={}".format(id))
						deleted = True
					value = "`{}` in {}\nRole: {}".format(message.id, channel.mention, role.mention)
					embed.add_field(name="{} id:`{}`".format(emoji,id), value=value, inline=True)
				if deleted:
					await ctx.send("Some deprecated reactionroles were deleted.")
			await ctx.send(embed=embed)

	@isAdmin()
	@reactionrole.command(brief="Add a reactionrole")
	async def add(self, ctx, channel:discord.TextChannel=None, messageID:int=None, emoji:str=None, role:str=None):
		if channel is None and messageID is None and emoji is None and role is None:
			pass
			#step by step
		elif channel is None or messageID is None or emoji is None or role is None:
			await ctx.send("Wrong positional argument. Please use the command like this:\n```?reactionrole add <#channel> <messageID> <emoji> <role>```")
			return
		else:
			role = await roleSearch(ctx, self.client, role)
			if role is None:
				return
			msg = await channel.get_message(messageID)
			if msg is None:
				await ctx.send("No message Found with the ID `{}`".format(messageID))
				return
			print(emoji)
			conn = create_connection(db_file)
			with conn:
				cur = conn.cursor()
				cur.execute("SELECT messageid,emoji,roleid FROM reactionroles WHERE messageid={} AND emoji={} AND roleid={}".format(messageID,emoji,role.id))
				rows = cur.fetchall()
				if len(rows) is not 0:
					await ctx.send("A reactionrole like this already exists.")
					return
				cur.execute("INSERT INTO reactionroles(messageid,channelid,guildid,emoji,roleid) VALUES (?,?,?,?,?)", (int(messageID),channel.id,ctx.guild.id,emoji,role.id))
				#await msg.add_reaction(emoji)
				embed = discord.Embed(
					color=0xffd700,
					timestamp=datetime.utcnow(),
					title="__reactionrole added!__"
				)
				member = ctx.author
				guild = ctx.guild
				icon = guild.icon_url_as(format='png', size=512)
				embed.set_author(name=member.name,icon_url=member.avatar_url)
				embed.set_footer(text=guild.name, icon_url=icon)
				embed.add_field(name="Reference ID", value="0")
				embed.add_field(name="Channel", value=channel.mention)
				embed.add_field(name="Message ID", value=msg.id)
				embed.add_field(name="Emoji", value=emoji)
				embed.add_field(name="Role", value=role.mention)
			await ctx.send(embed=embed)

	@isAdmin()
	@reactionrole.command(brief="Remove a reactionrole", aliases=["delete"])
	async def remove(self, ctx, id:int=None):
		if id is None:
			await ctx.send("Please provide an ID")
			return
		conn = create_connection(db_file)
		with conn:
			cur = conn.cursor()
			cur.execute("SELECT messageid,channelid,emoji FROM reactionroles WHERE id={}".format(id))
			row = cur.fetchone()
			if row is None:
				await ctx.send("There is no reactionrole with this ID.")
				return
			cur.execute("DELETE * FROM reactionroles WHERE id={}".format(id))
			conn.commit()
			channel = self.client.get_channel(int(row[1]))
			message = await channel.get_message(int(row[0]))
			emoji = row[3]
			for reaction in message.reacions:
				if reaction.emoji == emoji:
					async for member in reaction.users():
						await message.remove_reaction(emoji, member)

def setup(client):
	client.add_cog(ReactionRole(client))