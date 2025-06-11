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

@tasks.loop(minutes=5)
async def periodic_checks():
    await us_east_dropshot_check()
    await europe_dropshot_check()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    periodic_checks.start()

@bot.command()
async def ping(ctx):
    """Replies with Pong! and the bot's latency in ms."""
    latency = round(bot.latency * 1000)  # latency is in seconds, convert to ms
    await ctx.send(f'Pong! ({latency} ms)')
    

async def us_east_dropshot_check():
    now = datetime.datetime.now(datetime.timezone.utc)
    # Check window: 18:55–19:05 UTC or 19:25–19:35 UTC (1 hour before both cases)
    if (now.hour == 18 and now.minute >= 55) or (now.hour == 19 and now.minute <= 5):
        await check_dropshot_for_region("us-east", display_name="US-EAST")
    else:
        print("Not in US-EAST check window.")

async def europe_dropshot_check():
    now = datetime.datetime.now(datetime.timezone.utc)
    # Check window: 11:55–12:05 UTC or 11:25–11:35 UTC (1 hour before both cases)
    if (now.hour == 11 and now.minute >= 55) or (now.hour == 12 and now.minute <= 5):
        await check_dropshot_for_region("europe", display_name="EUROPE")
    else:
        print("Not in EUROPE check window.")

announced_tournaments = set()

async def check_dropshot_for_region(region: str, display_name: str):
    try:
        data = fetch_tournaments(region)
        tournament = find_dropshot_tournament(data)

        if tournament:
            start_str = tournament.get('starts')
            if not start_str:
                return

            start_dt = datetime.datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            key = f"{tournament.get('mode')}|{region}|{start_dt.isoformat()}"

            if key not in announced_tournaments:
                announced_tournaments.add(key)
                unix_timestamp = int(start_dt.timestamp())
                formatted_time = f"<t:{unix_timestamp}:R>" # Discord's relative time format

                channel = discord.utils.get(bot.get_all_channels(), name='tournament-alerts')
                if channel:
                    await channel.send(
                        f"# :alarm_clock: **IN-GAME TOURNAMENT ALERT!**\n"
                        f"**Dropshot** Tournament in **{display_name}** starts {formatted_time}\n"
                        f"<@&1377509538311176213>"
                    )   
                    print(f"[{region.upper()}] ✅ Alert sent for tournament at {start_dt.isoformat()}")
                else:
                    print("❌ ERROR: tournament-alerts channel not found")
            else:
                print(f"[{region.upper()}] Tournament at {start_dt.isoformat()} already announced.")
        else:
            print(f"[{region.upper()}] No Dropshot tournament found in API response.")
    except Exception as e:
        print(f"Error during check_dropshot_for_region({region}): {e}")

if not DISCORD_BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN is not set in the environment variables.")
bot.run(DISCORD_BOT_TOKEN)