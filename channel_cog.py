"""
This module contains the discord cog for managing channels
"""
import asyncio
from typing import Optional
from uuid import uuid4, UUID

import discord
from discord.ext import commands

from models import Guild, ChannelCategory, VoiceChannel, ChannelOwner


class ChannelCog(commands.Cog, name="Channel Commands"):
    """
    A command Cog that handles functionalities related to channels
    """

    command_permissions: dict = dict(
        manage_channels=True, manage_messages=True, move_members=True
    )
    message_delete_delay: int = 10

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(help="Add voice channel to the database")
    @commands.has_guild_permissions(**command_permissions)
    async def add_voice(
        self, ctx: commands.Context, channel: discord.VoiceChannel
    ):
        """
        Add the voice channel to the database enabling the fragment ability.
        :param ctx: the command context
        :param channel: the voice Channel to add
        """
        guild_db, category_db, bot_init = _get_guild_and_category_db_or_false(
            ctx.guild, channel.category
        )
        if not bot_init:
            await ctx.send("you must initialize bot in the server first")
            return

        channel_db: VoiceChannel
        channel_db, created = VoiceChannel.get_or_create(
            discord_id=channel.id,
            defaults=dict(
                name=channel.name, guild=guild_db, category=category_db
            ),
        )
        if created:
            await ctx.send(
                f"Channel {channel.mention} is now a fragment channel",
                delete_after=self.message_delete_delay,
            )
            await ctx.message.delete(delay=self.message_delete_delay)
        else:
            await ctx.send(
                f"Channel {channel.mention} is already a fragment channel",
                delete_after=self.message_delete_delay,
            )
            await ctx.message.delete(delay=self.message_delete_delay)

    @commands.command(
        aliases=["delete_voice"],
        help="Remove a voice channel from the database",
    )
    @commands.has_guild_permissions(**command_permissions)
    async def remove_voice(
        self, ctx: commands.Context, channel: discord.VoiceChannel
    ):
        """
        Remove the voice channel from the database disabling its fragment ability
        :param ctx: the command context
        :param channel: the voice channel to remove
        """
        channel_db: VoiceChannel = VoiceChannel.get_or_none(
            discord_id=channel.id
        )
        if channel_db is None:
            await ctx.send(
                f"Channel {channel.mention} is not a fragment channel",
                delete_after=self.message_delete_delay,
            )
            await ctx.message.delete(delay=self.message_delete_delay)
            return

        channel_db.delete_instance()
        await ctx.send(
            f"Channel {channel.mention} is no longer a fragment channel",
            delete_after=self.message_delete_delay,
        )
        await ctx.message.delete(delay=self.message_delete_delay)

    @commands.command(
        help="add a channel category and the channels within it."
    )
    @commands.has_guild_permissions(**command_permissions)
    async def add_category(
        self, ctx: commands.Context, category: discord.CategoryChannel
    ):
        """
        Add a channel category and the channels inside it to the database enabling the fragment ability.
        :param ctx: the command context
        :param category: the channel category to add
        """
        guild_db, category_db, bot_init = _get_guild_and_category_db_or_false(
            ctx.guild, category
        )
        if not bot_init:
            await ctx.send("you must initialize bot in the server first")
            return

        voice_channels: list[discord.VoiceChannel] = category.voice_channels
        if len(voice_channels) > 0:
            print("\t\tVoice channels:")
            for channel in voice_channels:
                print(f"\t\t\tChannel: {channel}")
                # get voice channel object from database if it exists otherwise insert into database
                voice_channel_db: VoiceChannel
                voice_channel_db, _ = VoiceChannel.get_or_create(
                    discord_id=channel.id,
                    defaults=dict(
                        name=channel.name, guild=guild_db, category=category_db
                    ),
                )
                print(f"\t\t\tChannel db: {voice_channel_db}")

        await ctx.send(
            f"Channels in category {category.mention} are now fragment channels",
            delete_after=self.message_delete_delay,
        )
        await ctx.message.delete(delay=self.message_delete_delay)

    @commands.command(
        aliases=["delete_category"],
        help="remove a channel category and the channels within it.",
    )
    @commands.has_guild_permissions(**command_permissions)
    async def remove_category(
        self, ctx: commands.Context, category: discord.CategoryChannel
    ):
        """
        Remove a category from the database disabling its fragment ability of channels inside it
        :param ctx: the command context
        :param category: the channel category to remove
        """
        category_db: ChannelCategory = ChannelCategory.get_or_none(
            discord_id=category.id
        )
        if category_db is None:
            await ctx.send(
                f"Category {category.mention} is not is not a fragment category",
                delete_after=self.message_delete_delay,
            )
            await ctx.message.delete(delay=self.message_delete_delay)
            return

        # delete voice channels
        VoiceChannel.delete().where(
            VoiceChannel.category == category_db
        ).execute()

        # delete category
        category_db.delete_instance()

        await ctx.send(
            f"Channels in category {category.mention} are no longer a fragment channels",
            delete_after=self.message_delete_delay,
        )
        await ctx.message.delete(delay=self.message_delete_delay)

    @commands.command(
        aliases=["display_voice", "show_voice", "list_fragment", "voice_list"],
        help="Display the voice channels with fragmentation enabled.",
    )
    @commands.has_guild_permissions(**command_permissions)
    async def list_voice(self, ctx: commands.Context):
        """
        Displays a list of fragment enabled channels.
        :param ctx: the command context
        """
        guild_db: Guild = Guild.get_or_none(discord_id=ctx.guild.id)
        if guild_db is None:
            await ctx.send(
                "you must initialize bot in the server first",
                delete_after=self.message_delete_delay,
            )
            await ctx.message.delete(delay=self.message_delete_delay)
            return

        result_message: str = "Fragment Channels:\n"
        categories_db: list[ChannelCategory] = list(
            ChannelCategory.select().where(ChannelCategory.guild == guild_db)
        )
        for category_db in categories_db:
            category: discord.CategoryChannel = discord.utils.find(
                lambda c: c.id == category_db.discord_id, ctx.guild.categories
            )
            result_message += f"{category.mention}\n"
            voice_channels_db: list[VoiceChannel] = list(
                VoiceChannel.select().where(
                    VoiceChannel.category == category_db
                )
            )
            for voice_channel_db in voice_channels_db:
                voice_channel: discord.VoiceChannel = discord.utils.find(
                    lambda c: c.id == voice_channel_db.discord_id,
                    category.voice_channels,
                )
                result_message += f"\t{voice_channel.mention}\n"

        await ctx.send(result_message)

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
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
                print("Entered AFK Channel!")
                return
            print(f"Connected to voice Channel: {after.channel}")
            channel_db: VoiceChannel = VoiceChannel.get_or_none(
                discord_id=after.channel.id
            )
            if channel_db is not None:
                print(f"Channel is in the database: {channel_db}")
                guild: discord.Guild = after.channel.guild
                category: discord.CategoryChannel = after.channel.category
                temp_channel_uuid: UUID = uuid4()
                temp_channel_name = (
                    after.channel.name + " fragment: " + str(temp_channel_uuid)
                )
                temp_voice_channel: discord.VoiceChannel = (
                    await guild.create_voice_channel(
                        name=temp_channel_name, category=category
                    )
                )
                await member.move_to(temp_voice_channel)
                channel_owner_db: ChannelOwner = ChannelOwner.create(
                    discord_id=member.id, channel_id=temp_voice_channel.id
                )

                def wait_to_empty(m, b, a):
                    if len(temp_voice_channel.members) == 0:
                        return True
                    if m.id == member.id and a.channel != temp_voice_channel:
                        new_owner: discord.Member = temp_voice_channel.members[
                            0
                        ]
                        channel_owner_db.discord_id = new_owner.id
                        channel_owner_db.save()

                    return False

                await self.bot.wait_for(
                    "voice_state_update", check=wait_to_empty
                )
                await temp_voice_channel.delete()
                channel_owner_db.delete_instance()
                await asyncio.sleep(5)
                print("Channel Deleted...")

            else:
                print("Channel is not in the database")
        else:
            print("Disconnected from voice channels")

    @commands.command(help="Change voice channel limit")
    async def voice_limit(self, ctx: commands.Context, limit: int):
        """
        Changes the user limit of the voice channel owned by the member
        :param ctx: the command context
        :param limit: new channel user limit
        """
        channel: discord.VoiceChannel = await _check_member_owns_channel(ctx)
        if channel is None:
            return

        print(
            f"Changing {channel.name} limit to from: {channel.user_limit}, to: {limit}"
        )
        await channel.edit(user_limit=limit)
        print(f"new limit: {channel.user_limit}")
        await ctx.send(
            f'{channel.mention} limit changed to {limit if limit > 0 else "no limit"}',
            delete_after=self.message_delete_delay,
        )
        await ctx.message.delete(delay=self.message_delete_delay)

    @commands.command(help="Change voice channel name")
    async def voice_name(self, ctx: commands.Context, new_name: str):
        """
        Changes the name of the voice channel owned by the member
        :param ctx: the command context
        :param new_name: new channel name
        """
        channel: discord.VoiceChannel = await _check_member_owns_channel(ctx)
        if channel is None:
            return

        print(f"Changing {channel.name} name to: {new_name}")
        await channel.edit(name=new_name)
        print(f"new name: {channel.name}")
        await ctx.send(
            f"{channel.mention} name changed",
            delete_after=self.message_delete_delay,
        )
        await ctx.message.delete(delay=self.message_delete_delay)


