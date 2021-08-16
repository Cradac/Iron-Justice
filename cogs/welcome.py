import discord
from discord.ext import commands
from utils import utils


class Welcome(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.iron = dict()
        self.rogue = dict()
        

    @commands.Cog.listener()
    async def on_ready(self):
        iron_guild = self.client.get_guild(479300072077787160)
        self.iron = {
            'guild': iron_guild,
            'welcome': iron_guild.get_channel(684390600598093862),
            'rules': iron_guild.get_channel(684390479491760161),
            'info': iron_guild.get_channel(684390511980838922),
            'intro': iron_guild.get_channel(684390743086858290)
        }
        if any(self.iron.values()) is None:
            print('Didn\'t get a channel in the Iron Fleet.')
        rogue_guild = self.client.get_guild(455901088164478976)
        self.rogue = {
            'guild': rogue_guild,
            'welcome': rogue_guild.get_channel(459692275522338837),
            'rules': rogue_guild.get_channel(455903378375966730),
            'rollcall': rogue_guild.get_channel(460149841050206218),
            'announcements': rogue_guild.get_channel(469822387567853568),
            'info': rogue_guild.get_channel(552115652555440149),
            'jenbot': rogue_guild.get_member(565661828474994698)
        }
        if any(self.rogue.values()) is None:
            print('Didn\'t get a channel in the Iron Fleet.')
        print('Got all welcome guilds and channels.')
        hogf_guild = self.client.get_guild(628663547647229982)
        self.hogf = {
            'guild': hogf_guild,
            'rules': hogf_guild.get_channel(676562579719454739),
            'guide': hogf_guild.get_channel(646204949281374225),
            'welcome': hogf_guild.get_channel(628663547647229984),
        }



    def iron_welcome(self, user: discord.Member):
        description = f'Excelsior! It seems {user.mention} has drunkenly washed ashore onto The Iron Islands!\nOur forces have reached {user.guild.member_count} strong!'
        embed_public = utils.createEmbed(description=description, author=user, guild=user.guild, colour='iron')
        embed_public.set_footer(text=f'#{user.guild.member_count} Ironborn', icon_url=user.guild.icon_url_as(format='png', size=128))

        #txt1 = f'Please take a moment to read the {self.iron["rules"].mention} and click the reaction emoji to indicate that you\'ve done so. This will open you up to the application channel.'
        #txt2 = f'To apply, submit an application in {self.iron["intro"].mention}.\n\
           # Head over to {self.iron["info"].mention} to read up on our FAQ, get our social media links and general info about the fleet.\n\
           # Feel free to message a Junior or Senior Officer if you have any questions or need any help.'
        #embed_private = utils.createEmbed(guild=user.guild, colour='iron')
        #embed_private.set_footer(text=f'#{user.guild.member_count} Ironborn', icon_url=user.guild.icon_url_as(format='png', size=128))
        #embed_private.add_field(name=f'Ahoy, {user.name} and welcome to the Iron Fleet!', value=txt1)
        #embed_private.add_field(name='Afterwards...', value=txt2)
        return embed_public

    def rogue_welcome(self, user: discord.Member):
        embed = utils.createEmbed(description='', author=user, guild=user.guild, colour='rogue')
        embed.set_footer(text=f'Member #{user.guild.member_count}', icon_url=user.guild.icon_url_as(format='png', size=128))
        embed.description = f'\
            It appears that {user.mention} has decided to go Rogue, and join us Legends!\n\n\
            Please take a moment to read and accept the {self.rogue["rules"].mention} & please provide the following information in a message below so we can set your roles.\n\n\
            **1.** How did you find us?\n\
            **2.** Age\n\
            **3.** Do you stream? (if so please provide streaming channel URL)\n\
            **4.** Are you an Insider? (Formerly Pioneer)\n\n'
        return embed

    def hogf_welcome(self, user: discord.Member):
        embed = utils.createEmbed(author=user, guild=user.guild, colour=0xffb53b)
        embed.description = f'Welcome to Hearts of Gold. Please review the {self.hogf["rules"].mention} and use the reaction role to agree to them. Once you have done this please make sure you familirize yourself with the {self.hogf["guide"].mention}. If you have any questions please ask an HoGF Admin or Mod.'
        embed.set_footer(text=f'Member #{user.guild.member_count}', icon_url=user.guild.icon_url_as(format='png', size=128))
        return embed

        

    @commands.Cog.listener()
    async def on_member_join(self, user: discord.Member):
        if not user.bot:
            if user.guild == self.iron['guild']:
                embed_public = self.iron_welcome(user)
                welcome_channel = self.iron['welcome']
                #try:
                #await user.send(embed=embed_private)
                #except discord.errors.Forbidden:
                #    pass
            elif user.guild == self.rogue['guild']:
                embed_public = self.rogue_welcome(user)
                welcome_channel = self.rogue['welcome']
            elif user.guild == self.hogf['guild']:
                embed_public = self.hogf_welcome(user)
                welcome_channel = self.hogf['welcome']
            else: 
                return
            await welcome_channel.send(embed=embed_public)

    @commands.Cog.listener()
    async def on_member_remove(self, user: discord.Member):
        if not user.bot:
            if user.guild == self.iron['guild']:
                welcome_channel = self.iron['welcome']
                text = f'Oh my, **{user}** lost their senses during a storm and drowned. Not worthy of being called an Ironborn! What is dead may never die!'
            else:
                return
            await welcome_channel.send(text)

    @utils.isMod()
    @commands.command(
        brief='Test the welcome message.',
        description='A command to test the welcome message.',
        usage='?welcome <channel>'
    )
    async def welcome(self, ctx, channel: discord.TextChannel):
        if ctx.guild == self.iron['guild']:
            embeds = self.iron_welcome(ctx.author)
        elif ctx.guild == self.rogue['guild']:
            embeds = self.rogue_welcome(ctx.author)
        elif ctx.guild == self.hogf['guild']:
            embeds = self.hogf_welcome(ctx.author)
        else:
            app_info = await self.client.application_info()
            await ctx.send(f'There is no custom welcome message set for your guild. Contact {app_info.owner}.')
            return
        for embed in embeds:
            await channel.send(embed=embed)


def setup(client):
    client.add_cog(Welcome(client))
