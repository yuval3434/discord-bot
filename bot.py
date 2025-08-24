import random
import discord
from discord.ext import commands
import json
import yt_dlp
from discord.ext.commands import has_permissions
from datetime import timedelta
import asyncio
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import tempfile


with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["TOKEN"]
PREFIX = config.get("PREFIX", "!")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"bot is connected as {bot.user} ✅")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.name}!")

@bot.command()
async def say(ctx, message):
    await ctx.send(message)

@bot.command()
async def add(ctx, a: int , b: int):
    await ctx.send(a + b)

@bot.command()
async def sub(ctx, a: int , b: int):
    await ctx.send(a - b)

@bot.command()
async def flip(ctx):
    await ctx.send(random.choice(["Head", "Tails"]))

@bot.command()
async def dice(ctx):
    await ctx.send(random.randint(1, 6))

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    embed = discord.Embed(title=f" info about: {member.name}", color=discord.Color.blue())
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

    embed.add_field(name="Username", value=member.name, inline=True)
    embed.add_field(name="Tag", value=member.discriminator , inline=True)
    embed.add_field(name="Join Date", value=member.joined_at.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name="Roles", value=", ".join([role.name for role in member.roles if role.name != "@everyone"]), inline=False)

    await ctx.send(embed=embed)

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"Welcome {member.mention}! \n"
                           f"You can use !show_commands to see the possible commands the bot can obey!")

@bot.command()
async def play(ctx, *, query):
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            return await ctx.send("❌ You need to be in a voice channel first!")

    ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True, 'outtmpl': 'temp/%(title)s.%(ext)s'}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
        filename = ydl.prepare_filename(info)

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        source = discord.FFmpegPCMAudio(filename)
        ctx.voice_client.play(source)

        await ctx.send(f"🎶 Now playing: **{info['title']}**")

@bot.command()
async def pause(ctx):
    if ctx.voice_client.is_playing():
         ctx.voice_client.pause()

@bot.command()
async def resume(ctx):
    if ctx.voice_client.is_paused():
        ctx.voice_client.resume()

@bot.command()
async def show_commands(ctx):
    await ctx.send("!ping - Pong! 🏓 \n"
                   "!hello - hello (username)! \n"
                   "!say (sentence) - (sentence) \n"
                   "!add (number1) (number2) - (number1 + number2) \n"
                   "!sub (number1) (number2) - (number1 - number2) \n"
                   "!flip - Head or Tails \n"
                   "!dice - number between 1 and 6 \n"
                   "!userinfo (username) - info about the user \n"
                   "!play (songname) - if in voicechat it plays the song \n"
                   "!pause - pause the song \n"
                   "!resume - resume the song \n"
                   "!remind (minutes) (message) - reminder \n"
                   "!poll \"(question)\" (options) - create poll \n"
                   "!mu_userinfo (username) - gives you info about the user in the game mu online \n"
                   "mu_removable (txt file) - returns a txt file with removable players \n"
                   "!lol_userinfo (username) - gives you info about the user in the game League of legends \n")

@bot.command()
@has_permissions(administrator=True)
async def show_admin_commands(ctx):
    await ctx.send("!announce (message) - announce the message \n"
                   "!kick (username) - kick username \n"
                   "!ban (username) - ban username \n"
                   "!unban (username) - unban username \n"
                   "!show_banned - show banned users \n"
                   "!timeout - timeout for 24 hours \n"
                   "!untimeout - untimeout \n")

@bot.command()
@has_permissions(administrator=True)
async def announce(ctx, *, message):
    await ctx.send(f"📢 Announcement from {ctx.author.name}: {message}")

@bot.command()
@has_permissions(administrator=True)
async def kick(ctx, member: discord.Member):
    await member.kick()
    await ctx.send(f"{member.mention} was kicked")

@bot.command()
@has_permissions(administrator=True)
async def ban(ctx, member: discord.Member):
    await member.ban()
    await ctx.send(f"{member.mention} was banned")

@bot.command()
@has_permissions(administrator=True)
async def unban(ctx, *, member_name):
    banned_users = [ban async for ban in ctx.guild.bans()]
    member_name = member_name.lower()

    for ban_entry in banned_users:
        user = ban_entry.user
        if user.name.lower() == member_name or f"{user.name.lower()}#{user.discriminator}" == member_name:
            await ctx.guild.unban(user)
            await ctx.send(f"{user.mention} was unbanned")
            return

    await ctx.send(f"❌ Could not find banned user: {member_name}")

