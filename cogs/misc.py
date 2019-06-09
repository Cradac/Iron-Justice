import discord
from discord.ext import commands
import asyncio
import datetime
import utils.guilds
from utils.utils import isAdmin, isMod, isGod, roleSearch, god, memberSearch, create_connection, db_file
import math

class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["guildinfo"], brief="Gives Admin Information about this guild and this bots setup")
    async def serverinfo(self, ctx):
        guild = ctx.message.guild
        member = ctx.message.author
        icon = guild.icon_url_as(format='png', size=1024)
        embed = discord.Embed(
            colour=discord.Colour(0xffd700), 
            timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=icon)
        if member.avatar_url == "":
            embed.set_author(name=member.display_name,icon_url=member.default_avatar_url)
        else:
            embed.set_author(name=member.display_name,icon_url=member.avatar_url)
        embed.set_footer(text=guild.name, icon_url=icon)
        server_info = "**Guild Name:** `{}`\n**Guild ID:** `{}`\n**Owner:** {}\n**Member Count:** {}".format(guild.name, guild.id, guild.owner.mention, guild.member_count)
        embed.add_field(name="__Server Info__", value=server_info, inline=False)
        lfc_enabled = ctx.bot.dictGuilds[ctx.message.guild.id].enabled["lfc"]
        lfc_text = ""           
        if lfc_enabled == "True":
            lfc_text = "`enabled` in:\n"
            lfc_channels = ctx.bot.dictGuilds[ctx.message.guild.id].lfc_channels
            for channel in lfc_channels:
                ch = discord.utils.get(ctx.message.guild.channels, id=channel)
                if ch is not None:
                    lfc_text += "{}, ".format(ch.mention)
            lfc_text = lfc_text[:-2]
        else:
            lfc_text = "`disabled`"
        embed.add_field(name="__LFC-Module__", value=lfc_text, inline=True)

        profile_enabled = ctx.bot.dictGuilds[ctx.message.guild.id].enabled["profile"]
        profile_text = ""      
        if profile_enabled == "True":
            profile_text = "`enabled` in:\n"
            profile_channels = ctx.bot.dictGuilds[ctx.message.guild.id].profile_channels
            for channel in profile_channels:
                ch = discord.utils.get(ctx.message.guild.channels, id=channel)
                if ch is not None:
                    profile_text += "{}, ".format(ch.mention)
            profile_text = profile_text[:-2]
        else:
            profile_text = "`disabled`"
        embed.add_field(name="__Profile-Module__", value=profile_text, inline=True)

        if ctx.author.id == god:
            await ctx.author.send(embed=embed)
            await ctx.message.delete()
            return
        await ctx.send(embed=embed)

    @commands.command(brief="Return every member of a role.", description=">>>Who is\nGet a list of members who are in a certain role.\nPLEASE WRAP ROLES WITH SPACES IN QUOTATIONMARKS!\n\nAliases:")
    async def whois(self, ctx, rolename : str, page : int=1 ):
        role = await roleSearch(ctx, self.client, rolename)
        if role is None:
            return
        users = []
        members = ctx.message.guild.members
        for member in members:
            if role in member.roles:
                users.append(member.id)
        users.sort()
        sumpages=math.ceil(len(users)/20)
        if page > sumpages:
            page = sumpages
        pagestart = (page * 20)-20
        pageend = pagestart + 19
        desctext = "({} in total)\n".format(str(len(users)))
        for i in range(pagestart, pageend):
            try:
                desctext += ctx.message.guild.get_member(users[i]).mention + "\n"
            except IndexError:
                break

        title = "__Users with the role '{}':__".format(role)
        emb=discord.Embed(color=0xffd700, timestamp=datetime.datetime.utcnow(), title=title, description=desctext)
        if member.avatar_url == "":
            emb.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.default_avatar_url)
        else:
            emb.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        emb.set_footer(text="Page {}/{}".format(page, sumpages))
        await ctx.send(embed=emb)

    @isMod()
    @commands.command(hidden=True, brief="Bans a member by ID.", description=">>>Ban\n Ban a member just by user ID.\n\n Usage:")
    async def ban(self,ctx, banID):
        member = discord.utils.get(ctx.message.guild.members, id=int(banID))
        await member.ban(delete_message_days=7)
        await ctx.send("Just banned '{}'`{}`".format(member.name, member.id))

    @isMod()
    @commands.command(hidden=True)
    async def id(self, ctx, member:discord.Member):
        memberName = member.display_name
        memberID = member.id
        await ctx.send("{}'s ID is `{}`".format(memberName, memberID))

    @isMod()
    @commands.command(hidden=True, aliases=["nick"])
    async def nickname(self, ctx, member, *new_name : str):
        new_name = (" ").join(new_name)
        member = await memberSearch(ctx, self.client, member)
        if member is None:
            return
        await member.edit(nick=new_name)
        await ctx.send("`{}` is now called *'{}'*".format(member, new_name))

    @isGod()
    @commands.command(hidden=True)
    async def sql(self, ctx, *query : str):
        query = " ".join(query)
        
        conn = create_connection(db_file)
        with conn:
            cur = conn.cursor()
            cur.execute(query)
            conn.commit()
            await ctx.send(f'Executed SQL Query `{query}` successfully.')

    @commands.command(
        aliases=['invite'],
        brief='Get this Guild\'s invitelink.',
        description='This sends you a PM the invite link to this Guild.'
    )
    async def invite(self, ctx):
        try:
            link = ctx.guild.invites[0]
        except:
            link = ctx.guild.channels[0].create_invite(max_age=86400, reason=f'{ctx.author} requested an invite link.')
        await ctx.author.send(f'Use this link to invite people to {ctx.guild.name}\'s Discord Server: {link.url}')
def setup(client):
    client.add_cog(Misc(client))