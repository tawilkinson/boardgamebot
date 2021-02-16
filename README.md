# Meeple Bot

Build for Board Game Fest 2020 [~~Cursed~~ Online Edition]

# Quick-Start Guide

Following the steps here should get you a test bot up and running to hack on. If you want to just add the production version to your server, you'll have to wait.

This guide assumes the following:

- You have set up a Discord Application with Administrator permissions in the [Discord Developer Portal](https://discord.com/developers), added it to your Discord Server, and that you have the token at-hand
- You have `git clone`'d this repo and are currently in its top-level directory
- Docker is installed and working (try `docker run --rm hello-world`, you'll know if it works!)
  - If you aren't using Docker,  `Quick-Start Guide [No Docker]` after creating your `.env` file (steps 1 & 2)

1. Create a file called `.env` in `bot/python` (so the full path will be eg. `/home/yourname/boardgamefest/bot/python/.env`) with the following contents:
  ```
  DISCORD_TOKEN='REPLACEME'
  ```
2. Replace `REPLACEME` in the `.env` file with your Discord Bot's Token
3. Change directory to `bot`
4. Run `./build.sh`
5. Run `./run.sh` and check to see your bot comes online in Discord!

`CTRL-C` to end execution. Repeat steps 4 & 5 each time you make changes to `bot.py`. 

## Quick-Start Guide [No Docker]

1. Follow steps 1-2 above
2. Change directory to `bot/python`
3. Install dependencies by running `pip install -r requirements.txt`
  - Read `requirements.txt` if you need to check what they are
4. Run `python bot.py` and check to see your bot comes online in Discord!

## Google Calendar API Credentials

_You will need a Google Account_

1. Click `Enable the Google Calendar API` on [this page](https://developers.google.com/calendar/quickstart/python)
2. Follow the instructions
3. Download the `credentials.json` file
4. Move the file to `~/.credentials/credentials.json` for the user who will run `bot.py`

# Feature List

All commands are called using `m;<command>` in a Discord channel. `m;help` will list all currently loaded commands.

- Agenda:
  - `agenda`: Prints the upcoming schedule for the weekend.
  - `cal`: Opens a webpage to show the boardgame weekend calender of events!
- Fun: a selection of fun bot commands
  - `theme`: generates a random board game theme.
- Games:
  - `game <game name>`: Prints detailed info about a board game. Uses BGG/local database to find the game and if that game exists gets information on places to play the game virtually.
- No Category:
  - `help`: Shows the help message.
  - `load`: Loads a cog.
  - `reload`: Reloads a cog.
  - `unload`: Unloads a cog.