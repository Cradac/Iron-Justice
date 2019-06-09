import discord
from discord.ext import commands
import asyncio
import datetime
from utils.utils import matchprofilechannel, matchlfcchannel, memberSearch, createEmbed
from utils.storage import Storage
import re

class Profile(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.Storage = Storage()
        self.profile_messages = list(int)
        self.profile_status = dict(int, str)

        self.steam_emoji = self.client.get_emoji(586475562772725780)
        self.xbox_emoji = self.client.get_emoji(563799115201249301)
        self.psn_emoji = self.client.get_emoji(563799160021712922)
        self.nintendo_emoji = self.client.get_emoji(534433688025563137)
        self.sot_emoji = self.client.get_emoji(488445174536601600)
        self.game_emoji = '🎮'
        self.game_emoji_url = 'https://discordapp.com/assets/7d600babcd1bddfd7a7d35acc1ed4cd3.svg'
        self.stop_emoji = '⏹'

        self.emojis = [self.xbox_emoji, self.sot_emoji, self.game_emoji, self.stop_emoji]


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        if reaction.message.id in self.profile_messages:
            if reaction.emoji in self.emojis:
                await reaction.remove(user)
                if user == reaction.message.author:
                    if reaction.emoji == self.xbox_emoji and self.profile_status[reaction.message.id] != 'xbox':
                        embed = self.get_xbox_page(user)
                        self.profile_status[reaction.message.id] = 'xbox'
                    elif reaction.emoji == self.sot_emoji and self.profile_status[reaction.message.id] != 'sot':
                        embed = self.get_sot_page(None, user)
                        self.profile_status[reaction.message.id] = 'sot'
                    elif reaction.emoji == self.game_emoji and self.profile_status[reaction.message.id] != 'game':
                        embed = self.get_game_page
                        self.profile_status[reaction.message.id] = 'game'
                    elif reaction.emoji == self.stop_emoji:
                        await self.reaction_menu_timeout(reaction.message, wait=False)
                        return
                    await reaction.message.edit(embed=embed)

    async def reaction_menu_timeout(self, message: discord.Message, wait: bool = True):
        if wait:
            await asyncio.sleep(300)
        await message.clear_reactions()
        self.profile_messages.remove(message.id)
        del self.profile_status[message.id]

    async def prepare_reaction_menu(self, message: discord.Message):
        for emoji in self.emojis:
            await message.add_reaction(emoji)

    def get_xbox_page(self, member: discord.Member):
        gtag = self.Storage.get_xbox_tag(member)
        embed = createEmbed(colour='iron', author=member)
        icon = member.guild.icon_url_as(format='png', size=512)
        embed.set_thumbnail(url=icon)
        embed.set_footer(icon_url=self.xbox_emoji.url, text='Xbox')
        if gtag:
            pass
        else:
            embed.description = 'There is no Xbox Gamertag set for this profile.\n\
                If this is your profile you can add it with `?gt edit <gamertag>`.'
        return embed

    async def get_sot_page(self, ctx: commands.Context, member: discord.Member):
        info = await self.Storage.get_sot_profile(ctx, member)
        embed = createEmbed(colour='iron', author=member)
        icon = member.guild.icon_url_as(format='png', size=512)
        embed.set_thumbnail(url=icon)
        embed.set_footer(icon_url=self.sot_emoji.url, text='Sea of Thieves')
        embed.add_field(name="Gamertag", value=info['gtag'], inline=False)
        if info['alias']:
            embed.add_field(name="<:jollyroger:486619773875126293> Pirate Alias", value=info['alias'], inline=False)
        embed.add_field(name="<:rank:486619774445551626> Rank", value=member.top_role.name, inline=False)
        embed.add_field(name="<:gh:486619774424449036> Gold Hoarders", value=info['gh'], inline=True)
        embed.add_field(name="<:oos:486619776593166336> Order of Souls", value=info['oos'], inline=True)
        embed.add_field(name="<:ma:486619774688952320> Merchant Alliance", value=info['ma'], inline=True)
        embed.add_field(name="<:hc:573788002455650314> Hunter's Call", value=info['hc'], inline=True)
        embed.add_field(name="<:sd:573788001407205376> Sea Dogs", value=info['sd'], inline=True)
        embed.add_field(name="<:af:486619774122459178> Athena's Fortune", value=info['af'], inline=False)
        if info['img']:
            embed.set_image(url=info['img'])
        alliances = [info['gh'] == 50, info['oos'] == 50, info['ma'] == 50, info['hc'] == 50, info['sd'] == 50]
        true_count = sum(alliances)
        if true_count >= 3:
            embed.add_field(name="You are a Legend!", value='\u200b', inline=False)
        return embed

    def get_game_page(self, member: discord.Member):
        info = self.Storage.get_tag_profile(member)
        embed = createEmbed(colour='iron', author=member)
        icon = member.guild.icon_url_as(format='png', size=512)
        embed.set_thumbnail(url=icon)
        embed.set_footer(icon_url=self.game_emoji_url, text='Gamertags')
        embed.add_field(name=str(self.steam_emoji) + 'Steam', value=info['steam'], inline=True)
        embed.add_field(name=str(self.xbox_emoji) + 'Xbox Live', value=info['xbox'], inline=True)
        embed.add_field(name=str(self.psn_emoji) + 'Playstation Network', value=info['psn'], inline=True)
        embed.add_field(name=str(self.nintendo_emoji) + 'Nintendo Friend Code', value=info['nintendo'], inline=True)
        return embed


    @matchprofilechannel()
    @commands.command(
        brief='Shows a member\' profile.',
        description='This command shows a member\'s profile.\n\
            You can navigate the pages with the reaction menu for 5 minutes. If you are done please click the `STOP` emoji.',
        usage='?profile [member]'
    )
    async def profile(self, ctx, *, member: str = None):
        member = await memberSearch(ctx, self.client, member) if member else ctx.message.author
        if not member:
            return
        embed = self.get_sot_page(ctx, member)
        msg = await ctx.send(embed=embed)
        await self.prepare_reaction_menu(msg)
        self.profile_messages.append(msg.id)
        self.profile_status[msg.id] = 'sot'


    @matchprofilechannel()
    @commands.command(
        brief='Show your own Gamertag',
        description='This command shows the Gamertag page of the profile.\n\
            There are some subcommands to alter your gamertags or show someone elses gamertags.\n\
            You can navigate the pages with the reaction menu for 5 minutes. If you are done please click the `STOP` emoji.',
        usage='?gt [edit|show] [*args]'
    )
    async def gt(self, ctx):
        embed = self.get_game_page(ctx.author)
        msg = await ctx.send(embed=embed)
        await self.prepare_reaction_menu(msg)
        self.profile_messages.append(msg.id)
        self.profile_status[msg.id] = 'game'


    @matchprofilechannel()
    @gt.command(
        brief='Edit your one of your gamertags.',
        description='Use this to edit your gamertag.\n\
            You can choose of these platforms: `steam`, `xbox`, `psn`, `nintendo`.',
        usage='?gt edit <platform> <gamertag>'
    )
    async def edit(self, ctx, platform: str , *, gamertag: str):
        platforms = ['steam', 'xbox', 'psn', 'nintendo']
        if platform not in platforms:
            await ctx.send(f'You need to select one of these platforms:\n• ' + '\n• '.join(platforms))
            return
        self.Storage.update_gamertag(ctx.author, platform, gamertag)
        embed = createEmbed(description=f'Your {platform} gamertag has been updated to `{gamertag}`.', author=ctx.author)
        embed.set_footer(icon_url=ctx.guild.icon_url_as(format='png', size='128'), text='Gamertag updated')
        await ctx.send(embed=embed)


    @matchprofilechannel()
    @gt.command(
        brief='Show another member\'s gamertag profile page.',
        description='This command can show another member\'s gamertag.',
        usage='?gt show <member>',
        aliases=['see', 'search']
    )
    async def show(self, ctx, *, member: str):
        member = await memberSearch(ctx, self.client, member) if member else ctx.message.author
        if not member:
            return
        embed = self.get_game_page(member)
        msg = await ctx.send(embed=embed)
        await self.prepare_reaction_menu(msg)
        self.profile_messages.append(msg.id)
        self.profile_status[msg.id] = 'game'


    @matchprofilechannel()
    @commands.command(
        aliases=['lvl'],
        brief='Update your Ingame Levels.',
        description='Use this command to regularly update your levels.\ngh: Gold Hoarders\noos: Order of Souls\nma: Merchant Aliance\nhc: Hunter\'s Call\nsd: Sea Dogs\naf: Athena\'s Fortune',
        usage='?levels *[<company>=<level>]'
    )
    async def levels(self, ctx, *, args: str):
        comps = dict()
        r = re.compile('^(([a-z]|[A-Z]){1,3}=([1-4][0-9]|50|[1-9])\s)*$')
        if not r.match(args + ' '):
            await ctx.send('The Syntax is not correct. Try this instead:\n`?levels gh=50`\n`?levels af=10 hc=50 gh=50 sd=50 ma=50 oos=50`')
            return
        for arg in args:
            arg = arg.split('=')
            try:
                comps[arg[0].lower()] = int(arg[1])
            except ValueError:
                await ctx.send("Please only pass integers for levels.")
                return
        for comp,lvl in comps.items():
            if comp not in ['gh', 'oos', 'ma', 'hc', 'sd', 'af']:
                await ctx.send(f'`{comp}` is not a correct trading company abbreviation.\nPossible abbreviations are: `gh`, `oos`, `ma`, `hc`, `sd`, `af`.')
                return
            if comp == 'af' and (not isinstance(lvl, int) or not 0 <= lvl <=10):
                await ctx.send('Athena\'s levels can only be between 0 and 10.')
                return
            if not isinstance(lvl, int) or not 0 < lvl <= 50:
                await ctx.send('Levels can only be between 1 and 50.')
        self.Storage.update_levels(ctx.author, comps)
        embed = createEmbed(description=f'Your levels have been updated.', author=ctx.author)
        embed.set_footer(icon_url=ctx.guild.icon_url_as(format='png', size='128'), text='Levels updated')
        await ctx.send(embed=embed)

    
    @matchprofilechannel()
    @commands.command(
        aliases=['set-image'],
        brief='Set a picture for your profile.',
        description='With this command you can set a picture for your profile.\n\
            Make sure your URL ends with \'.png\', \'.jpg\' or \'.gif\'.\n\
            If you want to delete your profile picture, ommit all command arguments.')
    async def img(self, ctx, url: str = None):
        if not url and len(ctx.message.attachments) > 0:
            url = ctx.message.attachments[0].url
        if not url:
            self.Storage.remove_img(ctx.author)
            txt = 'Your profile image has been removed.'
        elif url[-4:] in ['.jpg', '.png', '.gif']:
            self.Storage.update_img(ctx.author, url)
            txt = 'Your profile image has been updated.'
        else: 
            await ctx.send('The image type as to be either jpg, png or gif.')
            return
        embed = createEmbed(description=txt, author=ctx.author)
        embed.set_footer(icon_url=ctx.guild.icon_url_as(format='png', size='128'), text='Image updated')
        await ctx.send(embed=embed)


    @matchprofilechannel()
    @commands.command(
        aliases=['piratename'],
        brief='Set an alias for your pirate.',
        description='With this command you can set an alias for your pirate.\n\
            If you want to remove your alias, ommit all command arguments.'
        )
    async def alias(self, ctx, *, alias: str = None):
        if not alias:
            self.Storage.remove_alias(ctx.author)
            txt = 'Your alias has been removed.'
        else:
            self.Storage.update_alias(ctx.author, alias)
            txt = 'Your alias has been updated.'
        embed = createEmbed(description=txt, author=ctx.author)
        embed.set_footer(icon_url=ctx.guild.icon_url_as(format='png', size='128'), text='Image updated')
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Profile(client))