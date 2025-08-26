# Discord Bot Example

A multifunctional Discord bot built with discord.py.
The bot includes fun commands, moderation tools, music playback, reminders, polls, and integrations with external APIs such as Riot Games API (League of Legends stats) and MU Online player info.

## Features✨
- 🎮 Game Info

  - !lol_userinfo <Name#Tag> → League of Legends stats (KDA, rank, win rate, champion mastery).

  - !mu_userinfo <username> → MU Online player info.

  - !mu_available <.txt file> → Checks available MU Online nicknames.

- 🎵 Music Player

  - !play <song name> → Plays music in voice channel.

  - !pause / !resume → Control playback.

- 🛠️ Moderation (admin only)

  - !kick, !ban, !unban, !timeout, !untimeout.

  - !announce <message> → Send announcements.

  - !show_banned → Show banned users.

- 🎲 Fun & Utility

  - !ping, !hello, !say, !flip, !dice.

  - !add, !sub → Quick math.

  - !userinfo → Info about a Discord user.

  - !remind <minutes> <message> → Set reminders.

  - !poll "<question>" <options> → Create polls.

- 🌍 Web server (Flask)

  - Keeps the bot alive on Render platform.

## Installation🛠️
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/discord-bot.git
   cd discord-bot
   
2. Install dependencies:
   ```bash\
   pip install -r requirements.txt

3. Setup config.json:
Create a file called config.json with:
      ```bash\
   {
    "TOKEN": "Enter your Discord bot token here",
    "PREFIX": "!",
    "API_KEY": "Enter your Riot API key here"
   }

## Notes📌
- Make sure you have FFmpeg installed for music playback.

- Riot API requires a valid key from Riot Developer Portal

## License📜
This project is for educational and personal use.
Not affiliated with Discord, Riot Games, or MU Online.
