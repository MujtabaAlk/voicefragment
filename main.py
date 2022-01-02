"""
This is the main entry point for the program.
"""
__author__ = "Mojtaba Alkhalifah"
__author_desc__ = "A humble graduate from King Fahd University of Petroleum and Minerals."

from datetime import datetime
import logging
import os
import pathlib

import discord
from discord.ext import commands
from dotenv import load_dotenv

from channel_cog import ChannelCog
from models import Guild


def setup_logger():
    """
    set up the applications logger and adds the handlers to it.
    """
    # create log directory if it does not exist
    pathlib.Path("./logs").mkdir(exist_ok=True)

    logger_name = "VoiceFragment"

    logging_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s")

    stream_handler = logging.StreamHandler()
    dt_log_file_str = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    file_handler = logging.FileHandler(f"logs/log_{dt_log_file_str}.log", mode="w")
    stream_handler.setFormatter(logging_formatter)
    file_handler.setFormatter(logging_formatter)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    logger.info("logger is set up")


def create_bot() -> commands.Bot:
    """
    Create an instance of the bot and adds commands and Cogs
    :return: The created Discord bot instance
    """
    logger_name = "VoiceFragment"
    logger = logging.getLogger(logger_name)
    command_permissions = dict(manage_guild=True,
                               manage_channels=True,
                               manage_messages=True,
                               move_members=True)
    help_command = commands.DefaultHelpCommand(no_category='Global Commands')
    intents: discord.Intents = discord.Intents(voice_states=True, messages=True, guilds=True)
    client: commands.Bot = commands.Bot(command_prefix='!',
                                        help_command=help_command,
                                        intents=intents)

    @client.event
    async def on_ready():
        logger.info(f'{client.user.name} has connected to Discord!')

        logger.info('Bot is connected to server/s:')
        guild: discord.Guild
        for guild in client.guilds:
            logger.info(f'\t"{guild.name}"')

    @client.command(name='init', aliases=['setup'], help='Initialize the bot to this server.')
    @commands.has_guild_permissions(**command_permissions)
    async def initialize(ctx: commands.Context):
        setup_message: discord.Message = await ctx.send('initializing bot in server...')
        guild: discord.Guild = ctx.guild

        # get guild object from database if it exists otherwise insert into database
        guild_db: Guild
        guild_db, created, *_ = Guild.get_or_create(discord_id=guild.id, defaults=dict(name=guild.name))
        if created:
            logger.info(f'Guild {guild.name} was added to db.')
        else:
            logger.info(f'Guild {guild.name} was already in db.')

        await setup_message.delete(delay=10)
        await ctx.send('Finished Initializing to Server', delete_after=10)
        await ctx.message.delete(delay=10)

    # add the channel cog
    client.add_cog(ChannelCog(client))

    return client


def main():
    """
    Main function of module.
    """
    setup_logger()

    bot = create_bot()
    token = os.getenv('DISCORD_TOKEN')
    bot.run(token)


if __name__ == '__main__':
    load_dotenv()
    main()
