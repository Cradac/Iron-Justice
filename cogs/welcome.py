import discord
from discord.ext import commands

from utils.utils import createEmbed

class Welcome:
    def __init__(self, client):
        self.client = client

        self.iron = {
            'guild': 479300072077787160,
            'welcome': 479301249351548928,
            'rules': 479301263461449768,
            'info': 563479453091495945,
            'intro': 481455365192548363
        }
        self.rogue = {
            'guild': 455901088164478976,
            'welcome': 459692275522338837,
            'rules': 455903378375966730,
            'rollcall': 460149841050206218,
            'announcements': 469822387567853568,
            'info': 552115652555440149,
            'jenbot': 375060041813983242
        }


    def iron_welcome(self, user: discord.Member):
        description = f'Excelsior! It seems {user.mention} has drunkenly washed ashore onto The Iron Islands!\nOur forces have reached {user.guild.member_count} strong!'
        embed_public = createEmbed(description=description, author=user, guild=user.guild, colour='iron')
        embed_public.set_footer(text=f'#{user.guild.member_count} Ironborn', icon_url=user.guild.icon_url_as(format='png', size=128))

        rules_channel = discord.utils.get(user.guild.channels, id=self.iron['rules'])
        info_channel = discord.utils.get(user.guild.channels, id=self.iron['info'])
        intro_channel = discord.utils.get(user.guild.channels, id=['intro'])
        txt1 = f'Please take a moment to read the {rules_channel.mention} and click the reaction emoji to indicate that you\'ve done so. This will open you up to the application channel.'
        txt2 = f'To apply, submit an application in {intro_channel.mention}.\n\
            Head over to {info_channel.mention} to read up on our FAQ, get our social media links and general info about the fleet.\n\
            Feel free to message a Junior or Senior Officer if you have any questions or need any help.'
        embed_private = createEmbed(guild=user.guild, colour='iron')
        embed_private.set_footer(text=f'#{user.guild.member_count} Ironborn', icon_url=user.guild.icon_url_as(format='png', size=128))
        embed_private.add_field(name=f'Ahoy, {user.name} and welcome to the Iron Fleet!', value=txt1)
        embed_private.add_field(name='Afterwards...', value=txt2)
        return embed_public, embed_private

    def rogue_welcome(self, user: discord.Member):
        jenbot = self.client.get_user(self.rogue['jenbot'])
        description = f'It appears that {user.mention} has decided to go Rogue, and join us Legends!'
        embed = createEmbed(description=description, author=user, guild=user.guild, colour='rogue')
        embed.set_footer(text=f'Member #{user.guild.member_count}', icon_url=user.guild.icon_url_as(format='png', size=128))

        rules_channel = discord.utils.get(user.guild.channels, id=self.rogue['rules'])
        rogueserver_channel = discord.utils.get(user.guild.channels, id=self.rogue['info'])
        rollcall_channel = discord.utils.get(user.guild.channels, id=self.rogue['rollcall'])
        announcements_channel = discord.utils.get(user.guild.channels, id=self.rogue['announcements'])


        rules_txt = f'\
            Please take a moment to read the {rules_channel.mention} & please provide the following information in a message below or to {jenbot.mention} in a PM.\n\n\
            **1.** Gamertag\n\
            **2.** Age\n\
            **3.** Do you stream? (if so please provide streaming channel URL)\n\
            **4.** Ae you an Insider? (Formerly Pioneer)\n\
            **5.** How did you find Rogue Legends?'
        game_txt = f'After you applied and we\'ve set your rank please head to {rogueserver_channel.mention} and react with the emoji according to the games you play to get access to their categories!'
        joined_txt = f'Please leave a message in {rollcall_channel.mention} with the some information about you. Check the pinned message there for format.\n\n\
		Make sure you see the {announcements_channel.mention} channel for important information. (please do not mute the channel)\n\n\
		If you have any questions, comments or concerns please PM {jenbot.mention}'
        embed.add_field(name='__Rules and Server Access__', value=rules_txt)
        embed.add_field(name='__Game Channel Access__', value=game_txt)
        embed.add_field(name='__Once you have Server Access__', value=joined_txt)
        return embed
        

    @commands.Cog.listener()
    async def on_member_join(self, user: discord.Member):
        if not user.bot:
            if user.guild.id == self.iron['guild']:
                embed_public, embed_private = self.iron_welcome(user)
                welcome_channel = discord.utils.get(user.guild.channels, id=self.iron['welcome'])
                try:
                    await user.send(embed=embed_private)
                except discord.errors.Forbidden:
                    pass
            elif user.guild.id == self.rogue['guild']:
                embed_public = self.rogue_welcome(user)
                welcome_channel = discord.utils.get(user.guild.channels, id=self.rogue['welcome'])
            else: 
                return
            await welcome_channel.send(embed=embed_public)

    @commands.Cog.listener()
    async def on_member_remove(self, user: discord.Member):
        if not user.bot:
            if user.guild.id == self.iron['guild']:
                welcome_channel = discord.utils.get(user.guild.channels, id=self.iron['welcome'])
                text = f'Oh my, **{user}** lost their senses during a storm and drowned. Not worthy of being called an Ironborn! What is dead may never die!'
            else:
                return
            await welcome_channel.send(text)


def setup(client):
    client.add_cog(Welcome(client))