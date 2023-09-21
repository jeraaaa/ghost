import os
from dotenv import load_dotenv

import asyncio

import urllib.request
import urllib.error

import json

import discord
from discord import app_commands

local_filename, headers = urllib.request.urlretrieve('https://raw.githubusercontent.com/dwyl/english-words/master/words_dictionary.json')
dictionary_json = open(local_filename)
words = json.load(dictionary_json)
dictionary_json.close()

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
async def start(interaction : discord.Interaction, player2 : discord.User | discord.Member):
    player1 = interaction.user
    response = await interaction.response.send_message("Creating game...", ephemeral=True, delete_after=0, silent=True)
    thread : discord.Thread = await interaction.channel.create_thread(name="Ghost Game", auto_archive_duration=60, type=discord.ChannelType.public_thread)
    await thread.add_user(player1)
    await thread.add_user(player2)

    current_player = player1
    running = True

    word = ""

    msg = await thread.send("Word: \n Turn: " + player1.mention)

    while running:
        input = await client.wait_for('message', check=lambda msg: msg.author == current_player and msg.channel == thread)
        command = input.content.lower()

        if command == "help":
            await thread.send(content="""\n   Ghost (also known as ghosts or endbee) is a written or spoken word game in which players take turns adding letters to a growing word fragment, trying not to be the one to complete a valid word. Each fragment must be the beginning of an actual word. The minimum length for a word that counts is 3 letters.

Commands:
help
mode [Ghost|Superghost] - Set the mode of the game (First turn only)
quit - Quit the game
challenge - Challenge the current word on whether or not it is valid\n""")
        elif command == "quit":
            running = False
        elif command == "challenge":
            if len(word) > 3:
                valid = False

                if word in words:
                    await thread.send("Current spelled word is a word")
                else:
                    valid_words = []
                    for possible in words.keys():
                        if possible.startswith(word):
                            valid_words.append(possible)
                            valid = True
                    if valid:
                        other_player : discord.Member | discord.User
                        if current_player == player1:
                            other_player = player2
                        else:
                            other_player = player1
                        
                        await thread.send(content=other_player.mention+": Enter the word you were thinking of")
                        check = await client.wait_for('message', check=lambda msg: msg.author == other_player and msg.channel == thread)
                        check = check.content.lower()
                        
                        if not check.startswith(word):
                             await thread.send(content=check + " does not start with " + word)
                        elif check in valid_words:
                            await thread.send(valid_words)
                        else:
                            await thread.send(content=check + " is not a valid word")
                            valid = False
                    else:
                        await thread.send(content=word + " does not lead to any other word")

                if valid != (player1 == current_player):
                    await thread.send(content=player1.mention + " wins")
                else:
                    await thread.send(content=player2.mention + " wins")
                running = False
            else:
                await thread.send(content="The word must have more than three letters")
        elif len(command) != 1:
            await thread.send(content="Not a valid input")
        else:
            #await thread.purge(check=lambda m: m != msg)
            #await input.delete()
            async for message in thread.history(limit=100):
                if message.author != msg.author:
                    await message.delete()
            word += command
            if current_player == player1:
                current_player = player2
            else:
                current_player = player1
            
            await msg.edit(content="Word: " + word + "\n Turn: " + current_player.mention)
    
    await asyncio.sleep(1)

    await thread.remove_user(player1)
    await thread.remove_user(player2)
    await thread.remove_user(client.user)

client.run(TOKEN)