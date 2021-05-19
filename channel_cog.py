"""
This module contains the discord cog for managing channels
"""

import discord
from discord.ext import commands


class ChannelCog(commands.Cog):

    def __init__(self, bot: commands.Bot, text_category: int, voice_category: int):
        self.bot = bot
        self.text_category = text_category
        self.voice_category = voice_category

    @commands.command(help='create a new text channel')
    async def new_text(self, ctx: commands.Context, channel_name: str):
        """Create a new text function in the category given when bot is initialized"""
        guild: discord.Guild = ctx.guild
        category: discord.CategoryChannel = discord.utils.get(guild.categories, id=self.text_category)
        new_channel: discord.TextChannel = await guild.create_text_channel(channel_name, category=category)

        response = f'The text channel {new_channel.mention}\t was created'
        await ctx.send(response)

    @commands.command(help='create a new voice channel')
    async def new_voice(self, ctx: commands.Context, channel_name: str):
        """Create a new voice function in the category given when bot is initialized"""
        guild: discord.Guild = ctx.guild
        category: discord.CategoryChannel = discord.utils.get(guild.categories, id=self.voice_category)
        new_channel: discord.TextChannel = await guild.create_voice_channel(channel_name, category=category)

        response = f'The voice channel {new_channel.mention}\t was created'
        await ctx.send(response)
