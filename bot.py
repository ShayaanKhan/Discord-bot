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

# create a json file to store chat messages
if not os.path.exists("texts.json"):
    with open("texts.json", "w") as file:
        json.dump([], file)


# Function to load responses from responses.json file
def load_responses() -> List[Dict[str, str]]:
    try:
        with open("responses.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


# Function to write responses to responses.json file
def write_responses() -> None:
    with open("responses.json", "w") as file:
        json.dump(responses, file, indent=4)


# Event handler for when the bot is ready
@bot.event
async def on_ready() -> None:
    print("Logged in as a bot {0.user}".format(bot))


# event to read chat messages and store them in a texts.json file containing the text as well as user ID.
@bot.event
async def on_message(message):
    """
    This function is an event handler that is triggered whenever a message is received.
    It takes in a `message` parameter, which represents the message object.
    The function does the following:
    1. Checks if the message is not from the bot. If it is, the function returns.
    2. If the message is from someone else, it stores the message content and the user ID in a JSON file.
    3. It then checks if the message is a command. If it is, the function returns.
    4. Finally, it processes the commands in the message.
    """
    # if the message is not from the bot, ignore it
    if message.author == bot.user:
        return
    # if the message is from someone else, store it in the json file
    with open("texts.json", "r") as file:
        texts = json.load(file)
    texts.append({"text": message.content, "user_id": message.author.id})
    with open("texts.json", "w") as file:
        json.dump(texts, file, indent=4)

    # if the message is a command, process it
    if message.content.startswith("!"):
        return
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

#funtion to show the responses
@bot.command
async def show(ctx):
    await ctx.send(responses)
    


# Run the bot
bot.run(token)