@bot.command()
@has_permissions(administrator=True)
async def show_banned(ctx):
    banned_users = [ban async for ban in ctx.guild.bans()]
    if not banned_users:
        await ctx.send("There are no banned users ❌")
        return
    banned_list = ""
    for ban_entry in banned_users:
        user = ban_entry.user
        banned_list += f"{user.name}#{user.discriminator}\n"
    await ctx.send(f"📋 Banned users:\n{banned_list}")

@bot.command()
@has_permissions(administrator=True)
async def timeout(ctx, member: discord.Member, hours: int = 24):
    until = discord.utils.utcnow() + timedelta(hours=hours)
    await member.edit(timed_out_until=until)
    await ctx.send(f"{member.mention} was been timeout for 24 hours")

@bot.command()
@has_permissions(administrator=True)
async def untimeout(ctx, member: discord.Member):
    await member.edit(timed_out_until=None)
    await ctx.send(f"{member.mention} was been untimeout")

@bot.command()
async def remind(ctx,minutes: int,*,message):
    await ctx.send(f"⏰ Reminder set for {minutes} minute(s).")
    await asyncio.sleep(minutes * 60)
    await ctx.send(f"🔔 {ctx.author.mention}, reminder: {message}")

@bot.command()
async def poll(ctx,question, *options):
    if len(options) < 2:
        await ctx.send("❌ You need at least 2 options for a poll!")
        return
    if len(options) > 10:
        await ctx.send("❌ Maximum 10 options allowed!")
        return
    description = ""
    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

    embed = discord.Embed(title=question, description=description, color=discord.Color.blue())
    poll_message = await ctx.send(embed=embed)

    for i in range(len(options)):
        await poll_message.add_reaction(emojis[i])

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error,commands.MissingPermissions):
        await ctx.send("❌ You do not have permission to use this command!")
    elif isinstance(error,commands.MemberNotFound):
        await ctx.send("❌ Member not found")

def mu_search_player(player_name):
    url = f"https://www.uniquemu.co.il/profile/player/req/{player_name}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    tbodys = soup.find_all("tbody")
    tbody = tbodys[2]

    td = tbody.find_all("td")

    dic = {"name": td[0].text.split(":"),
    "class": td[1].text.split(":"),
    "status": td[7].text.split(":"),
    "level": td[9].text.split(":")
    }
    return dic

@bot.command()
async def mu_userinfo(ctx,*, player_name):
    dic = mu_search_player(player_name)
    embed = discord.Embed(title=f" info about: {player_name}", color=discord.Color.blue())
    embed.add_field(name="Username", value=dic["name"][1], inline=True)
    embed.add_field(name="class", value=dic["class"][1], inline=True)
    embed.add_field(name="status", value=dic["status"][1], inline=False)
    embed.add_field(name="level", value=dic["level"][1],inline=False)

    await ctx.send(embed=embed)

def mu_cam_remove(players):
    temp_file = tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt", encoding="utf-8")

    for player_name in players:
        url = f"https://www.uniquemu.co.il/profile/player/req/{player_name}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        tbodys = soup.find_all("tbody")
        tbody = tbodys[2]

        td = tbody.find_all("td")
        try:
            answer = td[30].text.split(":")[1].split()[0]
            if answer != "No":
                temp_file.write(f"{player_name}\n")
        except IndexError:
            temp_file.write(f"{player_name}\n")

    temp_file.close()
    return temp_file

@bot.command()
async def mu_removable(ctx):
    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        if attachment.filename.endswith(".txt"):
            file_bytes = await attachment.read()
            content = file_bytes.decode("utf-8")
            lines = [line.strip() for line in content.splitlines() if line.strip()]
            file = mu_cam_remove(lines)
            file_path = file.name
            await ctx.send("📄 here is the file I created for you:", file=discord.File(file_path, "output.txt"))
        else:
            await ctx.send("thats not a txt file ❌")
    else:
        await ctx.send("You didnt add a file ❌")


