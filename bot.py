import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import datetime

from keep_alive import keep_alive
# Start the Flask server to keep the bot alive

load_dotenv()
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

keep_alive()

# Discord bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

def fetch_tournaments(region):
    url = f"https://rocket-league1.p.rapidapi.com/tournaments/{region}"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "rocket-league1.p.rapidapi.com",
        "User-Agent": "DiscordBot",
        "Accept-Encoding": "identity"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def check_for_dropshot(tournament_data):
    for tournament in tournament_data.get('tournaments', []):
        if "Dropshot" in tournament.get('mode', ''):
            return tournament
    return None

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

    for region in ['us-east', 'europe']:
        data = fetch_tournaments(region)
        dropshot_tournament = check_for_dropshot(data)

        if dropshot_tournament:
            start_str = dropshot_tournament.get('start')  # Example: "2025-05-24T05:00:00.000Z"
            if not start_str:
                continue

            # Convert ISO timestamp to UTC datetime
            start_dt = datetime.datetime.fromisoformat(start_str.replace("Z", "+00:00"))

            # Calculate delay until 1 hour before start time
            now = datetime.datetime.now(datetime.timezone.utc)
            notify_time = start_dt - datetime.timedelta(hours=1)
            delay = (notify_time - now).total_seconds()

            # Avoid negative or excessively large sleeps
            if delay > 0 and delay < 86400:
                region_display = "US-EAST" if region == 'us-east' else 'EUROPE'
                print(f"Scheduled Dropshot tournament alert for {region_display} in {delay/60:.1f} minutes.")
                
                # Schedule the notification
                bot.loop.create_task(schedule_alert(region_display, start_dt, delay))

async def schedule_alert(region, start_time, delay):
    await asyncio.sleep(delay)
    channel = discord.utils.get(bot.get_all_channels(), name='tournament-alerts')
    if channel:
        await channel.send(
            f":alarm_clock: **1 Hour Warning!**\n"
            f"Dropshot Tournament in **{region}** starts at **{start_time.strftime('%H:%M UTC')}**"
        )

bot.run(DISCORD_BOT_TOKEN)
