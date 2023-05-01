# importing the libraries
import discord
from discord import app_commands
from util import (
    getResponse,
    initializeConversation,
)  
import functools
import typing
import asyncio


GUILD_ID = 1096876100040282254  # replace with your guild id
MY_GUILD = discord.Object(id=1096876100040282254)  # replace with your guild id
AI_LOADED = False
BOT_TOKEN = "MTA5NzA3ODIwNTMyOTk4MTUwMA.GQmbE8.V6CtajhBB9Pr_glzu0aAEkKqFpVdK9TgDXyQBs"


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
       
        self.tree = app_commands.CommandTree(self)
    async def setup_hook(self):
        
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    # initializeConversation()
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")


@client.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f"Hi, {interaction.user.mention}")


@client.tree.command()
async def ping(interaction: discord.Interaction):
    """Simple Ping Pong!"""
    # get latency client
    ping = round(client.latency * 1000)
    embed = discord.embeds.Embed(
        color=discord.colour.Color.blurple(),
    )
    embed.set_author(
        icon_url=interaction.user.display_avatar.url, name=f"|  Pong! (Took {ping}ms)"
    )
    await interaction.response.send_message(embed=embed)


# We need to use asyncio.to_thread to run the functions in a separate thread
def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper


# Get response from the AI
@to_thread
def get_ai(promt):
    resp = getResponse(promt)
    return resp


# Initialize/Reload the conversation
@to_thread
def start_ai():
    global AI_LOADED
    initializeConversation()
    AI_LOADED = True
    return


# Used to send a prompt to the AI
@client.tree.command()
@app_commands.guild_only()
@app_commands.describe(prompt="The prompt you want to send to the AI")
async def prompt(interaction: discord.Interaction, prompt: str):
    """Sends a prompt to the AI."""
    await interaction.response.defer()
    if not AI_LOADED:
        embed = discord.Embed(
            color=discord.colour.Color.dark_orange(), title="AI Not Loaded"
        )
        embed.description = "Ask the bot owner to reload the AI"
        return await interaction.followup.send(embed=embed)

    resp = await get_ai(prompt)
    # if len(resp) > 1024:
    embed = discord.Embed(color=discord.colour.Color.teal(), title=prompt)

    embed.description = resp
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url,
    )
    embed.timestamp = interaction.created_at

    return await interaction.followup.send(embed=embed)


# admin only
# reloads the AI
@client.tree.command()
@app_commands.default_permissions()
@app_commands.guild_only()
async def start(interaction: discord.Interaction):
    """Reloads/Starts the AI"""
    await interaction.response.defer()
    await start_ai()
    embed = discord.Embed(color=discord.colour.Color.yellow(), title="AI Reloaded")
    embed.description = "To use the AI, use the `/prompt` command"
    return await interaction.followup.send(embed=embed)


# help command
# lists all the commands
@client.tree.command()
@app_commands.guild_only()
async def help(interaction: discord.Interaction):
    """Lists all the commands"""
    embed = discord.Embed(
        color=discord.colour.Color.blurple(),
        title="Help",
        description="Here are the commands you can use",
    )

    embed.add_field(name="`/hello`", value="Says hello!", inline=False)
    embed.add_field(name="`/ping`", value="Simple Ping Pong!", inline=False)
    embed.add_field(name="`/prompt`", value="Sends a prompt to the AI.", inline=False)
    embed.add_field(name="`/reload`", value="Reloads/Starts the AI", inline=False)
    embed.add_field(name="`/help`", value="Shows this message", inline=False)
    embed.add_field(
        name="`/invite`", value="Sends the invite link for the bot", inline=False
    )
    embed.add_field(name="`/shutdown`", value="Shuts down the AI", inline=False)

    await interaction.response.send_message(embed=embed)


# invite link
# sends the invite link for the bot
@client.tree.command()
# @app_commands.guild_only()
async def invite(interaction: discord.Interaction):
    """Sends the invite link for the bot"""
    embed = discord.Embed(
        color=discord.colour.Color.blurple(),
        title="Invite 🔗",
        description="Here is the invite link for the bot 😊",
    )
    embed.url = "https://discord.com/api/oauth2/authorize?client_id=1097078205329981500&scope=applications.commands"
    await interaction.response.send_message(embed=embed)



@client.tree.command()
@app_commands.guild_only()
@app_commands.default_permissions()
async def shutdown(interaction: discord.Interaction):
    """Shuts down the AI"""
    global AI_LOADED
    AI_LOADED = False
    embed = discord.Embed(color=discord.colour.Color.red(), title="AI Shut Down")
    embed.description = "Start the AI again using `/reload`"
    await interaction.response.send_message(embed=embed)
   
@client.event
async def on_interaction(interaction: discord.Interaction):
   
    if (
        interaction.type is discord.InteractionType.application_command
        and not interaction.command
    ):
        await interaction.response.send_message("Unknown command.", ephemeral=True)


if __name__ == "__main__":
    client.run(BOT_TOKEN)