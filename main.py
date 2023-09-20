import os
from dotenv import load_dotenv

import discord
from discord import app_commands

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await(tree.sync())
    print("Logged in as {0.user}".format(client))    

@tree.command(name="start", description="Start a new game.")
async def start(interaction : discord.Interaction):
    await interaction.response.send_message("guh")

client.run(TOKEN)