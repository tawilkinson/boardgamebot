import { RegisterBehavior, Command, CommandOptions, PieceContext } from '@sapphire/framework';
import type { CommandInteraction } from 'discord.js';
import { Styles, Components, Settings } from '../../lib/theme_data';

export class ThemeCommand extends Command {
	public constructor(context: PieceContext, options: CommandOptions) {
		super(context, {
			...options,
			description: 'Generates a random board game theme.',
			chatInputCommand: {
				register: true,
				behaviorWhenNotIdentical: RegisterBehavior.Overwrite
			}
		});
	}

	public chatInputRun(interaction: CommandInteraction) {
		const style = Styles[Math.floor(Math.random() * Styles.length)];
		const component = Components[Math.floor(Math.random() * Components.length)];
		const setting = Settings[Math.floor(Math.random() * Settings.length)];
		return interaction.reply(`${style} using ${component} set in ${setting}`);
	}
}
