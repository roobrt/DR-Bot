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
intents.message_content = True 
bot = commands.Bot(command_prefix='!', intents=intents)

def fetch_tournaments(region):
    url = f"https://rocket-league1.p.rapidapi.com/tournaments/{region}"
    
    
    # DO NOT EDIT, these headers are required for the API to work
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY, # Your RapidAPI key, set it in the .env file
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
    us_east_dropshot_check.start()
    europe_dropshot_check.start()
    

@tasks.loop(time=datetime.time(hour=19, tzinfo=datetime.timezone.utc))
async def us_east_dropshot_check():
    await check_dropshot_for_region("us-east", display_name="US-EAST")

@tasks.loop(time=datetime.time(hour=12, tzinfo=datetime.timezone.utc))
async def europe_dropshot_check():
    await check_dropshot_for_region("europe", display_name="EUROPE")

async def check_dropshot_for_region(region: str, display_name: str):
    try:
        data = fetch_tournaments(region)
        tournament = find_dropshot_tournament(data)

        if tournament:
            start_str = tournament.get('starts')
            if not start_str:
                return

            start_dt = datetime.datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            now = datetime.datetime.now(datetime.timezone.utc)
            time_until_start = (start_dt - now).total_seconds()

            target_seconds = 5400  # 1 hour and 30 minutes in seconds
            tolerance = 300  # ±5 minutes

            if abs(time_until_start - target_seconds) <= tolerance:
                unix_timestamp = int(start_dt.timestamp())
                formatted_time = f"<t:{unix_timestamp}:R>" # Discord's relative time format

                channel = discord.utils.get(bot.get_all_channels(), name='tournament-alerts')
                if channel:
                    await channel.send(
                        # Sends a message to the channel with a mention of the role
                        f"# :alarm_clock: **IN-GAME TOURNAMENT ALERT!**\n"
                        f"**Dropshot** Tournament in **{display_name}** starts {formatted_time}\n"
                        f"<@&1377509538311176213>"  # Don't forget to give the bot the necessary permissions to mention roles
                    )   
                    print(f"[{region.upper()}] ✅ Alert sent for tournament at {start_dt.isoformat()}")

                else:
                    print("❌ ERROR: tournament-alerts channel not found")
            else:
                print(f"[{region.upper()}] No match: start in {time_until_start/3600:.2f}h — not within ±{tolerance//60}min of target")
                
    except Exception as e:
        print(f"Error during check_dropshot_for_region({region}): {e}")

if not DISCORD_BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN is not set in the environment variables.")
bot.run(DISCORD_BOT_TOKEN)