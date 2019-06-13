import discord
from discord.ext import commands
from utils.storage import Storage
from utils import utils
import asyncio, re, xbox

Utils = utils.Utils()

xbox.client.authenticate('max.dettmann@web.de', 'RexAnton#2017')

class Profile(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.Storage = Storage()
        self.profile_messages = dict()
        self.profile_status = dict()

        self.steam_emoji = None
        self.xbox_emoji = None
        self.psn_emoji = None
        self.nintendo_emoji = None
        self.minecraft_emoji = None
        self.origin_emoji = None
        self.blizzard_emoji = None
        self.bethesda_emoji = None

        self.twitch_emoji = None
        self.mixer_emoji = None
        self.youtube_emoji = None
        self.twitter_emoji = None
        self.reddit_emoji = None
        self.itchio_emoji = None

        self.social_emoji = None
        self.sot_emoji = None
        self.game_emoji = '🎮'
        self.game_emoji_url = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/146/video-game_1f3ae.png'
        self.stop_emoji = '⏹'
        
        self.emojis = list()

    @commands.Cog.listener()
    async def on_ready(self):
        self.steam_emoji = self.client.get_emoji(586475562772725780)
        self.xbox_emoji = self.client.get_emoji(563799115201249301)
        self.psn_emoji = self.client.get_emoji(563799160021712922)
        self.nintendo_emoji = self.client.get_emoji(534433688025563137)
        self.minecraft_emoji = self.client.get_emoji(588661530661355520)
        self.origin_emoji = self.client.get_emoji(588661018784301066)
        self.blizzard_emoji = self.client.get_emoji(588661019258126357)
        self.bethesda_emoji = self.client.get_emoji(588661017287065600)

        self.sot_emoji = self.client.get_emoji(488445174536601600)
        self.social_emoji = self.client.get_emoji(588748681365422110)

        self.twitch_emoji = self.client.get_emoji(588661018557808641)
        self.mixer_emoji = self.client.get_emoji(588661020591915021)
        self.youtube_emoji = self.client.get_emoji(588661163152375808)
        self.twitter_emoji = self.client.get_emoji(588661019270709248)
        self.reddit_emoji = self.client.get_emoji(588661023079399424)
        self.itchio_emoji = self.client.get_emoji(588661018394099722)

        self.emojis = [self.xbox_emoji, self.sot_emoji, self.game_emoji, self.social_emoji, self.stop_emoji]

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        if user.bot:
            return
        if reaction.message.id in self.profile_messages.keys() and reaction.emoji in self.emojis:
            await reaction.remove(user)
            if reaction.emoji == self.xbox_emoji and self.profile_status[reaction.message.id] != 'xbox':
                embed = self.get_xbox_page(self.profile_messages[reaction.message.id])
                self.profile_status[reaction.message.id] = 'xbox'

            elif reaction.emoji == self.sot_emoji and self.profile_status[reaction.message.id] != 'sot':
                embed = await self.get_sot_page(None, self.profile_messages[reaction.message.id])
                self.profile_status[reaction.message.id] = 'sot'

            elif reaction.emoji == self.game_emoji and self.profile_status[reaction.message.id] != 'game':
                embed = await self.get_game_page(None, self.profile_messages[reaction.message.id])
                self.profile_status[reaction.message.id] = 'game'

            elif reaction.emoji == self.social_emoji and self.profile_status[reaction.message.id] != 'social':
                embed = await self.get_social_page(None, self.profile_messages[reaction.message.id])
                self.profile_status[reaction.message.id] = 'social'
            elif reaction.emoji == self.stop_emoji:
                await self.reaction_menu_timeout(reaction.message, wait=False)
                return
            else:
                return
            await reaction.message.edit(embed=embed)

    async def reaction_menu_timeout(self, message: discord.Message, wait: bool = True):
        if wait:
            await asyncio.sleep(300)
        await message.clear_reactions()
        del self.profile_messages[message.id]
        del self.profile_status[message.id]

    async def prepare_reaction_menu(self, message: discord.Message):
        for emoji in self.emojis:
            await message.add_reaction(emoji)
        self.client.loop.create_task(self.reaction_menu_timeout(message))
        

    def get_xbox_page(self, member: discord.Member):
        gtag = self.Storage.get_xbox_tag(member)
        embed = utils.createEmbed(colour='iron', author=member)
        icon = member.guild.icon_url_as(format='png', size=512)
        embed.set_thumbnail(url=icon)
        embed.set_footer(icon_url=self.xbox_emoji.url, text='Xbox')
        if gtag:
            xbox_profile = xbox.GamerProfile.from_gamertag(gtag)
            embed.add_field(name='__Gamertag__', value=xbox_profile.gamertag)
            embed.add_field(name='__Gamerscore__', value=xbox_profile.gamerscore)
            embed.set_image(url=xbox_profile.gamerpic)
        else:
            embed.description = 'There is no Xbox Gamertag set for this profile.\n\
                If this is your profile you can add it with `?gt edit <gamertag>`.'
        return embed

    async def get_sot_page(self, ctx: commands.Context, member: discord.Member):
        info = await self.Storage.get_sot_profile(ctx, member)
        embed = utils.createEmbed(colour='iron', author=member, guild=member.guild)
        embed.set_footer(icon_url=self.sot_emoji.url, text='Sea of Thieves')
        embed.add_field(name="<:xbox:563799115201249301> Gamertag", value=info['gtag'], inline=False)
        if info['alias']:
            embed.add_field(name="<:jollyroger:486619773875126293> Pirate Alias", value=info['alias'], inline=False)
        embed.add_field(name="<:rank:486619774445551626> Rank", value=member.top_role.name, inline=False)
        embed.add_field(name="<:gh:486619774424449036> Gold Hoarders", value=info['gh'], inline=True)
        embed.add_field(name="<:oos:486619776593166336> Order of Souls", value=info['oos'], inline=True)
        embed.add_field(name="<:ma:486619774688952320> Merchant Alliance", value=info['ma'], inline=True)
        embed.add_field(name="<:hc:588378278772080641>  Hunter's Call", value=info['hc'], inline=True)
        embed.add_field(name="<:sd:588378278813761609> Sea Dogs", value=info['sd'], inline=True)
        embed.add_field(name="<:af:486619774122459178> Athena's Fortune", value=info['af'], inline=False)
        if info['img']:
            embed.set_image(url=info['img'])
        alliances = [info['gh'] == 50, info['oos'] == 50, info['ma'] == 50, info['hc'] == 50, info['sd'] == 50]
        true_count = sum(alliances)
        if true_count >= 3:
            embed.add_field(name="You are a Legend!", value='\u200b', inline=False)
        return embed

    async def get_game_page(self, ctx, member: discord.Member):
        info = await self.Storage.get_tag_profile(ctx, member)
        embed = utils.createEmbed(colour='iron', author=member)
        embed.set_thumbnail(url=member.guild.icon_url_as(format='png', size=512))
        embed.set_footer(icon_url=self.game_emoji_url, text='Gamertags')
        if info['steam']:
            embed.add_field(name=str(self.steam_emoji) + 'Steam', value=info['steam'], inline=True)
        if info['xbox']:
            embed.add_field(name=str(self.xbox_emoji) + 'Xbox Live', value=info['xbox'], inline=True)
        if info['psn']:
            embed.add_field(name=str(self.psn_emoji) + 'Playstation Network', value=info['psn'], inline=True)
        if info['nintendo']:
            embed.add_field(name=str(self.nintendo_emoji) + 'Nintendo Friend Code', value=info['nintendo'], inline=True)
        if info['minecraft']:
            embed.add_field(name=str(self.minecraft_emoji) + 'Minecraft', value=info['minecraft'], inline=True)
        if info['origin']:
            embed.add_field(name=str(self.origin_emoji) + 'Origin', value=info['origin'], inline=True)
        if info['blizzard']:
            embed.add_field(name=str(self.blizzard_emoji) + 'Blizzard Net', value=info['blizzard'], inline=True)
        if info['bethesda']:
            embed.add_field(name=str(self.bethesda_emoji) + 'Bethesda', value=info['bethesda'], inline=True)
        if len(embed.fields) == 0:
            embed.description = f'{member} has not set any gamertags.'
            
        return embed

    async def get_social_page(self, ctx, member: discord.Member):
        info = await self.Storage.get_social_profile(ctx, member)
        embed = utils.createEmbed(colour='iron', author=member)
        embed.set_thumbnail(url=member.guild.icon_url_as(format='png', size=512))
        embed.set_footer(icon_url=self.social_emoji.url, text='Social Media')
        if info['twitch']:
            embed.add_field(name=str(self.twitch_emoji) + 'Twitch', value=f'[{info["twitch"]}](https://www.twitch.tv/{info["twitch"]})', inline=True)
        if info['youtube']:
            embed.add_field(name=str(self.youtube_emoji) + 'Youtube', value=info['youtube'], inline=True)
        if info['mixer']:
            embed.add_field(name=str(self.mixer_emoji) + 'Mixer', value=info['mixer'], inline=True)
        if info['twitter']:
            embed.add_field(name=str(self.twitter_emoji) + 'Twitter', value=info['twitter'], inline=True)
        if info['reddit']:
            embed.add_field(name=str(self.reddit_emoji) + 'Reddit', value=info['reddit'], inline=True)
        if info['itchio']:
            embed.add_field(name=str(self.itchio_emoji) + 'Itch.io', value=info['itchio'], inline=True)
        if len(embed.fields) == 0:
            embed.description = f'{member} has not set any social media names.'

        return embed


    @Utils.matchProfileChannel()
    @commands.command(
        brief='Shows a member\' profile.',
        description='This command shows a member\'s profile.\n\
            You can navigate the pages with the reaction menu for 5 minutes. If you are done please click the `STOP` emoji.',
        usage='?profile [member]'
    )
    async def profile(self, ctx, *, member: str = None):
        member = await utils.memberSearch(ctx, self.client, member) if member else ctx.message.author
        if not member:
            return
        embed = await self.get_sot_page(ctx, member)
        msg = await ctx.send(embed=embed)
        await self.prepare_reaction_menu(msg)
        self.profile_messages[msg.id] = member
        self.profile_status[msg.id] = 'sot'



    @Utils.matchProfileChannel()
    @commands.group(
        brief='Show your own Gamertag',
        description='This command shows the Gamertag page of the profile.\n\
            There are some subcommands to alter your gamertags or show someone elses gamertags.\n\
            You can navigate the pages with the reaction menu for 5 minutes. If you are done please click the `STOP` emoji.',
        usage='?gt [edit|show] [*args]'
    )
    async def gt(self, ctx):
        if not ctx.invoked_subcommand:
            embed = await self.get_game_page(ctx, ctx.author)
            msg = await ctx.send(embed=embed)
            await self.prepare_reaction_menu(msg)
            self.profile_messages[msg.id] = ctx.author
            self.profile_status[msg.id] = 'game'

    @Utils.matchProfileChannel()
    @gt.command(
        brief='Edit your one of your gamertags.',
        description='Use this to edit your gamertag.\n\
            You can choose of these platforms: `steam`, `xbox`, `psn`, `nintendo`, `minecraft`, `origin`, `blizzard`, `bethesda`.',
        usage='?gt edit <platform> <gamertag>'
    )
    async def edit(self, ctx, platform: str , *, gamertag):
        platforms = ['steam', 'xbox', 'psn', 'nintendo', 'minecraft', 'origin', 'blizzard', 'bethesda']
        if platform not in platforms:
            embed = utils.createEmbed(author=ctx.author, colour='error', description=f'You need to select one of these platforms:\n• `' + '`\n• `'.join(platforms) + '`')
            await ctx.send(embed=embed)
            return
        self.Storage.update_gamertag(ctx.author, platform, gamertag)
        embed = utils.createEmbed(description=f'Your {platform} gamertag has been updated to `{gamertag}`.', author=ctx.author, colour='iron')
        embed.set_footer(icon_url=ctx.guild.icon_url_as(format='png', size=128), text='Gamertag updated')
        await ctx.send(embed=embed)


    @Utils.matchProfileChannel()
    @gt.command(
        brief='Show another member\'s gamertag profile page.',
        description='This command can show another member\'s gamertag.',
        usage='?gt show <member>',
        aliases=['see', 'search']
    )
    async def show(self, ctx, *, member: str):
        member = await utils.memberSearch(ctx, self.client, member) if member else ctx.message.author
        if not member:
            return
        embed = await self.get_game_page(ctx, member)
        msg = await ctx.send(embed=embed)
        await self.prepare_reaction_menu(msg)
        self.profile_messages[msg.id] = member
        self.profile_status[msg.id] = 'game'


    @Utils.matchProfileChannel()
    @commands.command(
        aliases=['lvl'],
        brief='Update your Ingame Levels.',
        description='Use this command to regularly update your levels.\ngh: Gold Hoarders\noos: Order of Souls\nma: Merchant Aliance\nhc: Hunter\'s Call\nsd: Sea Dogs\naf: Athena\'s Fortune',
        usage='?levels *[<company>=<level>]'
    )
    async def levels(self, ctx, *args):
        comps = dict()
        r = re.compile(r'^(([a-z]|[A-Z]){1,3}=([1-4][0-9]|50|[1-9])\s)*$')
        if not r.match(' '.join(args) + ' '):
            await ctx.send('The Syntax is not correct. Try this instead:\n`?levels gh=50`\n`?levels af=10 hc=50 gh=50 sd=50 ma=50 oos=50`')
            return
        for arg in args:
            arg = arg.split('=')
            try:
                comps[arg[0].lower()] = int(arg[1])
            except ValueError:
                await ctx.send('Please only pass integers for levels.')
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
        embed = utils.createEmbed(description=f'Your levels have been updated.', author=ctx.author, colour='iron')
        embed.set_footer(icon_url=ctx.guild.icon_url_as(format='png', size=128), text='Levels updated')
        await ctx.send(embed=embed)

    
    @Utils.matchProfileChannel()
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
            txt = 'Your profile image has been removed.'
        elif url[-4:] in ['.jpg', '.png', '.gif']:
            txt = 'Your profile image has been updated.'
        else:
            await ctx.send('The image type as to be either jpg, png or gif.')
            return
        self.Storage.update_img(ctx.author, url)
        embed = utils.createEmbed(description=txt, author=ctx.author, colour='iron')
        embed.set_footer(icon_url=ctx.guild.icon_url_as(format='png', size=128), text='Image updated')
        await ctx.send(embed=embed)


    @Utils.matchProfileChannel()
    @commands.command(
        aliases=['piratename'],
        brief='Set an alias for your pirate.',
        description='With this command you can set an alias for your pirate.\n\
            If you want to remove your alias, ommit all command arguments.'
        )
    async def alias(self, ctx, *, alias: str = None):
        if not alias:
            txt = 'Your alias has been removed.'
        else:
            txt = 'Your alias has been updated.'
        self.Storage.update_alias(ctx.author, alias)
        embed = utils.createEmbed(description=txt, author=ctx.author, colour='iron')
        embed.set_footer(icon_url=ctx.guild.icon_url_as(format='png', size=128), text='Image updated')
        await ctx.send(embed=embed)


    @Utils.matchProfileChannel()
    @commands.group(
        brief='Show your own Social Tab.',
        description='This command shows the Social page of the profile.\n\
            There are some subcommands to alter your Social Media names or show someone elses Social Page.\n\
            You can navigate the pages with the reaction menu for 5 minutes. If you are done please click the `STOP` emoji.',
        usage='?social [edit|show] [*args]'
    )
    async def social(self, ctx):
        if not ctx.invoked_subcommand:
            embed = await self.get_social_page(ctx, ctx.author)
            msg = await ctx.send(embed=embed)
            await self.prepare_reaction_menu(msg)
            self.profile_messages[msg.id] = ctx.author
            self.profile_status[msg.id] = 'social'

    @Utils.matchProfileChannel()
    @social.command(
        name='edit',
        brief='Edit your one of your Social Media Platforms.',
        description='Use this to edit one of your Social Media names.\n\
            You can choose of these platforms: `twitch`, `mixer`, `youtube`, `twitter`, `reddit`, `itchio`.',
        usage='?social edit <platform> <username>'
    )
    async def _s_edit(self, ctx, platform: str , *, username):
        platforms = ['twitch', 'mixer', 'youtube', 'twitter', 'reddit', 'itchio']
        if platform not in platforms:
            embed = utils.createEmbed(author=ctx.author, colour='error', description=f'You need to select one of these platforms:\n• `' + '`\n• `'.join(platforms) + '`')
            await ctx.send(embed=embed)
            return
        self.Storage.update_social_media(ctx.author, platform, username)
        embed = utils.createEmbed(description=f'Your {platform} gamertag has been updated to `{username}`.', author=ctx.author, colour='iron')
        embed.set_footer(icon_url=ctx.guild.icon_url_as(format='png', size=128), text='Username updated')
        await ctx.send(embed=embed) 


    @Utils.matchProfileChannel()
    @social.command(
        name='show',
        brief='Show another member\'s Social Media page.',
        description='This command can show another member\'s social media names.',
        usage='?social show <member>',
        aliases=['see', 'search']
    )
    async def _s_show(self, ctx, *, member: str):
        member = await utils.memberSearch(ctx, self.client, member) if member else ctx.message.author
        if not member:
            return
        embed = await self.get_social_page(ctx, member)
        msg = await ctx.send(embed=embed)
        await self.prepare_reaction_menu(msg)
        self.profile_messages[msg.id] = member
        self.profile_status[msg.id] = 'social'

def setup(client):
    client.add_cog(Profile(client))