def _get_guild_and_category_db_or_false(
    guild: discord.Guild, category: discord.CategoryChannel
) -> (Guild, ChannelCategory, bool):
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
    category_db: ChannelCategory
    category_db, _ = ChannelCategory.get_or_create(
        discord_id=category.id,
        defaults=dict(name=category.name, guild=guild_db),
    )

    return guild_db, category_db, True


async def _check_member_owns_channel(
    ctx: commands.Context,
) -> Optional[discord.VoiceChannel]:
    """
    checks if a member owns a channel or not and returns the channel if true.
    :param ctx: the command context
    :return: the owned voice channel or none
    """
    channel_owner_db: ChannelOwner = ChannelOwner.get_or_none(
        discord_id=ctx.author.id
    )
    if channel_owner_db is None:
        print("no entry for member in database.")
        await ctx.send(
            f"You do not control a channel.",
            delete_after=ChannelCog.message_delete_delay,
        )
        await ctx.message.delete(delay=ChannelCog.message_delete_delay)
        return None

    owned_voice_channel: discord.VoiceChannel = discord.utils.find(
        lambda c: c.id == channel_owner_db.channel_id, ctx.guild.voice_channels
    )
    if owned_voice_channel is None:
        print("Channel not found in guild.")
        await ctx.send(
            f"You do not control a channel.",
            delete_after=ChannelCog.message_delete_delay,
        )
        await ctx.message.delete(delay=ChannelCog.message_delete_delay)
        return None

    return owned_voice_channel
