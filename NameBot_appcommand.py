# Setup (Imports)
import os
import math

import discord
from discord import app_commands
from dotenv import load_dotenv
import nest_asyncio

from PIL import Image, ImageFont, ImageDraw
from datetime import datetime
import pickle

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')  # Need to supply your own Discord Token, placed in .env in same directory.
ID = os.getenv('GUILD_ID')  # ID for a guild to initialize global sync in. Place in .env
AUTHOR = os.getenv('AUTHOR_ID')  # ID for bot author. Failsafe in global sync. Place in .env

nest_asyncio.apply()

intents = discord.Intents(message_content=True, members=True, guilds=True)
client = discord.Client(intents=intents)
client.tree = app_commands.CommandTree(client)


# Setup (Classes & Objects)
class Server:
    def __init__(self, interaction):
        self.channel = interaction.channel.id
        self.users = {}
        for n in interaction.guild.members:
            if n.nick is None:
                self.users[n.global_name] = [[n.global_name], ['???'],
                                             ['---']]  # .[0] name, .[1] start-date, .[2] end-date
            else:
                self.users[n.global_name] = [[n.nick], ['???'], ['---']]


if os.path.isfile('Servers.pickle'):
    with open('Servers.pickle', 'rb') as f:
        Servers = pickle.load(f)
else:
    Servers = {}


# Functions
def save():
    global Servers
    if os.path.isfile('Servers.pickle'):
        with open('Servers.pickle', 'rb') as f:
            backup = pickle.load(f)
        with open('backup.pickle', 'wb') as f:
            pickle.dump(backup, f)
    with open('Servers.pickle', 'wb') as f:
        pickle.dump(Servers, f)


def historyfunc(interaction, name, ind):
    global Servers
    txt = []
    embed = []
    file = []
    if interaction.guild_id in Servers:
        if Servers[interaction.guild_id].channel != interaction.channel.id:
            txt = ("```subunit\nERROR: This isn't my update channel! If you want me to send updates from here now, "
                   "ask your admin to use the /start command in this channel!```")
        else:
            if name in Servers[interaction.guild_id].users:
                mat = Servers[interaction.guild_id].users[name]
                transmat = [[mat[j][i]
                             for j in range(len(mat))]
                            for i in range(len(mat[0]))]  # transposes nested list

                img = Image.open('history_bg.png')  # Keeping horizontal consistent, but MAY want to adjust vertical
                font = ImageFont.truetype("arialbd-COLR.ttf", 34)
                d = ImageDraw.Draw(img)

                st = len(transmat) - (10 * ind + 1)
                en = st - 9
                if en < 0:
                    en = 0

                try:
                    inc = 0
                    for i in range(st, en-1, -1):   # en-1 since range is exclusive for end
                        y = 108 * (inc + 1) + 95
                        d.text((447, y), font=font, text=transmat[i][0], fill=(255, 255, 255), anchor="mm",
                               embedded_color=True)
                        d.text((1023, y), font=font, text=transmat[i][1], fill=(255, 255, 255), anchor="mm",
                               embedded_color=True)
                        d.text((1335, y), font=font, text=transmat[i][2], fill=(255, 255, 255), anchor="mm",
                               embedded_color=True)
                        inc += 1

                    file = "history" + name + ".png"
                    img.save(file)

                    embed = discord.Embed(title=name + ' Nickname History')
                    embed.set_image(url="attachment://" + file)

                except:
                    txt = "```subunit\nERROR: User doesn't apply (most likely they're a bot)!```"

            else:
                txt = "```subunit\nERROR: The user you're looking for doesn't exist!```"
    else:
        txt = ("```subunit\nERROR: Looks like I haven't been set up in this server yet! "
               "Ask your admin to use the /start command!```")

    return txt, embed, file


# Setup (Views)
class MoveView(discord.ui.View):
    def __init__(self, timeout=360):
        super().__init__(timeout=timeout)

    @discord.ui.button(emoji="✔️", style=discord.ButtonStyle.success)
    async def buttonyes_callback(self, interaction):
        global Servers

        for x in self.children:
            x.disabled = True

        Servers[interaction.guild_id].channel = interaction.channel.id

        await interaction.response.edit_message(content="```Cool! Channel Updated!```", view=self)

    @discord.ui.button(emoji="✖️", style=discord.ButtonStyle.danger)
    async def buttonno_callback(self, interaction):
        for x in self.children:
            x.disabled = True

        await interaction.response.edit_message(content="```fine be that way see if I care```", view=self)


