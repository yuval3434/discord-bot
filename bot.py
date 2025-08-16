import random
import discord
from discord.ext import commands
import json
import yt_dlp
from discord.ext.commands import has_permissions

with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["TOKEN"]
PREFIX = config.get("PREFIX", "!")

intents = discord.Intents.default()
intents.message_content = True
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
        await channel.send(f"Welcome {member.mention}!")

@bot.command()
async def play(ctx, *, query):
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            return await ctx.send("❌ You need to be in a voice channel first!")

    ydl_opts = {'format': 'bestaudio[ext=m4a]', 'noplaylist': True, 'quiet': True, 'outtmpl': 'temp/%(title)s.%(ext)s'}

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
async def commands(ctx):
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
                   "!resume - resume the song \n")

@bot.command()
@has_permissions(administrator=True)
async def admin_commands(ctx):
    await ctx.send("!announce (message) - announce the message \n"
                   "!kick (username) - kick username \n"
                   "!ban (username) - ban username \n"
                   "!unban (username) - unban username \n")

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
    banned_users = await ctx.guild.bans()
    member_name = member_name.lower()

    for ban_entry in banned_users:
        user = ban_entry.user
        if user.name.lower() == member_name or f"{user.name.lower()}#{user.discriminator}" == member_name:
            await ctx.guild.unban(user)
            await ctx.send(f"{user.mention} was unbanned")
            return

    await ctx.send(f"❌ Could not find banned user: {member_name}")

@announce.error
async def announce_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You do not have permission to use this command!")


bot.run(TOKEN)