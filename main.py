"""
This is the main entry point for the program.
"""
__author__ = "Mojtaba Alkhalifah"
__author_desc__ = "A humble graduate from King Fahd University of Petroleum and Minerals."

import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from channel_cog import ChannelCog
from models import Guild


def create_bot() -> commands.Bot:
    """
    Create an instance of the bot and adds commands and Cogs
    :return: The created Discord bot instance
    """
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
        print(f'{client.user.name} has connected to Discord!')

        print('Bot is connected to server/s:')
        guild: discord.Guild
        for guild in client.guilds:
            print(f'\t"{guild.name}"')

    @client.command(name='init', aliases=['setup'], help='Initialize the bot to this server.')
    @commands.has_guild_permissions(**command_permissions)
    async def initialize(ctx: commands.Context):
        setup_message: discord.Message = await ctx.send('initializing bot in server...')
        guild: discord.Guild = ctx.guild

        # get guild object from database if it exists otherwise insert into database
        guild_db: Guild
        guild_db, created, *_ = Guild.get_or_create(discord_id=guild.id, defaults=dict(name=guild.name))
        if created:
            print(f'Guild {guild.name} was added to db.')
        else:
            print(f'Guild {guild.name} was already in db.')

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
    bot = create_bot()
    token = os.getenv('DISCORD_TOKEN')
    bot.run(token)


if __name__ == '__main__':
    load_dotenv()
    main()
