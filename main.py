import discord
from discord.ext import commands, tasks
import requests
from dotenv import load_dotenv
import os
import json
import asyncio
import time


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

keyword_cooldowns = {}


def write_responses():
    with open('responses.json', 'w') as file:
        json.dump(responses, file, indent=4)


# Events

@bot.event
async def on_ready():
  print("Logged in as a bot {0.user}".format(bot))


# Event listener that pastes copypastas
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Check if any keyword matches in the message
    for response in responses:
        keyword = response['keyword']
        text = response['text']

        # Check if the keyword is on cooldown for this user
        cooldown_key = f'{message.author.id}-{keyword.lower()}'
        current_time = time.time()

        if cooldown_key in keyword_cooldowns and current_time - keyword_cooldowns[cooldown_key] < 120:
            return

        if keyword.lower() in message.content.lower():
            await message.channel.send(text)
            keyword_cooldowns[cooldown_key] = current_time
            break  # Exit loop after the first match

    await bot.process_commands(message)


# Commands

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

# Warframe API base URL
WARFRAME_API_BASE_URL = 'https://api.warframe.market/v1/'

@bot.command()
async def godrolls(ctx, weapon_name):
    # Fetch weapon information from Warframe API
    weapon_url = f'{WARFRAME_API_BASE_URL}weapons/search?q={weapon_name}'
    response = requests.get(weapon_url)
    weapon_data = response.json()

    if not weapon_data.get('payload', {}).get('items'):
        await ctx.send("Weapon not found.")
        return

    weapon_id = weapon_data['payload']['items'][0]['id']

    # Fetch Riven mod data for the weapon
    riven_url = f'{WARFRAME_API_BASE_URL}rivens/search/{weapon_id}'
    response = requests.get(riven_url)
    riven_data = response.json()

    if not riven_data.get('payload', {}).get('riven_mods'):
        await ctx.send("No Riven mods found for this weapon.")
        return

    godrolls = []

    # Define your criteria for godrolls (example: high positive stats)
    for riven_mod in riven_data['payload']['riven_mods']:
        positive_stats = [stat for stat in riven_mod['rerolled']['positive_stats'] if stat['value'] > 1.0]
        if len(positive_stats) >= 3:
            godrolls.append(riven_mod)

    if not godrolls:
        await ctx.send("No godroll Riven mods found for this weapon.")
        return

    # Display the godrolls
    for godroll in godrolls:
        stats_str = ', '.join([f"{stat['value']} {stat['name']}" for stat in godroll['rerolled']['positive_stats']])
        message = f"Godroll Riven: {godroll['item_name']} with stats {stats_str}"
        await ctx.send(message)


# Command to submit custom keyword-text pair
@bot.command()
@commands.has_permissions(administrator=True)
async def submitpasta(ctx):
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



bot.run(token)
