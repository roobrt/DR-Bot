# 🎮 DRBot - Dropshot Tournament Discord Notifier

**DRBot** is a custom Discord bot made for the [Dropshot Resurgence Discord server](discord.gg/dropshot) that monitors upcoming **Dropshot tournaments** in *Rocket League* using the [Rocket League API on RapidAPI](https://rapidapi.com/rocket-league1/api/rocket-league1). 
It alerts your Discord server with a scheduled message 1.5 hours before a tournament starts, using Discord’s native timestamp formatting and role pings.

--- 
## 🚀 Features

- ⏰ Sends **automatic alerts** for upcoming Dropshot tournaments
- 🌍 Supports both **US-East** and **Europe** tournament regions
- 🧠 Detects tournaments using **live API data**
- 📅 Alerts are **scheduled once per day** per region
- 🕒 Uses **Discord relative timestamps** (`<t:...:R>`) for clean time formatting
- 🔔 Automatically pings a specified Discord **role**
- ♻️ Prevents duplicate alerts using an internal tracking system

---

## ⚙️ Technologies Used

- Python 3.9+
- `discord.py` 2.5+
- `requests`
- `python-dotenv`
- `zoneinfo` (standard in Python 3.9+)
- [RapidAPI Rocket League API](https://rapidapi.com/rocket-league1/api/rocket-league1)

---

## 📁 Project Structure
DR-Bot/

├── bot.py # Main bot logic and scheduler

├── keep_alive.py # Flask server to keep Render (or Replit) alive

├── .env # Contains API keys and tokens (not committed)

├── requirements.txt # Python dependencies

├── README.md # This file

---

## 🧪 Example Output
> **:alarm_clock: IN-GAME TOURNAMENT ALERT!**
> 
> Dropshot Tournament in **US-EAST** starts `in 1 hour`
> 
> `@In Game Tournament Ping`

---

## 📅 Alert Schedule

| Region   | Check Time       | Expected Start Time | Alert Lead Time |
|----------|------------------|---------------------|-----------------|
| US-East  | 19:00 UTC        | 20:00-20:30 UTC     | 1.5 hours       |
| Europe   | 12:00 UTC        | 13:00-13:30 UTC     | 1.5 hours       |

> [!NOTE]
> The Rocket League API on RapidAPI only allows 5 calls per 24 hours in their Free Subscription plan. By checking once every day for these two regions, we can limit the calls to 2 per day.

---

## 🔑 Environment Variables (`.env`)

Create a `.env` file with the following content:

```env
DISCORD_BOT_TOKEN=your_discord_bot_token
RAPIDAPI_KEY=your_rapidapi_key
```

---

## 🛠️ Setup Instructions

### ✅ 1. Prerequisites

Ensure you have:

- Python 3.9 or newer
- A Discord bot application created at [Discord Developer Portal](https://discord.com/developers/applications)
- A RapidAPI account and access to the [Rocket League API](https://rapidapi.com/rocket-league-rocket-league-default/api/rocket-league1)
- A `.env` file with the necessary tokens (see below)

---

### 📦 2. Install Dependencies

```bash
pip install -r requirements.txt
```

If using poetry, you can alternatively use:

```bash
poetry install
```

---

### 🔐 3. Configure Environment Variables

Create a .env file in your root directory:

```env
DISCORD_BOT_TOKEN=your_discord_bot_token
RAPIDAPI_KEY=your_rapidapi_key
```

**DO NOT COMMIT this file to version control.**

---

### 🔗 4. Invite the Bot to Your Server

Use the following OAuth2 URL structure (don't forget to change "YOUR_CLIENT_ID"):

https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=150528&integration_type=0&scope=bot

Recommended permissions (bitmask 150528):

- View Channels (to find the channel called #tournament-alerts)
- Send Messages
- Mention Everyone (to ping roles)
- Embed Links (could be used in future versions)

> [!NOTE]
> It is crucial that you make a Discord channel called "#tournament-alerts" and make sure that DRBot has permissions to write in it.
> If you want to change the name of this channel, you must edit the code.

---

### 🚀 5. Run the Bot

Run locally with:

```
python bot.py
```

If deployed to a service like Render, ensure:

- Your service is a web service type (to run keep_alive.py)

- The Start Command is set to:

```bash
$ python3 bot.py
```

- Add the following Build Command:

```
$ pip install -r requirements.txt
```

- Adding the .env file to Render, so the bot can use your own API keys

> Thank you to [CreepyD](https://www.youtube.com/@CreepyD246) for making a [Youtube video](https://www.youtube.com/watch?v=kBdDmCPcbfs) on how to do this. 

---

### 🌐 6. Uptime Monitoring (Must do)

Use [UptimeRobot](https://uptimerobot.com/) to ping your bot’s / route (http://your-bot-url.onrender.com/) every 5 minutes. 
This prevents the host (e.g., Render/Replit) from putting your bot to sleep.

## 🧩 Customization

Want to track Hoops, Rumble, or other modes?

Update this function:

```
def find_dropshot_tournament(data):
    for tournament in data.get('tournaments', []):
        if "dropshot" in tournament.get('mode', '').lower():
            return tournament
    return None
```
Replace "dropshot" with your desired mode (e.g., "hoops", "rumble", "heatseeker").

---

## 🙋 Support / Contact

If you run into issues or want to suggest improvements:

- Open an issue or pull request on GitHub

- Contact the maintainer on Discord: **@robrt**

## 📜 License

This project is licensed under the MIT License.
You are free to use, modify, and distribute this project with attribution.
