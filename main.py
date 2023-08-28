import discord
from discord.ext import commands, tasks
import requests
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("TOKEN")

intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)
platform = "pc"


@bot.event
async def on_ready():
  print("Logged in as a bot {0.user}".format(bot))

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if 'crazy' in message.content.lower():
        response = "Crazy? \nI was crazy once. \nThey locked me in a room. \nA rubber room. \nA rubber room with rats. \nThe rats made me crazy. "
        await message.channel.send(response)

    await bot.process_commands(message)

@bot.command()
async def cetus(ctx):
  # Make an API request to get Cetus cycle data
  response = requests.get(f"https://api.warframestat.us/{platform}/cetusCycle")
  data = response.json()

  state = data["state"]
  time_left = data["timeLeft"]

  if state == "day":
    state_text = "Daytime"
  else:
    state_text = "Nighttime"

  message = f"The current Cetus cycle is in {state_text}. Time remaining: {time_left}"
  await ctx.send(message)


bot.run(token)
