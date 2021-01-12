import requests
import discord
import random
import datetime
from gcsa.google_calendar import GoogleCalendar
from bs4 import BeautifulSoup
from discord.ext import commands


class Agenda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.calendar = 'c5ilkhfkd424ddm47unrfuvd9c@group.calendar.google.com'
        self.sharable_calender = 'https://calendar.google.com/calendar/embed?src=c5ilkhfkd424ddm47unrfuvd9c%40group.calendar.google.com'

    def scrape_events_from_calender(self):
        calendar = GoogleCalendar(self.calendar)

        events = {}
        for event in calendar:
            if isinstance(event.start, datetime.datetime):
                date = event.start.date()
            else:
                date = event.start
            event_data = {}

            if isinstance(event.start, datetime.datetime):
                event_data['start'] = event.start.time()
                event_data['start_str'] = datetime.date.strftime(
                    event.start, '%H:%M')
            else:
                event_data['start'] = ''
                event_data['start_str'] = 'All day event'

            if isinstance(event.end, datetime.datetime):
                event_data['end'] = event.end.time()
                event_data['end_str'] = datetime.date.strftime(
                    event.end, "%H:%M")
            else:
                event_data['end'] = ''
                event_data['end_str'] = ''
            event_data['summary'] = event.summary

            if date in events:
                events[date].append(event_data)
            else:
                events[date] = [event_data]

        if events:
            return events
        else:
            return False

    def format_full_schedule(self, schedule):
        embeds = []
        embed = discord.Embed(title='Board Game Festival Agenda')
        if schedule:
            for date in schedule:
                name = datetime.date.strftime(date, '%A %d %B')
                value = '```\n'

                for event in schedule[date]:
                    if event['start_str'] == 'All day event':
                        event_str = event['start_str'] + ' || ' + \
                            event['summary'] + '\n'
                    else:
                        event_str = event['start_str'] + ' - ' + \
                            event['end_str'] + ' || ' + \
                            event['summary'] + '\n'
                    if (len(embed) + len(event_str)) > 5999:
                        embeds.append(embed)
                        embed = discord.Embed(
                            title='Board Game Festival Agenda (continued)')
                    elif (len(value) + len(event_str)) > 1020:
                        value += '```'
                        embed.add_field(
                            name=f'{name} (continued)', value=value, inline=True)
                        value = '```\n'
                    value += event_str
                value += '```'
                embed.add_field(name=name, value=value, inline=True)
            embeds.append(embed)
        else:
            embed.add_field(name='Empty Schedule',
                            value='_Nothing currently scheduled_')
            embeds.append(embed)
        return embeds

    @commands.command(name='cal',
                      help='Opens a webpage to show the boardgame weekend calender of events!')
    async def cal(self, ctx):
        await ctx.send(f'Board Game Festival schedule of events is available online here: {self.sharable_calender}')

    @commands.command(name='agenda',
                      help='Prints the upcoming schedule for the weekend')
    async def agenda(self, ctx):
        schedule = self.scrape_events_from_calender()
        responses = self.format_full_schedule(schedule)
        for response in responses:
            await ctx.send(embed=response)


def setup(bot):
    bot.add_cog(Agenda(bot))
