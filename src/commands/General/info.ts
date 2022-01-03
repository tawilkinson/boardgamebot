import { Command, CommandOptions, PieceContext, container } from '@sapphire/framework';
import { send } from '@sapphire/plugin-editable-commands';
import { Message, MessageEmbed } from 'discord.js';
import { time, TimestampStyles } from '@discordjs/builders';
import { roundNumber } from '@sapphire/utilities';
import { seconds } from '../../lib/time';
import { uptime } from 'node:os';

export interface StatsUptime {
	client: string;
	host: string;
	total: string;
}

export class UserCommand extends Command {
	public constructor(context: PieceContext, options: CommandOptions) {
		super(context, {
			...options,
			description: 'Prints info on Board Game Bot',
			aliases: ['botinfo']
		});
	}

	public uptimeStatistics(message: Message): StatsUptime {
		const now = Date.now();
		const nowSeconds = roundNumber(now / 1000);
		return {
			client: time(seconds.fromMilliseconds(now - message.client.uptime!), TimestampStyles.RelativeTime),
			host: time(roundNumber(nowSeconds - uptime()), TimestampStyles.RelativeTime),
			total: time(roundNumber(nowSeconds - process.uptime()), TimestampStyles.RelativeTime)
		};
	}

	public async messageRun(message: Message) {
		const num_commands = container.stores.get('commands').size;
		const uptime_data = this.uptimeStatistics(message);
		// Make a snazzy embed
		const title = 'Board Game Bot Info';
		const description = 'Detailed bot info';
		const url = 'https://github.com/tawilkinson/boardgamebot';
		const embed = new MessageEmbed()
			.setTitle(title)
			.setDescription(description)
			.setTimestamp(message.createdTimestamp)
			.setColor('RANDOM')
			.setURL(url)
			.addField('Bot Name', 'SAGGA Bot', true)
			.addField('Creator', '[tawilkinson](https://github.com/tawilkinson/)', true)
			.addField('Total Commands', num_commands.toString(), true)
			.addField('Users', message.client.users.cache.size.toString(), true)
			.addField('Servers', message.client.guilds.cache.size.toString(), true)
			.addField('Channels', message.client.channels.cache.size.toString(), true)
			.addField('Client Uptime', uptime_data.client, true)
			.addField('Host Uptime', uptime_data.host, true)
			.addField('Total Uptime', uptime_data.total, true);

		return send(message, { embeds: [embed] });
	}
}
