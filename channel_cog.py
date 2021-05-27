"""
This module contains the discord cog for managing channels
"""
import asyncio

import discord
from discord.ext import commands

from models import Guild, ChannelCategory, VoiceChannel, TextChannel


class ChannelCog(commands.Cog, name='Channel Commands'):
    command_permissions = dict(manage_channels=True,
                               manage_messages=True,
                               move_members=True)

    def __init__(self, bot: commands.Bot, text_category: int, voice_category: int):
        self.bot = bot
        self.text_category = text_category
        self.voice_category = voice_category

    @commands.command(help='Create a new text channel')
    async def new_text(self, ctx: commands.Context, channel_name: str):
        """Create a new text function in the category given when bot is initialized"""
        guild: discord.Guild = ctx.guild
        category: discord.CategoryChannel = discord.utils.get(guild.categories, id=self.text_category)
        new_channel: discord.TextChannel = await guild.create_text_channel(channel_name, category=category)

        response = f'The text channel {new_channel.mention}\t was created'
        await ctx.send(response)

    @commands.command(help='Create a new voice channel')
    async def new_voice(self, ctx: commands.Context, channel_name: str):
        """Create a new voice function in the category given when bot is initialized"""
        guild: discord.Guild = ctx.guild
        category: discord.CategoryChannel = discord.utils.get(guild.categories, id=self.voice_category)
        new_channel: discord.VoiceChannel = await guild.create_voice_channel(channel_name, category=category)

        response = f'The voice channel {new_channel.mention}\t was created'
        await ctx.send(response)

    @commands.command(help='Add voice channel to the database')
    @commands.has_guild_permissions(**command_permissions)
    async def add_voice(self, ctx: commands.Context, channel: discord.VoiceChannel):
        guild_db: Guild = Guild.get_or_none(discord_id=ctx.guild.id)
        category_db: ChannelCategory = ChannelCategory.get_or_none(discord_id=channel.category_id)
        if guild_db is None or category_db is None:
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

    @commands.command(help='Change voice channel limit')
    async def voice_limit(self, ctx: commands.Context, channel: discord.VoiceChannel, limit: int):
        """Changes the user limit of the given voice channel"""
        print(f'Changing {channel.name} limit to from: {channel.user_limit}, to: {limit}')
        await channel.edit(user_limit=limit)
        print(f'new limit: {channel.user_limit}')
        await ctx.send(f'{channel.mention} limit changed to {limit if limit>0 else "no limit"}')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member,
                                    before: discord.VoiceState,
                                    after: discord.VoiceState):

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
