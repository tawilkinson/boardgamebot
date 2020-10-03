import requests
import discord
import random
from bs4 import BeautifulSoup
from discord.ext import commands


class Adgenda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.calendar = 'https://calendar.google.com/calendar/u/0/htmlembed?src=c5ilkhfkd424ddm47unrfuvd9c@group.calendar.google.com&amp;ctz=Europe/London&amp;mode=AGENDA&mode=AGENDA'

    def scrape_events_from_calender(self):
        adgenda_html = requests.get(self.calendar)
        soup = BeautifulSoup(adgenda_html.text, 'html.parser')
        adgenda_events = soup.select("body > div.view-container-border > div > div")
        events = []
        for event in adgenda_events:
            event_text = event.text
            oneline_event_text = event_text.replace('\n', ' ').replace('\r', '')
            events.append(oneline_event_text)
        return events

    def format_full_schedule(self, schedule):
        return ',\n'.join(schedule)

    @commands.command(name="adgenda", help="Prints the upcoming schedule for the weekend")
    async def adgenda(self, ctx):
        schedule = self.scrape_events_from_calender()
        response = self.format_full_schedule(schedule)
        await ctx.send(response)

def setup(bot):
    bot.add_cog(Adgenda(bot))
