# Setup (Imports)
import os
import io

import discord
from discord import app_commands
from dotenv import load_dotenv
import nest_asyncio

from PIL import Image, ImageFont, ImageDraw
from datetime import datetime
import pickle

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

nest_asyncio.apply()

intents = discord.Intents(message_content = True, members = True, guilds = True)
client = discord.Client(intents=intents)
client.tree = app_commands.CommandTree(client)

# Setup (Classes & Objects)
class Server:
    def __init__(self, interaction):
        self.channel = interaction.channel.id
        self.users = {}
        for n in interaction.guild.members:
            if n.nick is None:
                self.users[n.global_name] = [[n.global_name], ['???'], ['---']]  # .[0] name, .[1] start-date, .[2] end-date
            else:
                self.users[n.global_name] = [[n.nick],['???'],['---']] #.[0] name, .[1] start-date, .[2] end-date

if os.path.isfile('Servers.pickle'):
    with open('Servers.pickle', 'rb') as f:
        Servers = pickle.load(f)
else:
    Servers = {}

# Setup (Views)
class MoveView(discord.ui.View):
    def __init__(self, timeout=360):
        super().__init__(timeout=timeout)

    @discord.ui.button(emoji="✔️", style=discord.ButtonStyle.success)
    async def buttonyes_callback(self, interaction, button):
        global Servers

        for x in self.children:
            x.disabled = True

        Servers[interaction.guild_id].channel = interaction.channel.id

        await interaction.response.edit_message(content="```Cool! Channel Updated!```", view=self)

    @discord.ui.button(emoji="✖️", style=discord.ButtonStyle.danger)
    async def buttonno_callback(self, interaction, button):
        for x in self.children:
            x.disabled = True

        await interaction.response.edit_message(content="```fine be that way see if I care```", view=self)

class HistoryView(discord.ui.View):
    def __init__(self, timeout=360):
        super().__init__(timeout=timeout)

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
    guild=discord.Object(id=884316913218519050))  #NEED TO GET RID OF THIS
async def startcmd(interaction: discord.Interaction):
    global Servers
    if interaction.user.guild_permissions.manage_channels:
        if interaction.guild_id in Servers:
            if Servers[interaction.guild_id].channel != interaction.channel.id:
                await interaction.response.send_message(
                    "```Looks like this is different channel then the one I'm used to. Did you want me to move my updates to here?```",
                    view=MoveView())
            else:
                await interaction.response.send_message("```subunit\nERROR: I'm already active here!```")
        else:
            Servers[interaction.guild_id] = Server(interaction)

            # Rest of setup process
            await interaction.response.send_message(
                "```Hi, I'm Name Bot! From now on, I'll be keeping you up to date on any name changes in the server!```")

    else:
        await interaction.response.send_message(
            "```subunit\nERROR: You don't have the right to do that. Just what are you trying?```")


@client.tree.command(
    name="history",
    description="Lists all current and previous names of the given user",
    guild=discord.Object(id=884316913218519050))  #NEED TO GET RID OF THIS
@app_commands.describe(user='The user to look up')
async def historycmd(interaction: discord.Interaction, user : discord.Member):
    global Servers
    if interaction.guild_id in Servers:
        if Servers[interaction.guild_id].channel != interaction.channel.id:
            await interaction.response.send_message(
                "```subunit\nERROR: This isn't my update channel! If you want me to send updates from here now, ask your admin to use the /start command in this channel!```")
        else:
            if user.global_name in Servers[interaction.guild_id].users:
                mat = Servers[interaction.guild_id].users[user.global_name]
                transmat = [[mat[j][i]
                            for j in range(len(mat))]
                            for i in range(len(mat[0]))] #transposes nested list, don't ask me how


                try:
                    img = Image.open('history_bg.png') #Keeping horizontal consistent, but WILL need to adjust vertical
                    font = ImageFont.truetype("arialbd-COLR.ttf",34)
                    d = ImageDraw.Draw(img)

                    for i in range (len(transmat)):
                        y = 108*(i+1) +95
                        d.text((447, y), font=font, text=transmat[i][0], fill=(255,255,255), anchor="mm", embedded_color=True)
                        d.text((1023, y), font=font, text=transmat[i][1], fill=(255,255,255), anchor="mm", embedded_color=True)
                        d.text((1335, y), font=font, text=transmat[i][2], fill=(255,255,255), anchor="mm", embedded_color=True)


                    img.save("history.png")

                    embed = discord.Embed(title=user.global_name + ' Nickname History')
                    embed.set_image(url = "attachment://history.png")
                    await interaction.response.send_message(file=discord.File("history.png"), embed=embed)

                except:
                    await interaction.response.send_message("```subunit\nERROR: User doesn't apply (most likely they're a bot)!```")

            else:
                await interaction.response.send_message(
                    "```subunit\nERROR: The user you're looking for doesn't exist!```")
    else:
        await interaction.response.send_message(
            "```subunit\nERROR: Looks like I haven't been set up in this server yet! Ask your admin to use the /start command!```")

# Functions
def save():  # Going to need to figure out how to make this work on server (assuming there's issues)
    global Servers
    if os.path.isfile('Servers.pickle'):
        with open('Servers.pickle', 'rb') as f:
            backup = pickle.load(f)
        with open('backup.pickle', 'wb') as f:
            pickle.dump(backup, f)
    with open('Servers.pickle', 'wb') as f:
        pickle.dump(Servers, f)


# Discord End
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.tree.sync(guild=discord.Object(id=884316913218519050))

@client.event
async def on_member_update(before, after):
    global Servers

    if before.nick != after.nick:
        if before.nick is None:
            bnick = before.global_name
        else:
            bnick = before.nick
        if after.nick is None:
            anick = after.global_name
        else:
            anick = after.nick

        Servers[before.guild.id].users[after.global_name][0].append(anick)
        Servers[before.guild.id].users[after.global_name][1].append(datetime.today().strftime('%d-%m-%Y'))
        Servers[before.guild.id].users[after.global_name][2].pop()
        Servers[before.guild.id].users[after.global_name][2].append(datetime.today().strftime('%d-%m-%Y'))
        Servers[before.guild.id].users[after.global_name][2].append('---')
        save()

        out = "User " + after.global_name + " changed their nickname from " + bnick + " to " + anick + " !"
        channel = client.get_channel(Servers[before.guild.id].channel)
        await channel.send(f'```{out}```')


# Token
client.run(TOKEN)