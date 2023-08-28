import discord
from discord.ext import commands, tasks
import requests
from dotenv import load_dotenv
import os
import json
import asyncio


load_dotenv()
token = os.getenv("TOKEN")

# Load keyword-text pairs from JSON file
def load_responses():
    try:
        with open('responses.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

responses = load_responses()


intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)
platform = "pc"


@bot.event
async def on_ready():
  print("Logged in as a bot {0.user}".format(bot))


# Event listener that pastes copypastas
@bot.event
async def on_message(message):
    global responses

    if message.author.bot:
        return
    
    for response in responses:
        keyword = response['keyword']
        text = response['text']
        if keyword.lower() in message.content.lower():
            await message.channel.send(text)
            break  # Exit loop after the first match

    await bot.process_commands(message)



# Command to submit custom keyword-text pair
@bot.command()
async def submit(ctx):
    global responses  # Declare as global to access outside the function

    def check_author(m):
        return m.author == ctx.author and m.channel == ctx.channel

    await ctx.send("Please enter the keyword:")
    keyword_msg = await bot.wait_for('message', check=check_author)
    keyword_input = keyword_msg.content
    
    # Cancels the function    
    if keyword_input.lower() == 'cancel':
        await ctx.send("Submission canceled.")
        return

    await ctx.send("Please enter the text:")
    text_msg = await bot.wait_for('message', check=check_author)
    text_input = text_msg.content

    # Cancels the function
    if text_input.lower() == 'cancel':
        await ctx.send("Submission canceled.")
        return

    keyword = keyword_msg.content
    text = text_msg.content
    user_id = ctx.author.id

    # Add new keyword-text pair to responses list
    new_response = {'keyword': keyword, 'text': text, 'user_id': user_id}
    responses.append(new_response)

    # Write responses list to JSON file
    with open('responses.json', 'w') as file:
        json.dump(responses, file, indent=4)

    await ctx.send(f"Keyword '{keyword}' with text '{text}' has been submitted by user {ctx.author.mention}.")


# Command to show day night info for the plains of eidolon
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
