import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import docker

# Load the token from .env file
load_dotenv()
TOKEN = os.getenv("token")

# Set up intents and bot
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize Docker client
client = docker.from_env()

# Global variables
buffer = []  # Buffer to store terminal output lines
max_buffer_size = 20  # Maximum number of lines in the buffer
message = None  # To hold the message containing the embed

# Simple ping pong command
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

# Command to check the status of the container
@bot.command()
async def container_status(ctx):
    try:
        # Get the container by name
        container = client.containers.get("sussh-terminal")
        status = container.status  # Container status (running, exited, etc.)
        await ctx.send(f"Container 'sussh-terminal' is {status}.")
    except docker.errors.NotFound:
        await ctx.send("Container 'sussh-terminal' not found.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

# Command to send a user-specified command to the container
@bot.command()
async def send(ctx, *, command: str):
    global buffer, message
    
    # Execute the command in the container
    container = client.containers.get("sussh-terminal")
    result = container.exec_run(command)
    
    # Capture the output of the command
    output = result.output.decode().strip()  # Strip to avoid empty lines from being added
    
    # Split the output into individual lines
    output_lines = output.splitlines()
    
    # Append the new lines to the buffer
    buffer.extend(output_lines)
    
    # If the buffer exceeds max_buffer_size, remove the oldest lines (first lines)
    while len(buffer) > max_buffer_size:
        buffer.pop(0)
    
    # Join the buffer contents into a single string with new lines (only the last 20 lines)
    buffer_content = "\n".join(buffer)
    
    # Trim the buffer_content if it exceeds the Discord embed limit (4096 characters)
    if len(buffer_content) > 4096:
        buffer_content = buffer_content[:4093] + "..."  # Truncate and add ellipsis
    
    # Create or update the embed with the new output
    if not message:
        # If the embed doesn't exist, create a new one
        embed = discord.Embed(title="Terminal Output", description=f"```{buffer_content}```", color=0x00ff00)
        message = await ctx.send(embed=embed)
    else:
        # If the embed already exists, edit the existing message
        embed = discord.Embed(title="Terminal Output", description=f"```{buffer_content}```", color=0x00ff00)
        await message.edit(embed=embed)
    
    # Delete the command message to keep the bot's window clean
    await ctx.message.delete()

# Run the bot
bot.run(TOKEN)
