import discord
from datetime import datetime
import mysql.connector, json, sys



class Storage:
    
    def __init__(self):
        self.DBUsername = None
        self.DBPassword = None
        self.DBName = None
        try:
            with open('config.json') as f:
                c = json.load(f)

            self.DBUsername = c.get('db_username')
            self.DBPassword = c.get('db_password')
            self.DBName = c.get('db_name')

            if not all((
                self.DBUsername,
                self.DBPassword,
                self.DBName,
            )):
                raise KeyError('Missing field.')

        except FileNotFoundError:
            self.save()
            print('Please edit config.json')
            sys.exit(1)
        except KeyError as f:
            self.save()
            print(f'Missing value: {f}')
            sys.exit(1)

        
        self.conn = mysql.connector.connect(
            host='localhost',
            user=self.DBUsername,
            password=self.DBPassword,
            database=self.DBName
        )
        self.datetime_scheme = '%Y-%m-%d %H:%M:%S'

    def save(self):
        with open('config.json', 'w') as f:
            json.dump({
                'db_username': self.DBUsername,
                'db_password': self.DBPassword,
                'db_name': self.DBName,
            }, f)

    
    def get_cursor(self, retry: bool = True):
        try:
            cursor = self.conn.cursor(buffered=True)
            return cursor
        except Exception as e:
            if retry:
                self.conn = mysql.connector.connect(
                    host='localhost',
                    user=self.DBUsername,
                    passwd=self.DBPassword,
                    database=self.DBName
                )
                return self.get_cursor(retry=False)
            else:
                raise e

    def execute_query(self, query: str, commit: bool = True):
        cur = self.get_cursor()
        cur.execute(query)
        if commit:
            self.conn.commit()
        r = cur.fetchone()
        cur.close()
        return r

    def execute_query_many(self, query: str, commit: bool = True):
        cur = self.get_cursor()
        cur.execute(query)
        if commit:
            self.conn.commit()
        r = cur.fetchall()
        cur.close()
        return r


    '''
        CLEAN UP AND GENERAL FUNCTIONS
    '''

    def add_guild(self, guild: discord.Guild, role: discord.Role = None):
        if role:
            query = f'INSERT INTO settings (gid, lfc_role) VALUES ({guild.id}, {role.id});'
        else:
            query = f'INSERT INTO settings (gid) VALUES ({guild.id});'
        self.execute_query(query, commit=True)

    def get_all_guilds(self, client: discord.Client):
        query = f'SELECT gid FROM settings;'
        r = self.execute_query_many(query)
        return [client.get_guild(gid[0]) for gid in r]

    def guild_leave(self, guild: discord.Guild):
        query = f'DELETE FROM messages WHERE gid={guild.id};'
        self.execute_query(query)
        query = f'DELETE from settings WHERE gid={guild.id};'
        self.execute_query(query)
        query = f'DELETE from lfc_channels WHERE gid={guild.id};'
        self.execute_query(query)
        query = f'DELETE from profile_channels WHERE gid={guild.id};'
        self.execute_query(query)
        query = f'DELETE from auto_voice_names WHERE gid={guild.id};'
        self.execute_query(query, commit=True)

    def user_join(self, user: discord.Member):
        query = f'INSERT INTO sot_profile (uid) \
            SELECT {user.id} \
            FROM dual \
            WHERE NOT EXISTS (\
                SELECT uid \
                FROM sot_profile \
                WHERE uid={user.id}\
            ) LIMIT 1;'
        self.execute_query(query)
        query = f'INSERT INTO gamertags (uid) \
            SELECT {user.id} \
            FROM dual \
            WHERE NOT EXISTS (\
                SELECT uid \
                FROM gamertags \
                WHERE uid={user.id}\
            ) LIMIT 1;'
        self.execute_query(query)
        query = f'INSERT INTO social (uid) \
            SELECT {user.id} \
            FROM dual \
            WHERE NOT EXISTS (\
                SELECT uid \
                FROM social \
                WHERE uid={user.id}\
            ) LIMIT 1;'
        self.execute_query(query)

    def user_leave(self, user: discord.User):
        query = f'DELETE FROM sot_profile WHERE uid={user.id};'
        self.execute_query(query, commit=False)
        query = f'DELETE FROM gamertags WHERE uid={user.id};'
        self.execute_query(query, commit=False)
        query = f'DELETE FROM social WHERE uid={user.id};'
        self.execute_query(query)



    '''
        `PROFILE` FUNCTIONS
    '''

    async def get_sot_profile(self, ctx, user: discord.Member):
        query = f'SELECT hc,sd,gh,oos,ma,af,img,alias,rb FROM sot_profile WHERE uid={user.id};'
        cur = self.get_cursor()
        cur.execute(query)
        r = cur.fetchone()

        #If Profile doesn't exist yet
        if cur.rowcount == 0 or not r:
            await self.create_profile(ctx, user)
            return None
        cur.close()
        
        profile = {
            'hc': r[0],
            'sd': r[1],
            'gh': r[2],
            'oos': r[3],
            'ma': r[4],
            'rb': r[8],
            'af': r[5],
            'img': r[6],
            'alias': r[7]
        }
        profile['gtag'] = self.get_xbox_tag(user)
        return profile

    async def get_tag_profile(self, ctx, user: discord.Member):
        query = f'SELECT steam,xbox,psn,nintendo,minecraft,origin,blizzard,bethesda,gog FROM gamertags WHERE uid={user.id};'
        r = self.execute_query(query)
        if not r or len(r) == 0:
            await self.create_profile(ctx, user)
            return None
        profile = {
            'steam': r[0],
            'xbox': r[1],
            'psn': r[2],
            'nintendo': r[3],
            'minecraft': r[4],
            'origin': r[5],
            'blizzard': r[6],
            'bethesda': r[7],
            'gog': r[8]
        }
        return profile

    async def get_social_profile(self, ctx, user: discord.Member):
        query = f'SELECT twitch,mixer,youtube,twitter,reddit,itchio FROM social WHERE uid={user.id}'
        r = self.execute_query(query)
        if not r or len(r) == 0:
            await self.create_profile(ctx, user)
            return None
        profile = {
            'twitch': r[0],
            'mixer': r[1],
            'youtube': r[2],
            'twitter': r[3],
            'reddit': r[4],
            'itchio': r[5]
        }
        return profile

    def get_xbox_tag(self, user: discord.Member):
        query = f'SELECT xbox FROM gamertags WHERE uid={user.id};'
        r = self.execute_query(query)
        if not r:
            return 'None'
        return r[0] or 'None'

    async def create_profile(self, ctx, user: discord.Member):
        self.user_join(user)
        embed = discord.Embed(
            title='Profile Created', 
            colour=0xffd700, 
            description='For a full documentation of what you can change please type `?help Profile`.',
            timestamp=datetime.utcnow()
        )
        embed.set_author(name=user, icon_url=user.avatar_url)
        await ctx.send(embed=embed)

    def update_levels(self, user: discord.Member, comps: dict()):
        cur = self.get_cursor()
        for comp, lvl in comps.items():
            cur.execute(f'UPDATE sot_profile SET {comp}={lvl} WHERE uid={user.id};')
        self.conn.commit()
        cur.close()

    def update_gamertag(self, user: discord.Member, platform: str, gamertag: str):
        if gamertag.lower() == 'null':
            query = f'UPDATE gamertags SET {platform}=NULL WHERE uid={user.id};'
        else:
            query = f'UPDATE gamertags SET {platform}="{gamertag}" WHERE uid={user.id};'
        self.execute_query(query, commit=True)

    def update_img(self, user: discord.Member, url: str):
        if not url:
            query = f'UPDATE sot_profile SET img=NULL WHERE uid={user.id};'
        else:
            query = f'UPDATE sot_profile SET img="{url}" WHERE uid={user.id};'
        self.execute_query(query, commit=True)
        
    def update_alias(self, user: discord.Member, alias: str):
        if not alias:
            query = f'UPDATE sot_profile SET alias=NULL WHERE uid={user.id};'
        else:
            query = f'UPDATE sot_profile SET alias="{alias}" WHERE uid={user.id};'
        self.execute_query(query, commit=True)

    def update_social_media(self, user: discord.Member, platform: str, username: str):
        if username.lower() == 'null':
            query = f'UPDATE social SET {platform}=NULL WHERE uid={user.id};'
        else:
            query = f'UPDATE social SET {platform}="{username}" WHERE uid={user.id};'
        self.execute_query(query, commit=True)


    '''
        `LOOKING FOR CREW` FUNCTIONS
    '''

        

    '''
        `LOOKING FOR CREW`-MODULE SETTINGS
    '''
    
    def get_lfc_settings(self, guild: discord.Guild):
        settings = dict()
        query = f'SELECT lfc FROM settings WHERE gid={guild.id};'
        settings['status'] = self.execute_query(query)[0] == True
        query = f'SELECT cid FROM lfc_channels WHERE gid={guild.id};'
        r = self.execute_query_many(query)
        settings['channels'] = [guild.get_channel(c[0]) for c in r]
        settings['role'] = self.get_lfc_role(guild)
        return settings
        
    def update_lfc_status(self, guild: discord.Guild, status: bool):
        query = f'UPDATE settings SET lfc={str(status)} WHERE gid={guild.id};'
        self.execute_query(query, commit=True)

    def add_lfc_channels(self, guild: discord.Guild, channels: list()):
        self.delete_all_lfc_channels(guild)
        cur = self.get_cursor()
        cids = list()
        for c in channels:
            cids.append((str(c.id), str(guild.id)))
        cur.executemany(f'INSERT INTO lfc_channels (cid,gid) VALUES (%s,%s);', cids)
        self.conn.commit()
        cur.close()

    def delete_all_lfc_channels(self, guild: discord.Guild):
        query = f'DELETE FROM lfc_channels WHERE gid={guild.id};'
        self.execute_query(query, commit=True)

    def get_lfc_enabled_guilds(self, client: discord.Client):
        query = 'SELECT gid FROM settings WHERE lfc=TRUE;'
        r = self.execute_query_many(query)
        return [client.get_guild(gid[0]) for gid in r]

    def update_lfc_role(self, guild: discord.Guild, role: discord.Role):
        query = f'UPDATE settings SET lfc_role={role.id} WHERE gid={guild.id}'
        self.execute_query(query, commit=True)

    def get_lfc_role(self, guild: discord.Guild):
        query = f'SELECT lfc_role FROM settings WHERE gid={guild.id}'
        r = self.execute_query(query)[0]
        return guild.get_role(r)
    

    '''
        `PROFILE`-MODULE SETTINGS
    '''

    def get_profile_settings(self, guild: discord.Guild):
        settings = dict()
        query = f'SELECT profile FROM settings WHERE gid={guild.id};'
        settings['status'] = self.execute_query(query)[0] == True
        query = f'SELECT cid FROM profile_channels WHERE gid={guild.id};'
        r = self.execute_query_many(query)
        settings['channels'] = [guild.get_channel(c[0]) for c in r]
        return settings

    def update_profile_status(self, guild:discord.Guild, status: bool):
        query = f'UPDATE settings SET profile={str(status)} WHERE gid={guild.id};'
        self.execute_query(query, commit=True)

    def add_profile_channels(self, guild: discord.Guild, channels: list()):
        self.delete_all_profile_channels(guild)
        cur = self.get_cursor()
        cids = list()
        for c in channels:
            cids.append((str(c.id), str(guild.id)))
        cur.executemany(f'INSERT INTO profile_channels (cid,gid) VALUES (%s,%s);', cids)
        self.conn.commit()
        cur.close()

    def delete_all_profile_channels(self, guild: discord.Guild):
        query = f'DELETE FROM profile_channels WHERE gid={guild.id};'
        self.execute_query(query, commit=True)

    def get_profile_enabled_guilds(self, client: discord.Client):
        query = 'SELECT gid FROM settings WHERE profile=TRUE;'
        r = self.execute_query_many(query)
        return [client.get_guild(gid[0]) for gid in r]

    '''
        `AUTO-VOICE`-MODULE SETTINGS
    '''

    def get_auto_voice_settings(self, guild: discord.Guild):
        settings = dict()
        settings['channel'] = self.get_auto_voice_channel(guild)
        settings['names'] = self.get_auto_voice_names(guild)
        return settings

    def get_auto_voice_channel(self, guild: discord.Guild):
        query = f'SELECT auto_voice_channel FROM settings WHERE gid={guild.id};'
        return guild.get_channel(self.execute_query(query)[0])

    def get_auto_voice_names(self, guild:discord.Guild):
        query = f'SELECT name FROM auto_voice_names WHERE gid={guild.id};'
        r = self.execute_query_many(query)
        return [n[0] for n in r]


    def update_auto_voice_channel(self, guild:discord.Guild, channel: discord.abc.GuildChannel):
        if channel:
            query = f'UPDATE settings SET auto_voice_channel={channel.id} WHERE gid={guild.id};'
        else: 
            query = f'UPDATE settings SET auto_voice_channel=NULL WHERE gid={guild.id};'
        self.execute_query(query, commit=True)
    
    def add_auto_voice_names(self, guild:discord.Guild, names: list()):
        cur = self.get_cursor()
        namelist = list()
        for name in names:
            namelist.append((name, guild.id))
        cur.executemany(f'INSERT INTO auto_voice_names (name,gid) VALUES (%s, %s);', namelist)
        self.conn.commit()
        cur.close()

    def delete_auto_voice_names(self, guild:discord.Guild, names: list()):
        cur = self.get_cursor()
        namelist = list()
        for name in names:
            namelist.append((name, str(guild.id)))
        cur.executemany(f'DELETE FROM auto_voice_names WHERE name=%s and gid=%s;', namelist)
        self.conn.commit()
        cur.close()

    def delete_all_auto_voice_names(self, guild:discord.Guild):
        query = f'DELETE FROM auto_voice_names WHERE gid={guild.id};'
        self.execute_query(query, commit=True)


    '''
        `ACTIVITY-LOGGING` SETTINGS
    '''

    def get_activity_logging_status(self, guild: discord.Guild):
        query = f'SELECT activity_logging FROM settings WHERE gid={guild.id}'
        r = self.execute_query(query)[0] == True
        return r        

    def update_activity_logging_status(self, guild:discord.Guild, status: bool):
        query = f'UPDATE settings SET activity_logging={str(status)} WHERE gid={guild.id}'
        self.execute_query(query, commit=True)

    '''
        `ACTIVITY-LOGGING` FUNCTIONS
    '''

    def cleanup_messages(self, guilds:list()):
        cur = self.get_cursor()
        query = f'DELETE FROM messages WHERE timestamp < DATE_SUB(NOW(), INTERVAL 30 DAY) OR gid NOT IN ({",".join(str(g.id) for g in guilds)});'
        cur.execute(query)
        self.conn.commit()
        count = cur.rowcount
        cur.close()
        return count

    def user_leave_guild(self, user:discord.Member):
        query = f'DELETE FROM messages WHERE uid={user.id} and gid={user.guild.id};'
        self.execute_query(query, commit=True)

    def add_message(self, m: discord.Message):
        timestamp = m.created_at.strftime(self.datetime_scheme)
        query = f'INSERT INTO messages (mid,uid,gid,timestamp) VALUES ({m.id}, {m.author.id}, {m.guild.id}, "{timestamp}");'
        self.execute_query(query, commit=True)

    def get_user_activity(self, user:discord.Member):
        info = dict()
        query = f'SELECT COUNT(*) FROM messages WHERE uid={user.id} AND gid={user.guild.id};'
        info['amnt'] = self.execute_query(query)[0] or 0
        query = f'SELECT timestamp FROM messages WHERE uid={user.id} AND gid={user.guild.id} ORDER BY timestamp DESC LIMIT 1;'
        ts = self.execute_query(query)
        info['timestamp'] = ts[0] if ts else None
        return info

    def get_activity_logging_enabled_guilds(self, client: discord.Client):
        query = 'SELECT gid FROM settings WHERE activity_logging=TRUE;'
        r = self.execute_query_many(query)
        return [client.get_guild(gid[0]) for gid in r]
