import { RegisterBehavior, Command, CommandOptions, PieceContext } from '@sapphire/framework';
import type { CommandInteraction } from 'discord.js';

export class PingCommand extends Command {
	public constructor(context: PieceContext, options: CommandOptions) {
		super(context, {
			...options,
			description: 'ping pong',
			chatInputCommand: {
				register: true,
				behaviorWhenNotIdentical: RegisterBehavior.Overwrite
			}
		});
	}

	public async chatInputRun(interaction: CommandInteraction) {
		await interaction.reply({ content: 'Ping?', fetchReply: true });

		return interaction.editReply(
			`Pong from Docker! Bot Latency ${Math.round(this.container.client.ws.ping)}ms. API Latency ${Date.now() - interaction.createdTimestamp
			}ms.`
		);
	}
}
