import { RegisterBehavior, Command, CommandOptions, PieceContext, container } from '@sapphire/framework';
import { CommandInteraction, MessageEmbed } from 'discord.js';
import { time, TimestampStyles } from '@discordjs/builders';
import { roundNumber } from '@sapphire/utilities';
import { seconds } from '../../lib/time';
import { uptime } from 'node:os';

export interface StatsUptime {
	client: string;
	host: string;
	total: string;
}

export class InfoCommand extends Command {
	public constructor(context: PieceContext, options: CommandOptions) {
		super(context, {
			...options,
			description: 'Prints info on Board Game Bot',
			chatInputCommand: {
				register: true,
				behaviorWhenNotIdentical: RegisterBehavior.Overwrite
			}
		});
	}

	public uptimeStatistics(interaction: CommandInteraction): StatsUptime {
		const now = Date.now();
		const nowSeconds = roundNumber(now / 1000);
		return {
			client: time(seconds.fromMilliseconds(now - interaction.client.uptime!), TimestampStyles.RelativeTime),
			host: time(roundNumber(nowSeconds - uptime()), TimestampStyles.RelativeTime),
			total: time(roundNumber(nowSeconds - process.uptime()), TimestampStyles.RelativeTime)
		};
	}

	public chatInputRun(interaction: CommandInteraction) {
		const num_commands = container.stores.get('commands').size;
		const uptime_data = this.uptimeStatistics(interaction);
		// Make a snazzy embed
		const title = 'Board Game Bot Info';
		const description = 'Detailed bot info';
		const url = 'https://github.com/tawilkinson/boardgamebot';
		const embed = new MessageEmbed()
			.setTitle(title)
			.setDescription(description)
			.setTimestamp(interaction.createdTimestamp)
			.setColor('RANDOM')
			.setURL(url)
			.addField('Bot Name', 'Board Game Bot', true)
			.addField('Owner', 'Tom Wilkinson (<@290452800704479243>)', true)
			.addField('Total Commands', num_commands.toString(), true)
			.addField('Users', interaction.client.users.cache.size.toString(), true)
			.addField('Servers', interaction.client.guilds.cache.size.toString(), true)
			.addField('Channels', interaction.client.channels.cache.size.toString(), true)
			.addField('Client Uptime', uptime_data.client, true)
			.addField('Host Uptime', uptime_data.host, true)
			.addField('Total Uptime', uptime_data.total, true)
			.setFooter({ text: 'Thanks, The Board Game Bot Team' });

		return interaction.reply({ embeds: [embed] });
	}
}
