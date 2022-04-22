import { ApplicationCommandRegistry, Command, CommandOptions } from '@sapphire/framework';
import type { CommandInteraction } from 'discord.js';
import { SlashCommandBuilder } from '@discordjs/builders';
import * as cheerio from 'cheerio';
import axios from 'axios';
import { ApplyOptions } from '@sapphire/decorators';
import { titleCase } from "title-case";

@ApplyOptions<CommandOptions>({
    description: `Fetches game info from [BGG](https://boardgamegeek.com) and returns online places to play the game.`
})
export class SearchCommand extends Command {
    public override registerApplicationCommands(registry: ApplicationCommandRegistry) {
        const builder = new SlashCommandBuilder()
            .setName(this.name)
            .setDescription(this.description)
            .addStringOption((option) => option.setName('game').setDescription('The game you are searching for').setRequired(true))
        registry.registerChatInputCommand(builder);
    }

    public async chatInputRun(interaction: CommandInteraction) {
        //let message = "Searching for board games...";
        const args = interaction.options.getString('game');
        let search_game = args!.toLowerCase();

        await interaction.reply(`Searching for ${titleCase(search_game)}, standby whilst I search online...`);
        let total = await this.gameSearch(search_game, true);
        console.log(`${total} exact matches found`)
        if (total == 0) {
            total = await this.gameSearch(search_game, false);
            console.log(`${total} non-exact matches found`)
        }

        if (total >= 1) {
            return interaction.editReply(`${total} games found that match your query...`)
        }
        else {
            return interaction.editReply('Game not found on Board Game Geek! Is it even a board game?')
        }
    }

    private async gameSearch(game: string, exact: boolean): Promise<any> {
        return new Promise((resolve, reject) => {
            var url = `http://www.boardgamegeek.com/xmlapi2/search?query=${game}&type=boardgame`;
            if (exact) {
                url = `http://www.boardgamegeek.com/xmlapi2/search?query=${game}&exact=1&type=boardgame`;
            }
            let total = 0;
            axios.get(url).then(res => {
                const bgg_page = cheerio.load(res.data);

                console.log(bgg_page('items').attr('total'));
                total = parseInt(String(bgg_page('items').attr('total')));

                if (total >= 1) {
                    bgg_page('item').each((_: any, el: any) => {
                        console.log(el.attribs.id)
                        console.log(bgg_page(el).find('name').attr('value'));
                    });
                }
                console.log(`${total} in loop`)
            }).catch(err => reject(err));

            resolve(total);
        })
    }
}