import discord
from utils import createEmbed
#import mysql


class Storage:
    
    def __init__(self):
        self.conn = None
        '''
        self.conn = mysql.connector.connect(
            host="localhost",
            user=Configuration.DBUsername,
            passwd=Configuration.DBPassword,
            database=Configuration.DBName
        )'''

    
    def get_cursor(self):
        try:
            cursor = self.conn.cursor()
            return cursor
        except Exception as e:
            raise e

    def execute_query(self, query: str, commit: bool = False):
        
        cur = self.conn.get_cursor()
        cur.execute(query)
        if commit:
            self.conn.commit()
        r = cur.fetchall()
        cur.close()
        return r

    def add_server(self, guild: discord.Guild):
        query = f'INSERT INTO settings (gid) VALUES ({guild.id})'
        self.execute_query(query)


    async def get_sot_profile(self, ctx, user: discord.Member):
        query = f'SELECT hc,sd,gh,oos,ma,af,img,alias FROM sot_profile WHERE uid={user.id};'
        cur = self.execute_query(query)
        r = cur.fetchone()

        #If Profile doesn't exist yet
        if cur.rowcount == 0:
            await self.create_profile(ctx, user)
            return

        profile = {
            'hc': r[0],
            'sd': r[1],
            'gh': r[2],
            'oos': r[3],
            'ma': r[4],
            'af': r[5],
            'img': r[6],
            'alias': r[7],
        }
        query = f'SELECT xbox FROM gamertags WHERE uid={user.id};'
        cur.execute(query)
        r = cur.fetchone()
        profile['gtag'] = r[0]
        return profile

    def get_tag_profile(self, user: discord.Member):
        query = f'SELECT steam,xbox,psn,nintendo FROM gamertags WHERE uid={user.id};'
        cur = self.execute_query(query)
        r = cur.fetchone()
        profile = {
            'steam': r[0],
            'xbox': r[1],
            'psn': r[2],
            'nintendo': r[3],
        }
        return profile

    def get_xbox_tag(self, user: discord.Member):
        query = f'SELECT xbox FROM gamertags WHERE uid={user.id};'
        cur = self.execute_query(query)
        r = cur.fetchone()
        return r[0]

    async def create_profile(self, ctx, user: discord.Member):
        query = f'INSERT INTO sot_profile (uid) VALUES ({user.id});'
        self.execute_query(query)                                                #CAN I ONLY COMMIT ONCE?
        query = f'INSERT INTO gamertags (uid) VALUES ({user.id});'
        self.execute_query(query, commit=True)
        embed = createEmbed(title='**__Profile Created__**', colour='iron', author=user)
        embed.add_field(name="__add your information__", value="1. Add your XBox gamertag with `?gt edit <gamertag>`.\n2. Add your levels with `?levels gh=<gh> oos=<oos>` etc... Use `?help levels` for more info.", inline=False)
        embed.add_field(name="__optional features__", value="- Add an image of your pirate with `?set_image <URL>`. You can also upload the image right to discord and type `?set_image` without any paramters.\nThis URL **NEEDS** to be a direct link to the image ending with `.jpg`, `.png` or `.gif`.\n- Add a pirate name (for role players) by typing `?alias <piratename>`.", inline=False)
        embed.add_field(name="__additional notes__", value="Please note that you **DO NOT** need to add the brackets (`<>`, `[]`). They are merely Syntax to show which arguments are mandatory (`<>`) and which can be left out and will use the previous value (`[]`). This is programming standard.", inline=False)
        await ctx.send(embed=embed)

    def update_levels(self, user: discord.Member, comps: dict):
        
        cur = self.get_cursor()
        cur.executemany(f'UPDATE profile SET %s=%s WHERE uid={user.id}', comps.items())
        self.conn.commit()
        cur.close()

    def update_gamertag(self, user: discord.Member, platform: str, gamertag: str):
        query = f'UPDATE gamertags SET {platform}={gamertag}'
        self.execute_query(query, commit=True)
