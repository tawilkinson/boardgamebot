import { RegisterBehavior, Command, CommandOptions, PieceContext } from '@sapphire/framework';
import { CommandInteraction, MessageEmbed } from 'discord.js';

export class UserCommand extends Command {
	public constructor(context: PieceContext, options: CommandOptions) {
		super(context, {
			...options,
			description: 'Prints info on the Github repo',
			chatInputCommand: {
				register: true,
				behaviorWhenNotIdentical: RegisterBehavior.Overwrite
			}
		});
	}

	public chatInputRun(interaction: CommandInteraction) {
		// Make a snazzy embed
		const title = 'boardgamebot GitHub Repo';
		const description = `The GitHub repo for this bot is [tawilkinson/boardgamebot](https://github.com/tawilkinson/boardgamebot).
		If you find a bug or want to suggest a feature 
		[create a new issue](https://github.com/tawilkinson/boardgamebot/issues).
		Documentation is coming soon...`;
		const url = 'https://github.com/tawilkinson/boardgamebot';
		const embed = new MessageEmbed()
			.setTitle(title)
			.setDescription(description)
			.setTimestamp(interaction.createdTimestamp)
			.setColor('LIGHT_GREY')
			.setURL(url)
			.setThumbnail('attachment://GitHub.png');

		return interaction.reply( { embeds: [embed], files: [{ attachment: './assets/images/GitHub.png', name: 'GitHub.png' }] });
	}
}
