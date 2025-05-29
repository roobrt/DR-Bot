import requests
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import asyncio
import datetime
from keep_alive import keep_alive

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

@tasks.loop(time=datetime.time(hour=3, minute=50, tzinfo=datetime.timezone.utc))
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

@tasks.loop(time=datetime.time(hour=3, minute=50, tzinfo=datetime.timezone.utc))  # 14:00 EDT = 18:00 UTC REPLACE WITH YOUR DESIRED TIME
async def daily_check():
    print("⏰ Daily check triggered at", datetime.datetime.now(datetime.timezone.utc).isoformat())

    for region in ['us-east', 'europe']:
        try:
            data = fetch_tournaments(region)
            tournament = find_hoops_tournament(data)

            if tournament:
                start_str = tournament.get('starts')  # Fix to use 'starts' key
                
                if not start_str:
                    continue

                start_dt = datetime.datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                
                now = datetime.datetime.now(datetime.timezone.utc)
                
                notify_time = start_dt - datetime.timedelta(hours=1)
                
                delay = (notify_time - now).total_seconds()


                key = f"{tournament.get('mode')}|{region}|{start_dt.isoformat()}"
                
                
                if delay > 0 and delay < 86400 and key not in announced_tournaments:
                    
                    announced_tournaments.add(key)
                    region_display = "US-EAST" if region == 'us-east' else 'EUROPE'
                    print(f"Scheduled Hoops tournament alert for {region_display} in {delay/60:.1f} minutes.")
                    bot.loop.create_task(schedule_alert(region_display, start_dt, delay))
                    
                else:
                    print(f"No valid alert scheduled: delay={delay}, already announced={key in announced_tournaments}")
                    
                    
        except Exception as e:
            print(f"Error fetching tournaments for {region.upper()}: {e}")

async def schedule_alert(region, start_time, delay):
    await asyncio.sleep(delay)
    channel = discord.utils.get(bot.get_all_channels(), name='tournament-alerts')
    if channel:
        await channel.send(
            f":alarm_clock: **1 Hour Warning!**\n"
            f"Hoops Tournament in **{region}** starts at **{start_time.strftime('%H:%M UTC')}**"
        )

bot.run(DISCORD_BOT_TOKEN)