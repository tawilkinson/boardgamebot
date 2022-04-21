import { ApplicationCommandRegistry, Command, CommandOptions } from '@sapphire/framework';
import type { CommandInteraction } from 'discord.js';
import { SlashCommandBuilder } from '@discordjs/builders';
import cheerio from 'cheerio';
import axios from 'axios';
import { ApplyOptions } from '@sapphire/decorators';

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
        const { data } = await axios.get(`http://www.boardgamegeek.com/xmlapi2/search?query=${search_game}&exact=1&type=boardgame`);
        var bgg_page = cheerio.load(data);

        console.log(bgg_page.html());
        return interaction.reply("Test");
    }
}