import { Command, CommandOptions, PieceContext } from '@sapphire/framework';
import type { Message } from 'discord.js';
import { Thoughts } from '../../lib/thought_data';

export class UserCommand extends Command {
	public constructor(context: PieceContext, options: CommandOptions) {
		super(context, {
			...options,
			description: 'Sends a random thought of the day. The Emperor protects.',
			aliases: ['thought for the day']
		});
	}

	public async messageRun(message: Message) {
		const thought = Thoughts[Math.floor(Math.random() * Thoughts.length)];
		let thought_text = '```+++ BEGIN THOUGHT FOR THE DAY +++\n\n';
		thought_text += thought;
		thought_text += '\n\n+++  END THOUGHT FOR THE DAY  +++```'
		return message.channel.send(thought_text);
	}
}
