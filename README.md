# Iron Justice Discord Bot

This discord bot adds value to Sea of Thieves fleets by providing a "Looking for Crew" feature and a profile system to keep track of your pirate's levels.

## Setup

With it come also a message-logger for the discord server to store every message.
To initialize the logger you only have to create a channel called `#message-log`. Messages and files will automatically be put there. It is advised to have this channel only be read by moderators and administrators, as every message the bot can see gets logged there.

If you invite the bot to your server you have to type `?setup` in a channel you have for yourself to begin the bot's setup. You can cancel this setup by typing "cancel" when a text answer is expected or react with another emoji when a message-reaction is expected.

The set prefix for this bot is `?`.

## Looking for Crew

The `Looking for Crew` can be used by typing `?lfc`. The bot will create a role called "**lfc**" which you should set to be taggable to help with the whole LFC process. If the automatic creation does not work, please create the role yourself. Pay attention to use lower case letters.

This role will be removed from a user after 1 hour, but can manually be removed by typing `?nlfc`.

## Profile

In the profile you can add your XBox gamertag, your levels with the trading companies and Athena's Fortune as well as a profile picture and a pirate name or alias, your crewmates shall use upon the high seas.

1. Create a profile by typing `?profile`
2. Set your gamertag with `?gt <Gamertag>`
3. Set your levels with `?lvl <GH> <OOS> <MA> [AF]`

Now to the optional things:

* You can set a profile image by typing `?img [URl]`
* You can set a Pirate name, which you want to be adressed as, by typing `?alias <piratename>`

Every piece of info can be reset by leaving out the arguments.

**Additional info for Images:**\
You either need to upload an image to discord with `?img` as a comment on the upload or manually upload the image to an image hoster e.g. Imgur, and get a link that directly links to the image itself and ends with `.png`, `.jpg` or `.gif`.\
Here's a little [tutorial](https://imgur.com/gallery/L2IsRy0) on how to use the Imgur variant

**Please note that you DO NOT need to add the brackets (`<>`, `[]`). They are merely Syntax to show which arguments are mandatory (`<>`) and which can be left out and will use the previous value (`[]`). This is programming standard.**