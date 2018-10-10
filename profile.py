import discord
from discord.ext import commands
import asyncio
import guilds
import sqlite3
from sqlite3 import Error
import datetime
from checks import matchprofilechannel,matchlfcchannel

db_file = "JusticeDB.db"


class Profile:
    def __init__(self, client):
        self.client = client	

    #connecting to db 
    def create_connection(self, db_file):
        """ create a database connection to a SQLite database """
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return None


    @matchprofilechannel()
    @commands.command(brief="Shows your Player Profile.", description=">>>Profile:\nThis shows your player profile.\nAdd your XBox Profile name with '!gt <Your Gamertag>'.\nYou can update your levels with '!levels <GH> <OOS> <MA> [AF]'.\nIf you tag a player after '!profile [member]' you can see his/her profile.\n\nAliases:")
    async def profile(self, ctx, member:discord.Member=None):
        if member is None:
            member = ctx.message.author
        fr = member.top_role.name
        conn = self.create_connection(db_file)
        with conn:
            cur = conn.cursor()
            try:
                cur.execute("SELECT tag, gh, oos, ma, af, img_url, pirate_name FROM users WHERE user_id = {}".format(member.id))
                rows = cur.fetchall()
                for row in rows:
                    gamertag = row[0]
                    gh = int(row[1])
                    oos = int(row[2])
                    ma = int(row[3])
                    af = int(row[4])
                    img = row[5]
                    pname = row[6]
                embed=discord.Embed(
                    color=0xffd700,
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_author(name=member.name,icon_url=member.avatar_url)
                guild = ctx.message.guild
                embed.set_thumbnail(url="https://cdn.discordapp.com/icons/{}/{}.png".format(guild.id, guild.icon)) #"https://i.imgur.com/od8TIcs.png"
                embed.add_field(name="Gamertag", value=gamertag, inline=False)
                if pname != "none":
                    embed.add_field(name="<:jollyroger:486619773875126293> Pirate Name", value=pname, inline=False)
                embed.add_field(name="<:rank:486619774445551626> Rank", value=fr, inline=False)
                embed.add_field(name="<:gh:486619774424449036> Gold Hoarders", value=gh, inline=True)
                embed.add_field(name="<:oos:486619776593166336> Order of Souls", value=oos, inline=True)
                embed.add_field(name="<:ma:486619774688952320> Merchant Alliance", value=ma, inline=True)
                embed.add_field(name="<:af:486619774122459178> Athena's Fortune", value="{}".format(af), inline=False)
                embed.set_footer()
                if img != "none":
                    embed.set_image(url=img)
                if gh >= 50 and oos >= 50 and ma >= 50:
                    embed.add_field(name="You are a Legend!", value='\u200b', inline=False)
                await ctx.send(embed=embed)
            except:
                cur.execute("INSERT INTO users VALUES (?, ?, 0, 0, 0, 0, 'none', 'none', 'none');", (member.id, member.name))
                conn.commit()
                embed=discord.Embed(
                    color=0xffd700,
                    timestamp=datetime.datetime.utcnow(),
                    title="__Your Profile was created!__"
                )
                guild = ctx.message.guild
                icon = "https://cdn.discordapp.com/icons/{}/{}.png".format(guild.id, guild.icon)
                embed.set_footer(icon_url=icon)
                embed.set_author(name=member.name,icon_url=member.avatar_url)
                embed.add_field(name="__add your information__", value="1. Add your XBox gamertag with `?gt <gamertag>`.\n2. Add your levels with `?levels <GH> <OoS> <MA> [AF]`.", inline=False)
                embed.add_field(name="__optional features__", value="- Add an image of your pirate with `?set_image <URL>`. You can also upload the image right to discord and type `?set_image` without any paramters.\nThis URL **NEEDS** to be a direct link to the image ending with `.jpg`, `.png` or `.gif`.\n- Add a pirate name (for role players) by typing `?alias <piratename>`.", inline=False)
                embed.add_field(name="__additional notes__", value="Please note that you **DO NOT** need to add the brackets (`<>`, `[]`). They are merely Syntax to show which arguments are mandatory (`<>`) and which can be left out and will use the previous value (`[]`). This is programming standard.", inline=False)
                await ctx.send(embed=embed)

    @matchprofilechannel()
    @commands.command(aliases=["gamertag"], brief="Update your Gamertag.", description=">>>Gamertag:\nWith this command you can update your Gamertag so people can invite you easier.\n\nAliases:")
    async def gt(self, ctx, *gamertag):
        if len(gamertag) > 0:
            gt = " ".join(gamertag)
            if gt == "":
                gt = "None"
            conn = self.create_connection(db_file)
            with conn:
                cur = conn.cursor()
                if len(ctx.message.mentions) == 0:
                    try:
                        cur.execute("UPDATE users SET tag = '{}' WHERE user_id = '{}'".format(gt, ctx.message.author.id))
                        conn.commit()
                        await ctx.send("Successfully updated your Gamertag to *'{}'*.".format(gt))
                    except:
                        await ctx.send("Something went wrong there. Try again some time later.")
                else:
                    uid = ctx.message.mentions[0].id
                    cur.execute("SELECT tag FROM users WHERE user_id='{}'".format(uid))
                    gamertag = "%s" % cur.fetchone()
                    embed=discord.Embed(
                    color=0xffd700,
                    timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_author(name=ctx.message.mentions[0].name,icon_url=ctx.message.mentions[0].avatar_url)
                    embed.add_field(name="Gamertag", value=gamertag, inline=False)
                    embed.set_footer()
                    await ctx.send(embed=embed)
        else: 
            conn = self.create_connection(db_file)
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT tag FROM users WHERE user_id='{}'".format(ctx.message.author.id))
                gamertag = "%s" % cur.fetchone()
                embed=discord.Embed(
                color=0xffd700,
                timestamp=datetime.datetime.utcnow()
                )
                embed.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
                embed.add_field(name="Gamertag", value=gamertag, inline=False)
                embed.set_footer()
                await ctx.send(embed=embed)

    @matchprofilechannel()
    @commands.command(aliases=["lvl"], brief="Update your Ingame Levels.", description=">>>Levels:\nUse this command to regularly update your levels.\ngh = Gold Hoarders\noos = Order of Souls\nma = Merchant Aliance\naf(optional) = Athena's Fortune\n\nAliases:")
    async def levels(self, ctx, gh:int=0, oos:int=0, ma:int=0, af:int=None):
        #if ctx.message.channel.name == "crew-ledger":
        if 0< gh <=50 and 0< oos <=50 and 0 < ma <=50:	
            conn = self.create_connection(db_file)
            with conn:
                cur = conn.cursor()
                try:
                    if af == None:
                        cur.execute("UPDATE users SET gh='{}', oos='{}', ma='{}' WHERE user_id = '{}'".format(gh, oos, ma, ctx.message.author.id))
                    else:
                        if 0<= af <=10:
                            cur.execute("UPDATE users SET gh='{}', oos='{}', ma='{}', af='{}' WHERE user_id = '{}'".format(gh, oos, ma, af, ctx.message.author.id))	
                    await ctx.send("{}, your levels are updated.".format(ctx.message.author.mention))
                except:
                    await ctx.send("Something went wrong. Please try again later.")

    @matchprofilechannel()
    @commands.command(aliases=["image", "img"], brief="Set a picture for your profile.", description=">>>Set Image\nWith this command you can set a picture for your profile.\nMake sure your URL ends with '.png', '.jpg' or '.gif'.\nIf you want no profile picture type '!set-image none'.\n\n Aliases:")
    async def set_image(self, ctx, img_url:str="none"):
        print(img_url)
        if img_url == "none" and len(ctx.message.attachments) > 0:
            img_url = ctx.message.attachments[0].url
        if img_url.endswith(".png") or img_url.endswith(".jpg") or img_url.endswith(".gif") or img_url == "none":
            conn = self.create_connection(db_file)
            with conn:
                cur = conn.cursor()
                try:
                    cur.execute("UPDATE users SET img_url='{}' WHERE user_id = '{}'".format(img_url, ctx.message.author.id))
                    if img_url != "none":
                        await ctx.send("{}, your profile image was updated.".format(ctx.message.author.mention))
                    else: 
                        await ctx.send("{}, your profile image was deleted.".format(ctx.message.author.mention))
                except:
                    await ctx.send("Something went wrong. Please try again later.")
        else: 
            await ctx.send("The link you are submitting **has** to end with `.png`, `.jpg` or `.gif`.")

    @matchprofilechannel()
    @commands.command(aliases=["alias"], brief="Set a Piratename for your profile.", description=">>>Pirate Name\nWith this command you can set a pirate name for your profile.\nIf you want no pirate name type '!piratename none'.\n\n Aliases:")
    async def piratename(self, ctx, *pname):
        #if ctx.message.channel.name == "crew-ledger":
        pname = " ".join(pname)
        conn = self.create_connection(db_file)
        with conn:
            cur = conn.cursor()
            try:
                cur.execute("UPDATE users SET pirate_name='{}' WHERE user_id = '{}'".format(pname, ctx.message.author.id))
                if pname != "none":
                    await ctx.send("{}, your pirate name was updated.".format(ctx.message.author.mention))
                else: 
                    await ctx.send("{}, your pirate name was deleted.".format(ctx.message.author.mention))
            except:
                await ctx.send("Something went wrong. Please try again later.")


def setup(client):
    client.add_cog(Profile(client))