import { Command, CommandOptions, PieceContext } from '@sapphire/framework';
import type { Message } from 'discord.js';
import cheerio from 'cheerio';
import axios from 'axios';

export class UserCommand extends Command {
    public constructor(context: PieceContext, options: CommandOptions) {
        super(context, {
            ...options,
            description: `Fetches game info from [BGG](https://boardgamegeek.com/) then returns online sources, if they exist, to play the game.`,
            aliases: ['s']
        });
    }

    public async messageRun(msg: Message) {
        //let message = "Searching for board games...";
        const args = msg.content.trim().split(/ +/g);
        let search_game = args.splice(0, 2).toString().toLowerCase();
        const { data } = await axios.get(`http://www.boardgamegeek.com/xmlapi2/search?query=${search_game}&exact=1&type=boardgame`);
        var bgg_page = cheerio.load(data);

        console.log(bgg_page.html());
        return msg.channel.send("Test");
    }
}