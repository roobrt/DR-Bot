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
    
    
    # DO NOT EDIT, # these headers are required for the API to work
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY, # Your RapidAPI key, set in .env file
        "x-rapidapi-host": "rocket-league1.p.rapidapi.com",
        "User-Agent": "RapidAPI Playground",
        "Accept-Encoding": "identity"
    }
    
    response = requests.get(url, headers=headers)
    return response.json()

def find_dropshot_tournament(data):
    for tournament in data.get('tournaments', []):
        if "dropshot" in tournament.get('mode', '').lower():
            return tournament
    return None

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    daily_check.start()

# Daily check task to find Dropshot tournaments at 19:00 UTC, 1 hour before they usually start (sometimes 19:30 UTC)
@tasks.loop(time=datetime.time(hour=19, tzinfo=datetime.timezone.utc))
async def daily_check():
    print("⏰ Dropshot daily check triggered at", datetime.datetime.now(datetime.timezone.utc).isoformat())

    for region in ['us-east', 'europe']:
        try:
            data = fetch_tournaments(region)
            tournament = find_dropshot_tournament(data)

            if tournament:
                start_str = tournament.get('starts')
                if not start_str:
                    continue

                start_dt = datetime.datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                now = datetime.datetime.now(datetime.timezone.utc)
                time_until_start = (start_dt - now).total_seconds()

                key = f"{tournament.get('mode')}|{region}|{start_dt.isoformat()}"

                # 🔧 Target condition: 1h before tournament start
                target_seconds = 5400  # 1.5 hours in order to compensate for the 19:30 UTC start time sometimes
                tolerance = 300  # ±5 minutes

                if abs(time_until_start - target_seconds) <= tolerance and key not in announced_tournaments:
                    announced_tournaments.add(key)


                    # Format the region display and time. Only works for us-east and europe for now. (2 API calls per day)
                    region_display = "US-EAST" if region == 'us-east' else 'EUROPE'
                    unix_timestamp = int(start_dt.timestamp())
                    formatted_time = f"<t:{unix_timestamp}:R>"

                    channel = discord.utils.get(bot.get_all_channels(), name='tournament-alerts')
                    if channel:
                        await channel.send(
                            # Sends a message to the channel with a mention of the role
                            f"# :alarm_clock: **IN-GAME TOURNAMENT ALERT!**\n"
                            f"**Dropshot** Tournament in **{region_display}** starts {formatted_time}\n"
                            f"<@&1377509538311176213>"  # Don't forget to give the bot the necessary permissions to mention roles
                        )
                    else:
                        await channel.send(
                            f"Something went wrong, blame <@195640987849064458>! :robot:\n"
                        )
                        print("ERROR: Discord channel not found")
                else:
                    print(f"[{region}] No match: start in {time_until_start/3600:.2f} hours — not within 1h±5min")

        except Exception as e:
            print(f"Error during daily_check for {region.upper()}: {e}")

bot.run(DISCORD_BOT_TOKEN)