def HistoryMenu(pgs, ind, name, disable):
    global Servers

    class HistoryView(discord.ui.View):
        def __init__(self, pgs, ind, timeout=360):
            super().__init__(timeout=timeout)
            self.ind = ind
            self.pgs = pgs

        def buttondisable(self):
            inc = 0
            for x in self.children:  # THERE's NO WAY THIS IS PYTHONIC
                if inc < 2:
                    x.disabled = self.ind == 0
                else:
                    x.disabled = self.ind == self.pgs
                inc += 1

        @discord.ui.button(label="⏮️", style=discord.ButtonStyle.primary,
                           disabled=disable[0])
        async def buttonfirst_callback(self, interaction, button):
            self.ind = 0
            [], embed, file = historyfunc(interaction, name, self.ind)
            self.buttondisable()

            await interaction.response.edit_message(attachments=[discord.File(file)], embed=embed, view=self)

        @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary, disabled=disable[1])
        async def buttonback_callback(self, interaction, button):
            self.ind += -1
            [], embed, file = historyfunc(interaction, name, self.ind)
            self.buttondisable()

            await interaction.response.edit_message(attachments=[discord.File(file)], embed=embed, view=self)

        @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary, disabled=disable[2])
        async def buttonforward_callback(self, interaction, button):
            self.ind += 1
            [], embed, file = historyfunc(interaction, name, self.ind)
            self.buttondisable()

            await interaction.response.edit_message(attachments=[discord.File(file)], embed=embed, view=self)

        @discord.ui.button(label="⏭️", style=discord.ButtonStyle.primary, disabled=disable[3])
        async def buttonlast_callback(self, interaction, button):
            self.ind = self.pgs
            [], embed, file = historyfunc(interaction, name, self.ind)
            self.buttondisable()

            await interaction.response.edit_message(attachments=[discord.File(file)], embed=embed, view=self)

    return HistoryView(pgs, ind)


# Setup (Commands)
@client.tree.command(
    name="start",
    description="Specifies the channel for Name Bot to talk in",)
async def startcmd(interaction: discord.Interaction):
    global Servers
    if interaction.user.guild_permissions.manage_channels:
        if interaction.guild_id in Servers:
            if Servers[interaction.guild_id].channel != interaction.channel.id:
                await interaction.response.send_message(
                    "```Looks like this is different channel then the one I'm used to. "
                    "Did you want me to move my updates to here?```",
                    view=MoveView(), ephemeral=True)
            else:
                await interaction.response.send_message("```subunit\nERROR: I'm already active here!```",
                                                        ephemeral=True)
        else:
            Servers[interaction.guild_id] = Server(interaction)

            await interaction.response.send_message(
                "```Hi, I'm Name Bot! From now on, "
                "I'll be keeping you up to date on any name changes in the server!```")

    else:
        await interaction.response.send_message(
            "```subunit\nERROR: You don't have the right to do that. Just what are you trying?```", ephemeral=True)


@client.tree.command(
    name="history",
    description="Lists all current and previous names of the given user")
@app_commands.describe(user='The user to look up')
async def historycmd(interaction: discord.Interaction, user: discord.Member):
    global Servers

    pgs = math.floor(len(Servers[interaction.guild_id].users[user.global_name][0]) / 10)
    ind = 0
    if pgs == 0:
        disable = [True, True, True, True]
    else:
        disable = [True, True, False, False]

    txt, embed, file = historyfunc(interaction, user.global_name, ind)

    if txt:
        await interaction.response.send_message(txt, ephemeral=True)
    else:
        await interaction.response.send_message(file=discord.File(file), embed=embed,
                                                view=HistoryMenu(pgs, ind, user.global_name, disable), ephemeral=True)


@client.tree.command(
    name="sync",
    description="sync /commands for all active servers",
    guild=discord.Object(id=ID))
async def slashsync(interaction: discord.Interaction):
    if interaction.user.id == AUTHOR:
        await client.tree.sync()
        await interaction.response.send_message('/ Commands synced! Check back in a bit to confirm!', ephemeral=True)
    else:
        await interaction.response.send_message('You\'re not my dad!', ephemeral=True)


# Discord End
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.tree.sync(guild=discord.Object(id=ID))


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
