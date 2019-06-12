import discord
from discord.ext import commands
import asyncio
from  cogs import auto_voice
from utils.storage import Storage
from utils import utils
from cogs.activity_logging import active_fleets


class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.Storage = Storage()


    @commands.Cog.listener()
    async def on_ready(self):
        guilds = self.Storage.get_all_guilds(self.client)
        for guild in self.client.guilds:
            if guild not in guilds:
                self.Storage.add_guild(guild)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        user = self.client.get_user(member.id)
        can_remove = True
        for guild in self.client.guilds:
            if user in guild.members:
                can_remove = False
        if can_remove:
            self.Storage.user_leave(user)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.Storage.guild_leave(guild)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        embed = utils.createEmbed(
            title='__**The Iron Justice welcomes you!**__',
            description='Hey! I am the Iron Fleet\'s Iron Justice Bot, specifically for Discord Guilds of *Sea of Thieves* Fleets.\
            If you have any questions write a message `Cradac | Max#2614` or type `?help [command|module]`.\n\
            To set up the bot for your server use the `?config <subcommand>` commands (best in an admin-exclusive room) and go through the installation wizard.\n\
            **Please ensure the bot has sufficient rights, at least for the setup!**\n\
            You can set up a message logger by creating a channel called `#message-log`. The bot must be able to see and write in it. This channels should be at least Moderator exclusive!\n\
            Enjoy!',
            colour='iron',
            guild=guild,
            author=guild.owner
        )
        await guild.owner.send(embed=embed)
        role = await guild.create_role(name='lfc', mentionable=True, colour=discord.Color(0xFFFFFF))
        self.Storage.add_guild(guild, role)
    
    '''
        Setup goes through all config step one by one 
    '''
    @commands.command(
        hidden=True
    )
    async def setup(self, ctx):
        pass


    @commands.command(
        name='guild-info',
        aliases=['guildinfo'],
        brief='Gives information about this guild and the setup of the Iron Justice.',
        usage='?guild-info'
    )
    async def guild_info(self, ctx):
        embed = utils.createEmbed(author=ctx.author, guild=ctx.guild, colour='iron')
        guild = ctx.guild
        guild_info = f'**Guild Name:** `{guild.name}`\n**Guild ID:** `{guild.id}`\n**Owner:** {guild.owner.mention}\n**Member Count:** {guild.member_count}'
        embed.add_field(name="__Guild Info__", value=guild_info)

        # Looking for Crew Settings
        lfc_settings = self.Storage.get_lfc_settings(guild)
        lfc_status = '`enabled`' if lfc_settings['status'] else '`disabled`'
        embed.add_field(name='__Looking for Crew Module__', value=lfc_status)
        if lfc_settings['status']:
            lfc_channels = ' '.join(c.mention for c in lfc_settings['channels']) if lfc_settings['channels'] > 0 else 'all channels'
            embed.add_field(name='__Looking for Crew Channels__', value=lfc_channels)
            embed.add_field(name='__Looking for Crew Role__', value=lfc_settings['role'].mention)
        
        # Profile Settings
        profile_settings = self.Storage.get_profile_settings(guild)
        profile_status = '`enabled`' if profile_settings['status'] else '`disabled`'
        embed.add_field(name='___Profile Module__', value=profile_status)
        if profile_settings['status']:
            profile_channels = ' '.join(c.mention for c in profile_settings['channels']) if profile_settings['channels'] > 0 else 'all channels'
            embed.add_field(name='__Profile Channels__' , value=profile_channels)

        # Auto-Voice Settings
        auto_voice_settings = self.Storage.get_auto_voice_settings(guild)
        embed.add_field(name='__Auto-Voice Module__', value=auto_voice_settings['channel'].name or '`disabled`')
        if auto_voice_settings['channel']:
            embed.add_field(name='__Auto-Voice Custom Names__', value=' '.join(f'`{n}`' for n in auto_voice_settings['names']))
        
        # Activity-Logging Settings
        activity_logging_settings = self.Storage.get_activity_logging_status(guild)
        activity_logging_status = '`enabled`' if activity_logging_settings else '`disabled`'
        embed.add_field(name='__Activity-Logging Module__', value=activity_logging_status)


        await ctx.send(embed=embed)


    '''
        config is a command group which over spans `lfc`, `profile` and others.
    '''
    @utils.isAdmin()
    @commands.group(
        aliases=['settings', 'set'],
        brief='Configure the Iron Justice bot for your guild.'
    )
    async def config(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send('Possible modules to configure are:\n• ' + '\n• '.join(c.name for c in ctx.command.commands))
    
    @utils.isAdmin()
    @config.command(
        brief='Configure the LFC-module in your guild.',
        description='You can either pass all arguments or none and be put through a setup wizard.\n\
            If you are asked to mention channels please use the auto complete feature of discord. They need to be clickable in the message.',
        usage='?config lfc [enable|disable] <@role> *[channels]')
    async def lfc(self, ctx, status:bool=None, role: discord.Role=None, channels:commands.Greedy[discord.TextChannel]=None):
        if status is not None:
            self.Storage.update_lfc_status(ctx.guild, status)
            self.Storage.update_lfc_role(ctx.guild, role)
            if channels and status:
                self.Storage.add_lfc_channels(ctx.guild, channels)
            else:
                self.Storage.delete_all_lfc_channels(ctx.guild)


        # WIZARD
        else:
            def reaction_check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) in ["✅", "❌"]
            # Turn on or off
            msg = await ctx.send('Do you want to enable the `Looking for Crew`-Module? Please react below.')
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            try:
                r = await self.client.wait_for('reaction_add', timeout=30.0, check=reaction_check)
            except asyncio.TimeoutError:
                await ctx.send('Cancelled the Setup.')
            status = str(r[0]) == '✅'
            self.Storage.update_lfc_status(ctx.guild, status)
            s = 'on' if status else 'off'
            await ctx.send(f'The `Looking for Crew`-Module is now turned {s}.')
            
            if status:
                def message_check(msg):
                    return msg.author == ctx.author and msg.content
                
                #Select lfc role
                await ctx.send('Which role should be used as a `Looking for Crew` role?')
                try:
                    msg = await self.client.wait_for('message', timeout=60.0, check=message_check)
                except asyncio.TimeoutError:
                    await ctx.send('Cancelled the Setup.')
                role = await utils.roleSearch(ctx, self.client, msg)
                self.Storage.update_lfc_role(ctx.guild, role)
                await ctx.send(f'{role.mention} will now be used for the `Looking for Crew`-Module.')

                # Select channels
                await ctx.send('Please mention all channels you want to enable the module in. If you don\'t want to restrict it to certain channels just type `all`.')
                try:
                    msg = await self.client.wait_for('message', timeout=60.0, check=message_check)
                except asyncio.TimeoutError:
                    await ctx.send('Cancelled the Setup.')
                channels = msg.channel_mentions
                if len(channels) > 0:
                    self.Storage.add_lfc_channels(ctx.guild, msg.channel_mentions)
                    await ctx.send('The `Looking for Crew`-Module can be used in all mentioned channels.')
                else:
                    self.Storage.delete_all_lfc_channels(ctx.guild)
                    await ctx.send('The `Looking for Crew`-Module can be used in all channels.')
            else:
                self.Storage.delete_all_lfc_channels(ctx.guild)

        # Send Settings Embed
        s = 'enabled' if status else 'disabled'
        embed = utils.createEmbed(title='**__`Looking for Crew`-Setup__**', description=f'The module is {s}.', colour='iron', guild=ctx.guild)
        ch = '`all`' if len(channels) == 0 else ' '.join(c.mention for c in channels)
        embed.add_field(name='__Role__', value=role.mention)
        embed.add_field(name='__Channels__', value=ch)
        await ctx.send(embed=embed)

    @utils.isAdmin()
    @config.command(
        brief='Configure the Profile-module in your guild.',
        description='You can either pass all arguments or none and be put through a setup wizard.\n\
            If you are asked to mention channels please use the auto complete feature of discord. They need to be clickable in the message.',
        usage='?config profile [enable|disable] *[channels]'
    )
    async def profile(self, ctx, status:bool=None, channels:commands.Greedy[discord.TextChannel]=None):
        if status is not None:
            self.Storage.update_profile_status(ctx.guild, status)
            if channels and status:
                self.Storage.add_profile_channels(ctx.guild, channels)
            else:
                self.Storage.delete_all_profile_channels(ctx.guild)

        # WIZARD
        else:
            def reaction_check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) in ["✅", "❌"]
            # Turn on or off
            msg = await ctx.send('Do you want to enable the `Profile`-Module? Please react below.')
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            try:
                r = await self.client.wait_for('reaction_add', timeout=30.0, check=reaction_check)
            except asyncio.TimeoutError:
                await ctx.send('Cancelled the Setup.')
            status = str(r[0]) == '✅'
            self.Storage.update_profile_status(ctx.guild, status)
            s = 'on' if status else 'off'
            await ctx.send(f'The `Profile`-Module is now turned {s}.')
            
            if status:
                def message_check(msg):
                    return msg.author == ctx.author and msg.content
                # Select channels
                await ctx.send('Please mention all channels you want to enable the module in. If you don\'t want to restrict it to certain channels just type `all`.')
                try:
                    msg = await self.client.wait_for('message', timeout=60.0, check=message_check)
                except asyncio.TimeoutError:
                    await ctx.send('Cancelled the Setup.')
                channels = msg.channel_mentions
                if len(channels) > 0:
                    self.Storage.add_profile_channels(ctx.guild, msg.channel_mentions)
                    await ctx.send('The `Profile`-Module can be used in all mentioned channels.')
                else:
                    self.Storage.delete_all_profile_channels(ctx.guild)
                    await ctx.send('The `Profile`-Module can be used in all channels.')
            else:
                self.Storage.delete_all_profile_channels(ctx.guild)

    # Send Settings Embed
    s = 'enabled' if status else 'disabled'
    embed = utils.createEmbed(title='**__`Profile`-Setup__**', description=f'The module is {s}.', colour='iron', guild=ctx.guild)
    ch = '`all`' if len(channels) == 0 else ' '.join(c.mention for c in channels)
    embed.add_field(name='__Channels__', value=ch)
    await ctx.send(embed=embed)

    @utils.isAdmin()
    @config.command(
        name='auto-voice',
        brief='Configure the Auto-Voice-module in your guild.',
        description='Here you set the voice channel, which acts as a `join here` channel and then redirects you to your own voice channel.\n\
            Please either pass the whole and correct voice channel name or the channel\'s id.\n\
            If you want to disable it, ommit the channel parameter.',
        usage='?config auto-voice <Voice Channel>'
    )
    async def auto_voice(self, ctx, *, channel:discord.VoiceChannel = None):
        self.Storage.update_auto_voice_channel(ctx.guild, channel) #TODO does this work with None?
        if channel:
            await ctx.send(f'\
                Set the channel `{channel.name}` as Auto-Voice Channel.\n\
                If you want to add custom names please use the `?auto-voice-names add <names>` command.')
        else:
            await ctx.send('Auto-Voice has been disabled.')
        

    @auto_voice.error
    async def auto_voice_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Voice channel could not be found. Either use the channel ID or the full name.')
    
    @utils.isAdmin()
    @config.command(
        name='activity-logging',
        brief='Configure the Activity-Logging Module in your guild.',
        decription='You can enable or disable the activity logging status for your guild.\n\
            If you do not use this module, please disable it as it\'s quite heavy on the clients ressource usage.',
        usage='?config activity-logging [enable|disable]'
    )
    async def activity_logging(self, ctx, status:bool):
        self.Storage.update_activity_logging_status(ctx.guild, status)
        s = 'enabled' if status else 'disabled'
        global active_fleets
        active_fleets.add(ctx.guild) if status else active_fleets.discard(ctx.guild)
        embed = utils.createEmbed(title='**__`Activity-Logging`-Setup__**', description=f'The module is {s}.', colour='iron', guild=ctx.guild)
        await ctx.send(embed=embed)



    '''
        Command Group to add and remove names to the voice channel list.
        Default removes all added names and uses the default name list.
    '''
    @utils.isAdmin()
    @commands.group(
        name='auto-voice-names',
        brief='Add, remove or view custom names for the `Auto-Voice`-Module.',
        usage='?auto-voice-names [get|add|delete|default] *[args]'
    )
    async def auto_voice_names(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send('Possible subcommands to invoke are:\n• ' + '\n• '.join(c.name for c in ctx.command.commands))
    
    @utils.isAdmin()
    @auto_voice_names.command(
        brief='Show a list of all names used for voice channel generation.',
        description='Show a list of all names used for voice channel generation. Shows the default names if none are set.',
        usage='?auto-voice-names get'
    )
    async def get(self, ctx):
        l = self.Storage.get_auto_voice_names(ctx.guild)
        l = l if len(l) > 0 else auto_voice.channel_names
        embed = utils.createEmbed(title='__**List of voice channel names**__', description='• ' + '\n• '.join(l), colour='iron', author=ctx.author, guild=ctx.guild)
        await ctx.send(embed=embed)
    
    @utils.isAdmin()
    @auto_voice_names.command(
        brief='Add names for voice channel generation.',
        description='Add names to your custom voice channel name list. You can add multiple names at a time. Use `,` to seperate names.',
        usage='?auto-voice-names add <name1,name2,...>'
    )
    async def add(self, ctx, *, names):
        names = [name.trim() for name in names.split(',')]
        self.Storage.add_auto_voice_names(ctx.guild, names)
        await ctx.invoke(self.client.get_command('auto_voice_names get'))
    
    @utils.isAdmin()   
    @auto_voice_names.command(
        aliases=['remove'],
        description='Delete names out of your custom list of voice channel names. You can delete multiple names at a time. Use `,` to seperate names.',
        usage='?auto-voice-names delete <name1,name2,...>'
    )
    async def delete(self, ctx, *, names):
        names = [name.trim() for name in names.split(',')]
        self.Storage.delete_auto_voice_names(ctx.guild, names)
        await ctx.invoke(self.client.get_command('auto_voice_names get'))
    
    @utils.isAdmin()
    @auto_voice_names.command()
    async def default(self, ctx):
        self.Storage.delete_all_auto_voice_names(ctx.guild)
        await ctx.send('The Auto-Voice-Channel name list has been set to default. All your custom names have been deleted.')


def setup(client):
    client.add_cog(Settings(client))