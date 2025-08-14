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


bot.run(TOKEN)