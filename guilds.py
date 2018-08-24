import discord

class Guilds:
    def __init__(self, guild_name, guild_id, enabled, lfc_channels, profile_channels):
        self.guild_name = guild_name
        self.guild_id = guild_id
        self.enabled = enabled                      #dict
        self.lfc_channels = lfc_channels            #list
        self.profile_channels = profile_channels    #list