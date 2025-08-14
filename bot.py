import random
import discord
from discord.ext import commands
import json

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

@commands.Cog.listener()
async def on_member_join(self, member):
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"Welcome {member.mention}!")

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

bot.run(TOKEN)