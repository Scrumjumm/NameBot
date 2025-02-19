# Setup (Imports)
import os

import discord
from discord import app_commands
from dotenv import load_dotenv
import nest_asyncio

import table2ascii as t2a
import pandas as pd

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

nest_asyncio.apply()

intents = discord.Intents(message_content = True, members = True, guilds = True)
client = discord.Client(intents=intents)
client.tree = app_commands.CommandTree(client)

# Setup (Classes & Objects)
class Server:
    def __init__(self,channel,users):
        self.channel = channel
        for n in users:
            self.users[n] = users

            Servers[interaction.guild_id]
Servers = {}  # Creating dictionary to store servers in

# Setup (Views)
class MoveView(discord.ui.View):
    def __init__(self, timeout=360):
        super().__init__(timeout=timeout)

    @discord.ui.button(emoji="✔️", style=discord.ButtonStyle.success)
    async def buttonyes_callback(self, interaction, button):
        global Servers

        for x in self.children:  # Still not 100% convinced this is most efficient
            x.disabled = True

        Servers[interaction.guild_id].channel = interaction.channel

        await interaction.response.edit_message(content="```Cool! Channel Updated!```", view=self)

    @discord.ui.button(emoji="✖️", style=discord.ButtonStyle.danger)
    async def buttonno_callback(self, interaction, button):
        for x in self.children:  # Still not 100% convinced this is most efficient
            x.disabled = True

        await interaction.response.edit_message(content="```fine be that way see if I care```", view=self)

class HistoryView(discord.ui.View):
    #Want three columns: Name, Start Date, End Date
    #Embed should be made of pages, each containing... let's say 10 entries?
    #See the following links for inspo-- https://discordpy.readthedocs.io/en/latest/api.html#embed https://plainenglish.io/blog/send-an-embed-with-a-discord-bot-in-python https://stackoverflow.com/questions/63565825/how-to-make-data-to-be-shown-in-tabular-form-in-discord-py
    @discord.ui.button(label="⏮️", style=discord.ButtonStyle.primary)
    async def buttonfirst_callback(self, interaction, button):
        await interaction.response.edit_message(content="```yerp I still need to add this```", view=self)

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary)
    async def buttonback_callback(self, interaction, button):
        await interaction.response.edit_message(content="```yerp I still need to add this```", view=self)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary)
    async def buttonforward_callback(self, interaction, button):
        await interaction.response.edit_message(content="```yerp I still need to add this```", view=self)

    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.primary)
    async def buttonlast_callback(self, interaction, button):
        await interaction.response.edit_message(content="```yerp I still need to add this```", view=self)

# Setup (Commands)
@client.tree.command(
    name="start",
    description="Specifies the channel for Name Bot to talk in",
    guild=discord.Object(id=884316913218519050))  #Need to get rid of guild part soon
async def startcmd(interaction: discord.Interaction):
    global Servers
    if interaction.user.guild_permissions.manage_channels:
        if interaction.guild_id in Servers:
            if Servers[interaction.guild_id].channel != interaction.channel:
                await interaction.response.send_message(
                    "```Looks like this is different channel then the one I'm used to. Did you want me to move my updates to here?```",
                    view=MoveView())
            else:
                await interaction.response.send_message("```subunit\nERROR: I'm already active here!```")
        else:
            Servers[interaction.guild_id] = Server(interaction.channel, interaction.guild.members)
            for n in interaction.guild.members:
                print(n)
            # Rest of setup process
            await interaction.response.send_message(
                "```Hi, I'm Name Bot! From now on, I'll be keeping you up to date on any name changes in the server!```")

    else:
        await interaction.response.send_message(
            "```subunit\nERROR: You don't have the right to do that. Just what are you trying?```")


@client.tree.command(
    name="history",
    description="Lists all current and previous names of the given user",
    guild=discord.Object(id=884316913218519050))
@app_commands.describe(user='The user to look up')
async def historycmd(interaction: discord.Interaction, user : discord.Member):
    global Servers
    if interaction.guild_id in Servers:
        if Servers[interaction.guild_id].channel != interaction.channel:
            await interaction.response.send_message(
                "```subunit\nERROR: This isn't my update channel! If you want me to send updates from here now, ask your admin to use the /start command in this channel!```")
        else:
            if user in Servers[interaction.guild_id].users:
                await interaction.response.send_message('This will do something cool eventually, I swear')  # send an embed list!
            else:
                await interaction.response.send_message(
                    "```subunit\nERROR: The user you're looking for doesn't exist!```")
    else:
        await interaction.response.send_message(
            "```subunit\nERROR: Looks like I haven't been set up in this server yet! Ask your admin to use the /start command!```")


# Discord End
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.tree.sync(guild=discord.Object(id=884316913218519050))

@client.event
async def on_member_update(before, after):
    global Servers

    if before.nick != after.nick:
        await Servers[before.guild.id].channel.send(embed="User " + after.global_name + " changed their nickname from "
                                + before.nick + " to " + after.nick + " !")  #Should probably do this as a embed like the rest


# Token
client.run(TOKEN)