def league_player_search(name, tag):
    API_KEY = config["API_KEY"]
    REGION = "europe"
    url = f"https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{quote(name)}/{quote(tag)}"

    headers = {"X-Riot-Token": API_KEY}
    response = requests.get(url, headers=headers)

    info= {"username": name, "riotTag" : tag, "region": REGION}
    if response.status_code == 200:
        data = response.json()
        PUUID = data["puuid"]

        matchurl = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{PUUID}/ids?start=0&count={20}"
        matchresponse = requests.get(matchurl, headers=headers)
        lastmatches = matchresponse.json()

        if len(lastmatches) < 20:
            return 1

        if matchresponse.status_code != 200:
            return 0

        totalkillsAndAsists = 0
        totaldeaths = 0

        for i in range(len(lastmatches)):
            matchId = lastmatches[i]
            statsurl = f"https://europe.api.riotgames.com/lol/match/v5/matches/{matchId}"
            statsresponse = requests.get(statsurl, headers=headers)
            statsdata = statsresponse.json()

            if statsresponse.status_code != 200:
                return 0


            for participant in statsdata["info"]["participants"]:
                if participant["puuid"] == PUUID:
                    totalkillsAndAsists += participant["kills"]
                    totalkillsAndAsists += participant["assists"]
                    totaldeaths += participant["deaths"]

        if totaldeaths != 0:
            kda = totalkillsAndAsists / totaldeaths
            info['kda'] = kda
        else:
            kda = totalkillsAndAsists

        url2 = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-puuid/{PUUID}"
        response2 = requests.get(url2, headers=headers)
        data2 = response2.json()


        for queue in data2:
            if queue["queueType"] == "RANKED_SOLO_5x5":
                info['tier'] = queue["tier"]
                info["rank"] = queue["rank"]
                wins = queue["wins"]
                losses = queue["losses"]
                info['winRate'] = wins / (wins + losses) * 100

        champurl = f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{PUUID}"
        champoresponse = requests.get(champurl, headers=headers)
        champdata = champoresponse.json()

        topChampId = None
        topChampLevel = -1

        for champ in champdata:
            if champ["championLevel"] > topChampLevel:
                topChampLevel = champ["championLevel"]
                topChampId = champ["championId"]

        info["topChampId"] = topChampId
        info["topChampLevel"] = topChampLevel

        dd_version = "13.20.1"
        champions_url = f"http://ddragon.leagueoflegends.com/cdn/{dd_version}/data/en_US/champion.json"
        championresponse = requests.get(champions_url)
        championsData = championresponse.json()

        for champ_name, champ_info in championsData["data"].items():
            if champ_info["key"] == str(topChampId):
                 topChampName = champ_info["name"]
                 info["topChampName"] = topChampName
                 break

        summonerUrl = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{PUUID}"
        summonerResponse = requests.get(summonerUrl, headers=headers)
        summonerData = summonerResponse.json()

        info["summonerLevel"] = summonerData["summonerLevel"]
        info["profileIconId"] = summonerData["profileIconId"]

        info["iconUrl"] = f"https://ddragon.leagueoflegends.com/cdn/{dd_version}/img/profileicon/{info['profileIconId']}.png"

        return info
    else:
        return 0

@bot.command()
async def lol_userinfo(ctx, *, fullname):
    if "#" not in fullname:
        await ctx.send("Please use the format Name#Tag")
        return

    name = fullname.split("#")[0]
    tag = fullname.split("#")[1]

    info = league_player_search(name, tag)

    if info == 0:
        await ctx.send("Player not found")
        return
    if info == 1:
        await ctx.send("Need 20 games")

    embed = discord.Embed(title=f"{name + '#' + tag}", color=discord.Color.blue())
    embed.set_thumbnail(url=info["iconUrl"])
    embed.add_field(name="KDA", value=round(info["kda"],2), inline=True)
    embed.add_field(name="Win Rate", value=f"{round(info['winRate'], 2)}%", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    embed.add_field(name="Rank", value=info["tier"] + ' ' + info["rank"], inline=True)
    embed.add_field(name="Level", value=info["summonerLevel"], inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    embed.add_field(name="Top Champion", value=info["topChampName"], inline=True)
    embed.add_field(name="Champion Level", value=info["topChampLevel"], inline=True)

    await ctx.send(embed=embed)

bot.run(TOKEN)