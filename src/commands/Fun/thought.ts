import { RegisterBehavior, Command, CommandOptions, PieceContext } from '@sapphire/framework';
import type { CommandInteraction } from 'discord.js';
import { Thoughts } from '../../lib/thought_data';

export class ThoughtCommand extends Command {
	public constructor(context: PieceContext, options: CommandOptions) {
		super(context, {
			...options,
			description: 'Sends a random thought of the day. The Emperor protects.',
			chatInputCommand: {
				register: true,
				behaviorWhenNotIdentical: RegisterBehavior.Overwrite
			}
		});
	}

	public chatInputRun(interaction: CommandInteraction) {
		const thought = Thoughts[Math.floor(Math.random() * Thoughts.length)];
		let thought_text = '```+++ BEGIN THOUGHT FOR THE DAY +++\n\n';
		thought_text += thought;
		thought_text += '\n\n+++  END THOUGHT FOR THE DAY  +++```'
		return interaction.reply(thought_text);
	}
}
