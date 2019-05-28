import discord
from utils import createEmbed
#import mysql

conn = None


def connect_db():
    # global conn
    # conn = mysql.connector.connect(user='NAME', databse='DB', passwd='PW')
    # cur = conn.cursor()
    cur = None
    return cur

def execute_query(query: str, commit: bool = False):
    global conn
    #conn = mysql.connector.connect(user='NAME', databse='DB', passwd='PW')
    cur = conn.cursor()
    cur.execute(query)
    if commit:
        conn.commit()
    return cur


def get_sot_profile(ctx, user: discord.Member):
    query = f'SELECT hc,sd,gh,oos,ma,af,img,alias FROM sot_profile WHERE uid={user.id};'
    cur = execute_query(query)
    r = cur.fetchone()

    #If Profile doesn't exist yet
    if cur.rowcount == 0:
        create_profile(ctx, user)
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

def get_tag_profile(user: discord.Member):
    query = f'SELECT steam,xbox,psn,nintendo FROM gamertags WHERE uid={user.id};'
    cur = execute_query(query)
    r = cur.fetchone()
    profile = {
        'steam': r[0],
        'xbox': r[1],
        'psn': r[2],
        'nintendo': r[3],
    }
    return profile

def get_xbox_tag(user: discord.Member):
    query = f'SELECT xbox FROM gamertags WHERE uid={user.id};'
    cur = execute_query(query)
    r = cur.fetchone()
    return r[0]

def create_profile(ctx, user: discord.Member):
    query = f'INSERT INTO sot_profile (uid) VALUES ({user.id});'
    execute_query(query)                                                #CAN I ONLY COMMIT ONCE?
    query = f'INSERT INTO gamertags (uid) VALUES ({user.id});'
    execute_query(query, commit=True)
    embed = createEmbed(title='**__Profile Created__**', colour='iron', author=user)
    embed.add_field(name="__add your information__", value="1. Add your XBox gamertag with `?gt edit <gamertag>`.\n2. Add your levels with `?levels gh=<gh> oos=<oos>` etc... Use `?help levels` for more info.", inline=False)
    embed.add_field(name="__optional features__", value="- Add an image of your pirate with `?set_image <URL>`. You can also upload the image right to discord and type `?set_image` without any paramters.\nThis URL **NEEDS** to be a direct link to the image ending with `.jpg`, `.png` or `.gif`.\n- Add a pirate name (for role players) by typing `?alias <piratename>`.", inline=False)
    embed.add_field(name="__additional notes__", value="Please note that you **DO NOT** need to add the brackets (`<>`, `[]`). They are merely Syntax to show which arguments are mandatory (`<>`) and which can be left out and will use the previous value (`[]`). This is programming standard.", inline=False)
    await ctx.send(embed=embed)

def update_levels(user: discord.Member, comps: dict):
    global conn
    cur = connect_db()
    cur.executemany(f'UPDATE profile SET %s=%s WHERE uid={user.id}', comps.items())
    conn.commit()

def update_gamertag(user: discord.Member, platform: str, gamertag: str):
    query = f'UPDATE gamertags SET {platform}={gamertag}'
    execute_query(query, commit=True)