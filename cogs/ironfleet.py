import discord
from discord.ext import commands
import asyncio
import sqlite3
from sqlite3 import Error 
from cogs.checks import isGod, isAdmin, isMod, isIronFleet, memberSearch
from cogs.checks import create_connection, db_file, welcome, servers
from datetime import datetime


class IronFleet(commands.Cog):
    def __init__(self, client):
        self.client = client
    '''
    @isIronFleet()
    @isMod()
    @commands.command(hidden=True, aliases=["member"], brief="This roles grant a player basic member status.", description=">>>add Membership\nTo use this command tag a member or type his full name. His 'Stowaway' role will be removed and he will receive the ranks of 'Member' and 'Fledgling'.\n\nAliases:")
    async def membership(self, ctx, *member):
        member = await memberSearch(ctx, self.client, " ".join(member))
        if member is None:
            return
        guild = ctx.message.guild
        for role in guild.roles:
            if role.name == "Member":
                role_member = role
            if role.name == "Fledgling":
                role_fledge = role
        await member.edit(roles=[role_member, role_fledge])
        await ctx.message.delete()
        await ctx.send("{} is now a true Ironborn! *What is dead may never die!*".format(member.mention))
    '''

    @isIronFleet()
    @isMod()
    @commands.command(hidden=True, aliases=["recruit"], brief="This roles grant a player basic recruit status.", description=">>>add Recruit Rank\nTo use this command tag a member or type his full name. His 'Stowaway' role will be removed and he will receive the ranks of 'Recruit'.\n\nAliases:")
    async def recruitment(self, ctx, *member):
        member = await memberSearch(ctx, self.client, " ".join(member))
        if member is None:
            return
        guild_roles = ctx.message.guild.roles
        recruit_role = discord.utils.get(guild_roles, name='Recruit')
        canread_role = discord.utils.get(guild_roles, name='can read')
        await member.add_roles(recruit_role, reason="Recruit Command")
        await asyncio.sleep(3)
        await member.remove_roles(canread_role, reason="Recruit Command")
        await ctx.message.delete()
        await ctx.send("{} is now an Ironborn Recruit! *What is dead may never die!*".format(member.mention))

    @isIronFleet()
    @commands.command(aliases=["invite"], brief="Get this Discord's invitelink.", description=">>>Invite Link\nThis sends a message with the invite link to the Iron Fleet's Discord.\n\nAliases:")
    async def invitelink(self, ctx):
        await ctx.message.author.send("Use this link to invite people to the Iron Fleet's Discord: https://discord.gg/cSZPMF7")


    #MEMBER JOIN MESSAGE
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.guild.id in servers or member.bot:
            return
        welcome_channel = discord.utils.get(member.guild.channels, id=welcome)
        rules_channel = discord.utils.get(member.guild.channels, id=479301263461449768)
        info_channel = discord.utils.get(member.guild.channels, id=479313811518652417)
        intro_channel = discord.utils.get(member.guild.channels, id=481455365192548363)

        #WELCOME EMBED
        member_count = str(len(member.guild.members))
        maintext = "Excelsior! It seems {} has drunkenly washed ashore onto The Iron Islands!  Our forces have reached {} strong!\n".format(member.mention, member_count)
        embed=discord.Embed(
            color=0xffd700,
            description=maintext,
            timestamp=datetime.utcnow()
        )
        embed.set_author(name=member,icon_url=member.avatar_url)
        guild = member.guild
        icon = guild.icon_url_as(format='png', size=1024)
        embed.set_thumbnail(url=icon) #"https://i.imgur.com/od8TIcs.png"
        footertext = "#{} Ironborn".format(member_count)
        embed.set_footer(text=footertext, icon_url=icon) #"https://i.imgur.com/od8TIcs.png"
        await welcome_channel.send(embed=embed)


        #PM EMBED
        txt = '\
Ahoy and welcome to the Iron Fleet!\n\
Please take a moment to read the {} and click the reaction emoji to indicate that you\'ve done so.  To apply, submit an application in {}.\n\
Lastly, head over to {} and use the appropriate reaction to gain access to game specific channels.\n\
Feel free to message a Senior or Junior Officer if you have any questions or need any help.'.format(rules_channel.mention, intro_channel.mention, info_channel.mention)
        embed=discord.Embed(
            color=0xffd700,
            description=txt,
            timestamp=datetime.utcnow()
        )
        guild = member.guild
        icon = guild.icon_url_as(format='png', size=1024)
        embed.set_thumbnail(url=icon)
        footertext = "#{} Ironborn".format(member_count)
        embed.set_footer(text=footertext, icon_url=icon)
        await member.send(embed=embed)


    #MEMBER REMOVE MESSAGE
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if not member.guild.id in servers or member.bot:
            return
        channel = discord.utils.get(member.guild.channels, id=welcome)
        await channel.send("Oh my, **{}** lost their senses during a storm and drowned. Not worthy of being called an Ironborn! What is dead may never die!".format(member))

def setup(client):
    client.add_cog(IronFleet(client))