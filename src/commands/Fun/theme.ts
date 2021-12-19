import { Command, CommandOptions, PieceContext } from '@sapphire/framework';
import type { Message } from 'discord.js';
import { Styles, Components, Settings } from '../../lib/theme_data';

export class UserCommand extends Command {
	public constructor(context: PieceContext, options: CommandOptions) {
		super(context, {
			...options,
			description: 'Generates a random board game theme.',
			aliases: ['t']
		});
	}

	public async messageRun(message: Message) {
		const style = Styles[Math.floor(Math.random() * Styles.length)];
		const component = Components[Math.floor(Math.random() * Components.length)];
		const setting = Settings[Math.floor(Math.random() * Settings.length)];
		return message.channel.send(`${style} using ${component} set in ${setting}`);
	}
}
