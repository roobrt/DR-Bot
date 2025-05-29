import requests
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import asyncio
import datetime
from keep_alive import keep_alive
from zoneinfo import ZoneInfo 

load_dotenv()
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

keep_alive()

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True #v2
bot = commands.Bot(command_prefix='!', intents=intents)

announced_tournaments = set()

def fetch_tournaments(region):
    url = f"https://rocket-league1.p.rapidapi.com/tournaments/{region}"
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "rocket-league1.p.rapidapi.com",
        "User-Agent": "RapidAPI Playground",
        "Accept-Encoding": "identity"
    }
    
    response = requests.get(url, headers=headers)
    return response.json()

def find_hoops_tournament(data):
    for tournament in data.get('tournaments', []):
        if "hoops" in tournament.get('mode', '').lower():
            return tournament
    return None

@tasks.loop(time=datetime.time(hour=4, minute=30, tzinfo=datetime.timezone.utc))
async def send_alive_message():
    print("✅ Sending alive message at 03:50 UTC")
    await asyncio.sleep(5)  # Optional small delay for safety

    channel = discord.utils.get(bot.get_all_channels(), name='tournament-alerts')
    if channel:
        await channel.send("I am alive!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    daily_check.start()
    send_alive_message.start()  # Start new loop

@tasks.loop(time=datetime.time(hour=4, minute=30, tzinfo=datetime.timezone.utc))
async def daily_check():
    print("⏰ TEST RUN at", datetime.datetime.now(datetime.timezone.utc).isoformat())

    for region in ['us-east', 'europe']:
        try:
            data = fetch_tournaments(region)
            tournament = find_hoops_tournament(data)

            if tournament:
                start_str = tournament.get('starts')
                if not start_str:
                    continue

                start_dt = datetime.datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                now = datetime.datetime.now(datetime.timezone.utc)

                time_until_start = (start_dt - now).total_seconds()

                key = f"{tournament.get('mode')}|{region}|{start_dt.isoformat()}"

                # 🔧 Test condition: 15h30m before start time
                target_seconds = 15 * 3600 + 30 * 60
                tolerance = 300  # ±5 minutes

                if abs(time_until_start - target_seconds) <= tolerance and key not in announced_tournaments:
                    announced_tournaments.add(key)

                    if region == 'us-east':
                        local_time = start_dt.astimezone(ZoneInfo("America/New_York"))
                        formatted_time = local_time.strftime('%I:%M %p EST')
                        region_display = "US-EAST"
                    else:
                        formatted_time = start_dt.strftime('%H:%M UTC')
                        region_display = "EUROPE"

                    channel = discord.utils.get(bot.get_all_channels(), name='tournament-alerts')
                    if channel:
                        await channel.send(
                            f"# IN-GAME TOURNAMENT ALERT! :alarm_clock:\n"
                            f"**Hoops** Tournament in **{region_display}** starts at **{formatted_time}**"
                        )
                    else:
                        print("Channel not found")
                else:
                    print(f"[{region}] No match: start in {time_until_start/3600:.2f} hours — not within 15h45m±5min")

        except Exception as e:
            print(f"Error during daily_check for {region.upper()}: {e}")

bot.run(DISCORD_BOT_TOKEN)