## [Add it to your server!](https://discord.com/api/oauth2/authorize?client_id=812455891692552202&permissions=117760&scope=bot&scope=applications.commands)

# Board Game Bot
[![All Contributors](https://img.shields.io/badge/all_contributors-3-orange.svg?style=flat-square)](#contributors-) [![Python 3](https://pyup.io/repos/github/tawilkinson/boardgamebot/python-3-shield.svg)](https://pyup.io/repos/github/tawilkinson/boardgamebot/) [![CodeFactor](https://www.codefactor.io/repository/github/tawilkinson/boardgamebot/badge)](https://www.codefactor.io/repository/github/tawilkinson/boardgamebot) [![Maintainability](https://api.codeclimate.com/v1/badges/54d6c7104004d9e94c5a/maintainability)](https://codeclimate.com/github/tawilkinson/boardgamebot/maintainability) [![Updates](https://pyup.io/repos/github/tawilkinson/boardgamebot/shield.svg)](https://pyup.io/repos/github/tawilkinson/boardgamebot/) 

A Discord bot to fetch board game data and a list of places you can play them online.

Supported websites/services:
- [Board Game Arena](https://boardgamearena.com/)
- [Boite a Jeux](http://www.boiteajeux.net/)
- [Tabletopia](https://tabletopia.com/)
- [Tabletop Simulator](https://store.steampowered.com/app/286160/Tabletop_Simulator/)
- [Yucata.de](https://www.yucata.de/en)

The main feature of the bot is to search Board Game Geek for information on a board game and then try to find online versions of the game to play as showcased below:

![The bot's response to the command `bg game Carcassonne` which shows detials of the game and links to multiple online versions of the game](carcassonne.png)

# Feature List

All commands are called using `bg <command>` in a Discord channel. `bg help` will list all currently loaded commands.

- Dice: simple dice roller
  - `roll`: Using standard dice notation: You can roll up to 9,999 dice with up to 9,999 sides each.
- Fun: a selection of fun bot commands
  - `theme`: generates a random board game theme.
- Games:
  - `game <game name>`: Prints detailed info about a board game. Uses BGG/local database to find the game and if that game exists gets information on places to play the game virtually.
  - `bga`: Lists all games currently avaialable on [Board Game Arena](https://boardgamearena.com/gamelist) (cache updates every 24 hours).
  - `boite`: Lists all games currently avaialable on [Boîte a Jeux](http://www.boiteajeux.net/) (cache updates every 24 hours).
  - `tabletopia`: Gives a link to [Tabletopia](https://tabletopia.com/) as it has too many gmaes to list.
  - `tts`: Lists all official DLC currently avaialable for [Tabletop Simulator](https://store.steampowered.com/dlc/286160/Tabletop_Simulator/#browse) (cache updates every 24 hours).
  - `yucata`: Lists all games currently avaialable on [Yucata.de](https://www.yucata.de/en) (cache updates every 24 hours).
- No Category:
  - `help`: Shows the help message.
  - `load`: Loads a cog.
  - `reload`: Reloads a cog.
  - `unload`: Unloads a cog.

# Quick-Start Guide

Following the steps here should get you a test bot up and running to hack on. If you want to just add the production version to your server, you'll have to wait.

This guide assumes the following:

- You have set up a Discord Application with Administrator permissions in the [Discord Developer Portal](https://discord.com/developers), added it to your Discord Server, and that you have the token at-hand\*
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

\* There is a [good guide to this process](https://www.freecodecamp.org/news/create-a-discord-bot-with-python/)

## Quick-Start Guide [No Docker]

1. Follow steps 1-2 above
2. Change directory to `bot/python`
3. Install dependencies by running `pip install -r requirements.txt`
   * Read `requirements.txt` if you need to check what they are
4. Run `python bot.py` and check to see your bot comes online in Discord!

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://tawilkinson.com"><img src="https://avatars.githubusercontent.com/u/3664960?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Tom Wilkinson</b></sub></a><br /><a href="https://github.com/tawilkinson/boardgamebot/commits?author=tawilkinson" title="Code">💻</a></td>
    <td align="center"><a href="http://aishamclean.co.uk"><img src="https://avatars.githubusercontent.com/u/13386970?v=4?s=100" width="100px;" alt=""/><br /><sub><b>sonmi451</b></sub></a><br /><a href="https://github.com/tawilkinson/boardgamebot/commits?author=sonmi451" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/ElectricWarr"><img src="https://avatars.githubusercontent.com/u/10360900?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Michael Warr</b></sub></a><br /><a href="https://github.com/tawilkinson/boardgamebot/commits?author=ElectricWarr" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
