import discord

class Members:
    def __init__(self, user_name, user_id, gh, oos, ma, af, gamertag, img_url, pirate_name):
        self.user_name = user_name
        self.user_id = user_id
        self.levels = {"gh": gh, "oos": oos, "ma": ma, "af": af}
        self.gamertag = gamertag
        self.img_url = img_url
        self.pirate_name = pirate_name