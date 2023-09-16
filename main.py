import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
import os
import json
import time
from typing import List, Dict, Any

# Load environment variables from .env file
load_dotenv()

# Retrieve token from environment variable
token: str = os.getenv("TOKEN")

# Create Discord intents object with all intents enabled except typing and presences
intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.messages = True

# Create a bot instance with the specified command prefix and intents
bot: commands.Bot = commands.Bot(command_prefix="!", intents=intents)

# Set the platform to "pc"
platform: str = "pc"

# List to store responses loaded from responses.json
responses: List[Dict[str, str]] = []

# Dictionary to store cooldowns for each keyword and user combination
keyword_cooldowns: Dict[str, float] = {}

# Base URL for Warframe API
WARFRAME_API_BASE_URL: str = "https://api.warframe.com/"

# Function to load responses from responses.json file
def load_responses() -> List[Dict[str, str]]:
    try:
        with open('responses.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Function to write responses to responses.json file
def write_responses() -> None:
    with open('responses.json', 'w') as file:
        json.dump(responses, file, indent=4)

# Event handler for when the bot is ready
@bot.event
async def on_ready() -> None:
    print("Logged in as a bot {0.user}".format(bot))

# Event handler for when a message is received
@bot.event
async def on_message(message: discord.Message) -> None:
    # Ignore messages sent by bots
    if message.author.bot:
        return

    # Iterate through each response
    for response in responses:
        # Extract keyword and text from response
        keyword: str = response['keyword']
        text: str = response['text']
        
        # Generate a unique cooldown key for each user and keyword combination
        cooldown_key: str = f'{message.author.id}-{keyword.lower()}'
        
        # Get the current time
        current_time: float = time.time()
        
        # Check if the user is on cooldown for the keyword
        if cooldown_key in keyword_cooldowns and current_time - keyword_cooldowns[cooldown_key] < 120:
            return
        
        # Check if the keyword is present in the message content
        if keyword.lower() in message.content.lower():
            # Send the response text to the channel
            await message.channel.send(text)
            
            # Update the cooldown for the user and keyword
            keyword_cooldowns[cooldown_key] = current_time
            
            # Exit the loop after sending the response
            break

    # Process the message as a command
    await bot.process_commands(message)

# Command to get the current Cetus cycle in Warframe

@bot.command()
async def cetus(ctx):
    """
    Retrieves the Cetus cycle data from the Warframe API and sends a message with the current state and time remaining.

    Args:
        ctx (object): The context object representing the invocation context of the command.

    Returns:
        None
    """
    # Make a GET request to the Warframe API to retrieve Cetus cycle data
    response = requests.get(f"https://api.warframestat.us/{platform}/cetusCycle")
    data = response.json()

    # Extract the state and time left from the API response
    state = data["state"]
    time_left = data["timeLeft"]

    # Map the state to a human-readable text
    if state == "day":
        state_text = "Daytime"
    else:
        state_text = "Nighttime"

    # Format the message with the Cetus cycle information
    message = f"The current Cetus cycle is in {state_text}. Time remaining: {time_left}"
    
    # Send the message to the channel
    await ctx.send(message)
