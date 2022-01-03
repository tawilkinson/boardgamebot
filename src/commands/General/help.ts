import { Command, CommandOptions, PieceContext, container } from '@sapphire/framework';
import { send } from '@sapphire/plugin-editable-commands';
import { Message, MessageEmbed } from 'discord.js';

export class UserCommand extends Command {
	public constructor(context: PieceContext, options: CommandOptions) {
		super(context, {
			...options,
			description: 'Prints help for using Board Game Bot',
			aliases: ['commands']
		});
	}

	public async messageRun(message: Message) {
		const commands = container.stores.get('commands');
		// Make a snazzy embed
		const title = 'Board Game Bot Help';
		const description = `Command prefix is \`${process.env.DEFAULT_PREFIX}\`\n Usage: \`${process.env.DEFAULT_PREFIX}command\``;
		const embed = new MessageEmbed().setTitle(title).setDescription(description).setTimestamp(message.createdTimestamp).setColor('RANDOM');

		const map = new Map();
		commands.map((cmd: any) => map.set(cmd.name, cmd.description));
		const sorted = new Map([...map.entries()].sort());
		for (const [key, value] of sorted) {
			embed.addField(key, value, true);
		}

		return send(message, { embeds: [embed] });
	}
}
