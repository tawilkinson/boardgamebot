import requests
import discord
import random
from bs4 import BeautifulSoup
from discord.ext import commands


class Agenda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.calendar = 'https://calendar.google.com/calendar/u/0/htmlembed?src=c5ilkhfkd424ddm47unrfuvd9c@group.calendar.google.com&amp;ctz=Europe/London&amp;mode=AGENDA&mode=AGENDA'
        self.sharable_calander = 'https://calendar.google.com/calendar/embed?src=c5ilkhfkd424ddm47unrfuvd9c%40group.calendar.google.com'

    def scrape_events_from_calender(self):
        adgenda_html = requests.get(self.calendar)
        soup = BeautifulSoup(adgenda_html.text, 'html.parser')
        adgenda_events = soup.select(
            "body > div.view-container-border > div > div")
        events = []
        for event in adgenda_events:
            event_text = event.text
            oneline_event_text = event_text.replace(
                '\n', ' ').replace('\r', '')
            events.append(oneline_event_text)
        return events

    def format_full_schedule(self, schedule):
        return ',\n'.join(schedule)

    @commands.command(name="cal",
                      help="Opens a webpage to show the boardgame weekend calander of events!")
    async def cal(self, ctx):
        await ctx.send(f'Board game festival schedule of events available online here: {self.sharable_calander}')

    @commands.command(name="agenda",
                      help="Prints the upcoming schedule for the weekend")
    async def agenda(self, ctx):
        schedule = self.scrape_events_from_calender()
        response = self.format_full_schedule(schedule)
        await ctx.send(response)


def setup(bot):
    bot.add_cog(Agenda(bot))
