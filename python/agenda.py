import requests
import discord
import random
from bs4 import BeautifulSoup
from discord.ext import commands


class Agenda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.calendar = 'https://calendar.google.com/calendar/u/0/htmlembed?src=c5ilkhfkd424ddm47unrfuvd9c@group.calendar.google.com&amp;ctz=Europe/London&amp;mode=AGENDA&mode=AGENDA'
        self.sharable_calender = 'https://calendar.google.com/calendar/embed?src=c5ilkhfkd424ddm47unrfuvd9c%40group.calendar.google.com'

    def scrape_events_from_calender(self):
        agenda_html = requests.get(self.calendar)
        soup = BeautifulSoup(agenda_html.text, 'html.parser')
        agenda_events = soup.select(
            'body > div.view-container-border > div > div')
        events = []
        for event in agenda_events:
            date = event.select_one('div.date').text
            event_classes = event.select('tr.event')
            event_data = {}
            event_data['date'] = date
            event_data['events'] = []

            for event_class in event_classes:
                time = event_class.select_one('td.event-time').text
                description = event_class.select_one(
                    'span.event-summary').text
                data = {}
                data['time'] = time
                data['description'] = description
                event_data['events'].append(data)

            events.append(event_data)
        return events

    def format_full_schedule(self, schedule):
        embed = discord.Embed(title='Board Game Festival Agenda')
        for date in schedule:
            name = date['date']
            value = ''

            for event in date['events']:
                value += event['time'] + ' - ' + event['description'] + '\n'
            embed.add_field(name=name, value=value, inline=True)
        return embed

    @commands.command(name='cal',
                      help='Opens a webpage to show the boardgame weekend calender of events!')
    async def cal(self, ctx):
        await ctx.send(f'Board Game Festival schedule of events is available online here: {self.sharable_calender}')

    @commands.command(name='agenda',
                      help='Prints the upcoming schedule for the weekend')
    async def agenda(self, ctx):
        schedule = self.scrape_events_from_calender()
        response = self.format_full_schedule(schedule)
        await ctx.send(embed=response)


def setup(bot):
    bot.add_cog(Agenda(bot))
