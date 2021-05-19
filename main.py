"""
This is the main entry point for the program.
"""
__author__ = "Mojtaba Alkhalifah"

import os

import discord
from discord.ext import commands
from dotenv import load_dotenv


def create_bot() -> commands.Bot:
    guild_name = os.getenv('GUILD_NAME')
    help_command = commands.DefaultHelpCommand(no_category='Global Commands')
    intents: discord.Intents = discord.Intents.default()
    intents.members = True
    client: commands.Bot = commands.Bot(command_prefix='!',
                                        help_command=help_command,
                                        intents=intents)

    @client.event
    async def on_ready():
        guild: discord.Guild = discord.utils.get(client.guilds, name=guild_name)

        print(f'{client.user.name} has connected to Discord!')
        if guild is not None:
            print(f'Bot is connected to server "{guild.name}".')

    return client


def main():
    bot = create_bot()
    token = os.getenv('DISCORD_TOKEN')
    bot.run(token)


if __name__ == '__main__':
    load_dotenv()
    main()
