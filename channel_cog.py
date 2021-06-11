"""
This module contains the discord cog for managing channels
"""
import asyncio

import discord
from discord.ext import commands

from models import Guild, ChannelCategory, VoiceChannel, TextChannel


class ChannelCog(commands.Cog, name='Channel Commands'):
    """
    A command Cog that handles functionalities related to channels
    """
    command_permissions = dict(manage_channels=True,
                               manage_messages=True,
                               move_members=True)

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(help='Add voice channel to the database')
    @commands.has_guild_permissions(**command_permissions)
    async def add_voice(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Add the voice channel to the database making it a fragment channel.
        :param ctx: the command context
        :param channel: the voice Channel to add
        """
        guild_db, category_db, bot_init = _get_guild_and_category_db_or_false(ctx.guild, channel.category)
        if not bot_init:
            await ctx.send('you must initialize bot in the server first')
            return

        channel_db: VoiceChannel
        channel_db, created = VoiceChannel.get_or_create(discord_id=channel.id, defaults=dict(
            name=channel.name, guild=guild_db, category=category_db))
        if created:
            await ctx.send('Channel added to db', delete_after=15)
            await ctx.message.delete(delay=15)
        else:
            await ctx.send('Channel already in db', delete_after=15)
            await ctx.message.delete(delay=15)

    @commands.command(help='Add text channel to the database')
    @commands.has_guild_permissions(**command_permissions)
    async def add_text(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Add the text channel to the database.
        :param ctx: the command context
        :param channel: the text Channel to add
        """
        guild_db, category_db, bot_init = _get_guild_and_category_db_or_false(ctx.guild, channel.category)
        if not bot_init:
            await ctx.send('you must initialize bot in the server first')
            return

        channel_db: TextChannel
        channel_db, created = TextChannel.get_or_create(discord_id=channel.id, defaults=dict(
                        name=channel.name, guild=guild_db, category=category_db))
        if created:
            await ctx.send('Channel added to db', delete_after=15)
            await ctx.message.delete(delay=15)
        else:
            await ctx.send('Channel already in db', delete_after=15)
            await ctx.message.delete(delay=15)

    @commands.command(help='Change voice channel limit')
    async def voice_limit(self, ctx: commands.Context, channel: discord.VoiceChannel, limit: int):
        """
        Changes the user limit of the given voice channel
        :param ctx: the command context
        :param channel: target voice channel
        :param limit: new channel user limit
        """
        print(f'Changing {channel.name} limit to from: {channel.user_limit}, to: {limit}')
        await channel.edit(user_limit=limit)
        print(f'new limit: {channel.user_limit}')
        await ctx.send(f'{channel.mention} limit changed to {limit if limit>0 else "no limit"}')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member,
                                    before: discord.VoiceState,
                                    after: discord.VoiceState):
        """
            This function runs when a users/members voice status changes
            (ie. enter/exit a voice channel). If the channel the user enters is in the database,
            a new temporary channel is created and the user is moved into it. Whenever the
            temporary channel gets empty it is deleted.
            :param member: the member whose voice status just changed
            :param before: the previous voice state of the member
            :param after: the current/new voice state of the member
        """
        if after.channel is not None:
            if after.channel == member.guild.afk_channel:
                print('Entered AFK Channel!')
                return
            print(f'Connected to voice Channel: {after.channel}')
            channel_db: VoiceChannel = VoiceChannel.get_or_none(discord_id=after.channel.id)
            if channel_db is not None:
                print(f'Channel is in the database: {channel_db}')
                guild: discord.Guild = after.channel.guild
                category: discord.CategoryChannel = after.channel.category
                temp_channel_name = after.channel.name + " temp"
                temp_voice_channel: discord.VoiceChannel = await guild.create_voice_channel(name=temp_channel_name,
                                                                                            category=category)
                await member.move_to(temp_voice_channel)

                def wait_to_empty(m, b, a):
                    return len(temp_voice_channel.members) == 0
                await self.bot.wait_for('voice_state_update', check=wait_to_empty)
                await temp_voice_channel.delete()
                await asyncio.sleep(5)
                print('Channel Deleted...')

            else:
                print('Channel is not in the database')
        else:
            print('Disconnected from voice channels')


def _get_guild_and_category_db_or_false(guild: discord.Guild, category: discord.CategoryChannel) \
        -> (Guild, ChannelCategory, bool):
    """
    check if the bot is initialized by checking if guild is in the database,
    and get or add the channel category to the database.
    :param guild: the discord guild object
    :param category: the discord channel category object
    :returns:(Guild: guild database object,
            ChannelCategory: category database object,
            bool: boolean true if bot has been initialized)
    """
    guild_db: Guild = Guild.get_or_none(discord_id=guild.id)
    if guild_db is None:
        return None, None, False
    category_db, _ = ChannelCategory.get_or_create(discord_id=category.id, defaults=dict(
        name=category.name, guild=guild_db))
    category_db: ChannelCategory

    return guild_db, category_db, True
