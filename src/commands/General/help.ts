import { RegisterBehavior, Command, CommandOptions, PieceContext, container } from '@sapphire/framework';
import { CommandInteraction, MessageEmbed } from 'discord.js';

export class HelpCommand extends Command {
	public constructor(context: PieceContext, options: CommandOptions) {
		super(context, {
			...options,
			description: 'Prints help for using Board Game Bot',
			chatInputCommand: {
				register: true,
				behaviorWhenNotIdentical: RegisterBehavior.Overwrite
			}
		});
	}

	public chatInputRun(interaction: CommandInteraction) {
		const commands = container.stores.get('commands');
		// Make a snazzy embed
		const title = 'Board Game Bot Help';
		const description = `Slash commands available:`;
		const embed = new MessageEmbed().setTitle(title).setDescription(description).setTimestamp(interaction.createdTimestamp).setColor('RANDOM');

		const map = new Map();
		commands.map((cmd: any) => console.log(cmd));
		commands.map((cmd: any) => map.set(cmd.name, cmd.description));
		const sorted = new Map([...map.entries()].sort());
		console.log(sorted);
		for (const [key, value] of sorted) {
			embed.addField(key, value, true);
		}

		void interaction.reply({ embeds: [embed] });
	}
}
