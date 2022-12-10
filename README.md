# Iron Justice Discord Bot

![GitHub release](https://img.shields.io/github/release/Cradac/Iron-Justice.svg) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) 

[![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/E1E52E9WJ)

## IMPORTANT NOTICE
Since May 2022 the Iron Justice has taken been offline. If you want to use a bot with similar features you should try out [TechPotion's](https://github.com/Atreatis) *Kraken's Watch* bot.

Its documentation and invite link are available [here](https://kraken.potionlab.net).

## General Info

**This project is no longer maintained by me.**

This custom discord bot aims to bring value to Sea of Thieves communities by providing a number of features.

The Justice has been the custom discord bot of the Iron Fleet Sea of Thieves Community for over a year. Since its initial release I felt it has evolved enough to be published.

Most prominently there is a 'Looking for Crew'-module which allows the user to be put into a special group in the discord guild for a limited time.

There is also a profile system. There are multiple pages to the profile which let you keep track of your pirate's in-game levels, your handles on different gaming platforms and your user names of a number of social media pages.

There are also many other additional features, as listed below.

The default prefix is `?`.

## Modules

* Looking For Crew Helper
* Profile System with multiple pages
* Auto-Voice Channel
* In-Discord Message Logging
* Activity-Logging of Members
* Custom Welcome and Leave-Message (These can be requested to be added by the developer)
* Help-Command for Modules and Commands

All Module can be configured with the `?config` command.

The Message-Logger can be enabled by adding a channel called `#message-log`. Messages and files will automatically be put there. It is advised to have this channel only be read by moderators and administrators, as every message the bot can see gets logged there.

For a complete documentation of all commands and modules head [here](https://gist.github.com/Cradac/4544f0cbe9456a637c0d3a85061bda78).

## Self Hosting

It is advised to invite the bot and not host it yourself, since some modules are dependant on Emojis from other Servers.
You are allowed to self-host the bot for your own community and modify the source code to your own needs under the GNU General Public License 3.

Be also advised, that most of the code is not documented, since I have been working mostly alone on this. Please do not let this stop your adventure drive.

Among other things the Welcome and Profile Module are dependant on the bot being invited to some distinct discord guilds to function, since those are dependant on channels and emojis in there.
You can request the Emoji-Set for the Profile Module from me. The contact info is below and in my GitHub Profile.

You can remove the custom welcome messsages and the guild checks from the Welcome Module, or remove it altogether.
You can use the rest of the welcome framework to add your own, custom welcome message.

The Justice requires a connection to a MySQL Database. If you choose the self-host, it should be simple to change the [Storage Module](utils/storage.py) file to use another SQL Database.

It also requires three json files, which store the bot's token, the database credentials and the info for the xbox API.
[Database Credentials](https://gist.github.com/Cradac/816e650fc45faf8e43218e7d69f63899) | [Bot Token](https://gist.github.com/Cradac/f8a7dfef507efaf8b2e57cd83d58e8f3) | [XBox Info](https://gist.github.com/Cradac/c521a80199657479c2c4ec7c43218344)

[This](https://gist.github.com/Cradac/08b7bfcb5674278c06644ffd6b39b4d2) is the database model of the Iron Justice. I advice you change up some things with the charset of the tables, since I'm sometimes having issues with non-latin characters.

## Contributing

I will probably not accept any contributions from other sources.
If you have an interesting idea for the Justice, feel free to contact me and we can find a solution.

## License

The project runs under the GPL v3 License. Feel free to fork the repo.

## Acknowledgment

Thanks to the entire Officer team of the Iron Fleet and Rogue Legends for testing and iterating over all new additions of the Justice.

I also thank my tendency to procrastination, which sometimes halted the development for months and at two other occasions made me rewrite the entire code base within a few days.

## Links
[Invite the Bot](https://discordapp.com/oauth2/authorize?client_id=442346885538250752&scope=bot&permissions=8) | [Read the Documentation](https://gist.github.com/Cradac/4544f0cbe9456a637c0d3a85061bda78) | [Join the Iron Fleet Community](https://discord.gg/yU3BVfW)

## Contact

[Contact me on Mastodon](https://home.social/@cradac) or add me on Discord: `Cradac | Max#2614`
