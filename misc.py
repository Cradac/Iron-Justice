import discord
from discord.ext import commands
import asyncio
import datetime
import guilds
from checks import isAdmin, isMod
import math

class Misc:
    def __init__(self, client):
        self.client = client

    @isAdmin()
    @commands.command(pass_context=True, aliases=["guildinfo"], brief="Gives Admin Information about this server and this bots setup")
    async def serverinfo(self, ctx):
        guild = ctx.message.server
        member = ctx.message.author
        icon = "https://cdn.discordapp.com/icons/{}/{}.png".format(guild.id, guild.icon)
        embed = discord.Embed(
            colour=discord.Colour(0xffd700), 
            timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=icon)
        if member.avatar_url == "":
            embed.set_author(name=member.display_name,icon_url=member.default_avatar_url)
        else:
            embed.set_author(name=member.display_name,icon_url=member.avatar_url)
        embed.set_footer(text=guild.name, icon_url=icon)
        server_info = "**Server Name:** `{}`\n**Server ID:** `{}`\n**Owner:** {}\n**Member Count:** {}".format(guild.name, guild.id, guild.owner.mention, guild.member_count)
        embed.add_field(name="__Server Info__", value=server_info, inline=False)
        lfc_enabled = ctx.bot.dictGuilds[ctx.message.server.id].enabled["lfc"]
        lfc_text = ""           
        if lfc_enabled == "True":
            lfc_text = "`enabled` in:\n"
            lfc_channels = ctx.bot.dictGuilds[ctx.message.server.id].lfc_channels
            for channel in lfc_channels:
                ch = discord.utils.get(ctx.message.server.channels, id=channel)
                if ch is not None:
                    lfc_text += "{}, ".format(ch.mention)
            lfc_text = lfc_text[:-2]
        else:
            lfc_text = "`disabled`"
        embed.add_field(name="__LFC-Module__", value=lfc_text, inline=True)

        profile_enabled = ctx.bot.dictGuilds[ctx.message.server.id].enabled["profile"]
        profile_text = ""      
        if profile_enabled == "True":
            profile_text = "`enabled` in:\n"
            profile_channels = ctx.bot.dictGuilds[ctx.message.server.id].profile_channels
            for channel in profile_channels:
                ch = discord.utils.get(ctx.message.server.channels, id=channel)
                if ch is not None:
                    profile_text += "{}, ".format(ch.mention)
            profile_text = profile_text[:-2]
        else:
            profile_text = "`disabled`"
        embed.add_field(name="__Profile-Module__", value=profile_text, inline=True)

        await self.client.say(embed=embed)

    @isMod()
    @commands.command(pass_context=True, hidden=True, brief="Bans a member by ID.", description=">>>Ban\n Ban a member just by user ID.\n\n Usage:")
    async def ban(self,ctx, banID):
        member = discord.utils.get(ctx.message.server.members, id=banID)
        await self.client.ban(member, 7)
        await self.client.say("Just banned '{}'`{}`".format(member.name, member.id))

    @isMod()
    @commands.command(pass_context=True, hidden=True)
    async def id(self, ctx, mention):
        memberName = ctx.message.mentions[0].display_name
        memberID = ctx.message.mentions[0].id
        await self.client.say("{}'s ID is `{}`".format(memberName, memberID))

    @commands.command(pass_context=True, brief="Return every member of a role.", description=">>>Who is\nGet a list of members who are in a certain role.\nPLEASE WRAP ROLES WITH SPACES IN QUOTATIONMARKS!\n\nAliases:")
    async def whois(self, ctx, rolename : str, page : int=1 ):
        role = discord.utils.get(ctx.message.server.roles, name=rolename)
        if role == None:
            self.client.say("This is not a valid role name.")
            return
        users = []
        members = ctx.message.server.members
        for member in members:
            if role in member.roles:
                users.append(int(member.id))
        users.sort()
        sumpages=math.ceil(len(users)/20)
        if page > sumpages:
            page = sumpages
        pagestart = (page * 20)-20
        pageend = pagestart + 19
        desctext = "({} in total)\n".format(str(len(users)))
        for i in range(pagestart, pageend):
            try:
                desctext += ctx.message.server.get_member(str(users[i])).mention + "\n"
            except IndexError:
                break

        title = "__Users with the role '{}':__".format(role.name)
        emb=discord.Embed(color=0xffd700, timestamp=datetime.datetime.utcnow(), title=title, description=desctext)
        if member.avatar_url == "":
            emb.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.default_avatar_url)
        else:
            emb.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        emb.set_footer(text="Page {}/{}".format(page, sumpages))
        await self.client.say(embed=emb)


def setup(client):
    client.add_cog(Misc(client))