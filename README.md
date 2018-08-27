# Iron Justice Discord Bot

This discord bot adds value to Sea of Thieves Fleets by providing a "Looking for Crew" Feature and a Profile System to keep track of your Pirate's levels.



## Setup

With it come also a message-logger for the discord server to store every message.
To initialize the logger you only have to create a channel called `#message-log`. Messages and Files will automatically be put there. It is advised to have this channel only be read by Moderators and Administrators, as every message the bot can see gets logged there.

If you invite the bot to your server you have to type `?setup` in a channel you have for yourself to begin the bot's Setup.

## Looking for Crew

The `Looking for Crew` can be used by typing `?lfc`. You have to have added a role called "**lfc**" which should be taggable to help with the whole process.

This role will be removed after 3 hours, but can manually be removed by typing `?nlfc`.

## Profile

In the profile you can add your XBox Gamertag, your levels with the Trading Companies and Athena's Fortune as well as a profile picture and a pirate name or alias, your crewmates shall use upon the high seas.

At first you have to create a profile by typing `?profile`. This will add you to the Database.

After you've done that you can add your Gamertag with `?gt <gamertag>` and your levels with the command `?levels <gh> <oos> <ma> [af]`. The Athena's Fortune levels are optional to update in.