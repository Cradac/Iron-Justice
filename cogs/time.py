import discord
from discord.ext import commands
from utils import time
import typing


class Time_Conversion(commands.Cog, name='Time-Conversion'):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def time_zone(self, ctx, time_str: str, d_n: typing.Optional[str] = None, time_zone: str = 'GMT'):
        if d_n:
            time_str += ' ' + d_n
        gmt_time = time.calc_time(ctx, time_str, time_zone)
        if not gmt_time:
            return
        await ctx.send(f'The GMT time is: {gmt_time}')
        


def setup(client):
    client.add_cog(Time_Conversion(client))