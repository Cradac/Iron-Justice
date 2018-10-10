import discord
from discord.ext import commands
import asyncio
import sqlite3
from sqlite3 import Error 
from cogs.checks import isGod, isAdmin, isMod
from cogs.checks import create_connection, db_file

class RogueLegends:
    def __init__(self, client):
        self.client = client



def setup(client):
    client.add_cog(RogueLegends(client))