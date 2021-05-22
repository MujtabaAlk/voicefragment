"""
This is the main entry point for the program.
"""
__author__ = "Mojtaba Alkhalifah"

import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from channel_cog import ChannelCog
from models import database, Guild, Channel, ChannelCategory, ChannelType


def create_bot() -> commands.Bot:
    guild_name = os.getenv('GUILD_NAME')
    text_category_id = 720722777803456515
    voice_category_id = 720722778243989504
    command_permissions = dict(manage_channels=True,
                               manage_messages=True,
                               move_members=True)
    help_command = commands.DefaultHelpCommand(no_category='Global Commands')
    intents: discord.Intents = discord.Intents.default()
    intents.members = True
    intents.voice_states = True
    client: commands.Bot = commands.Bot(command_prefix='!',
                                        help_command=help_command,
                                        intents=intents)

    @client.event
    async def on_ready():
        guild: discord.Guild = discord.utils.get(client.guilds, name=guild_name)

        print(f'{client.user.name} has connected to Discord!')
        if guild is not None:
            print(f'Bot is connected to server "{guild.name}".')

    @client.command(name='init', aliases=['setup'], help='Initialize the bot to this server.')
    @commands.has_guild_permissions(**command_permissions)
    async def initialize(ctx: commands.Context):
        print(f'permissions: {ctx.author.permissions_in(ctx.channel)}')
        setup_message: discord.Message = await ctx.send('initializing bot in server...')
        text_channel_type_db = ChannelType.get_by_id(1)
        voice_channel_type_db = ChannelType.get_by_id(2)
        guild: discord.Guild = ctx.guild
        print(f'Guild: {guild}')

        # get guild object from database if it exists otherwise insert into database
        guild_db: Guild
        guild_db, _ = Guild.get_or_create(discord_id=guild.id, defaults=dict(name=guild.name))
        print(f'Guild db: {guild_db}')

        categories: list[discord.CategoryChannel] = guild.categories
        for category in categories:
            print(f'\tCategory: {category}')

            # get category object from database if it exists otherwise insert into database
            category_db: ChannelCategory
            category_db, _ = ChannelCategory.get_or_create(discord_id=category.id, defaults=dict(
                name=category.name, guild=guild_db))
            print(f'\tCategory db: {category_db}')

            text_channels: list[discord.TextChannel] = category.text_channels
            if len(text_channels) > 0:
                print('\t\tText channels:')
                for channel in text_channels:
                    print(f'\t\t\tChannel: {channel}')
                    # get text channel object from database if it exists otherwise insert into database
                    channel_db: Channel
                    channel_db, _ = Channel.get_or_create(discord_id=channel.id, defaults=dict(
                        name=channel.name, type=text_channel_type_db, guild=guild_db, category=category_db))
                    print(f'\t\t\tChannel db: {channel_db}')

            voice_channels: list[discord.VoiceChannel] = category.voice_channels
            if len(voice_channels) > 0:
                print('\t\tVoice channels:')
                for channel in voice_channels:
                    print(f'\t\t\tChannel: {channel}')
                    # get voice channel object from database if it exists otherwise insert into database
                    channel_db: Channel
                    channel_db, _ = Channel.get_or_create(discord_id=channel.id, defaults=dict(
                        name=channel.name, type=voice_channel_type_db, guild=guild_db, category=category_db))
                    print(f'\t\t\tChannel db: {channel_db}')

        await setup_message.delete(delay=5)
        await ctx.message.delete(delay=5)

    # add the channel cog
    client.add_cog(ChannelCog(client, text_category_id, voice_category_id))

    return client


def main():
    bot = create_bot()
    token = os.getenv('DISCORD_TOKEN')
    bot.run(token)


if __name__ == '__main__':
    load_dotenv()
    main()
