"""
This module contains the data models for the system.
"""
import os

from peewee import Model, AutoField, IntegerField, CharField, ForeignKeyField
from playhouse.db_url import connect
from dotenv import load_dotenv

load_dotenv()

database = connect(os.getenv("DATABASE") or "sqlite:///discord.db")


class BaseModel(Model):
    """
    The base model class.
    """

    # pylint: disable=[missing-docstring, too-few-public-methods]
    class Meta:
        database = database


class Guild(BaseModel):
    """
    A class representing a Discord guild/server.
    """

    id = AutoField()
    discord_id = IntegerField(unique=True)
    name = CharField()


class ChannelCategory(BaseModel):
    """
    A class representing a Discord channel category.
    """

    id = AutoField()
    discord_id = IntegerField(unique=True)
    name = CharField()
    guild = ForeignKeyField(Guild, backref="categories")

    # pylint: disable=[missing-docstring, too-few-public-methods]
    class Meta:
        table_name = "channel_category"


class VoiceChannel(BaseModel):
    """
    A class representing a Discord voice channel.
    """

    id = AutoField()
    discord_id = IntegerField(unique=True)
    name = CharField()
    guild = ForeignKeyField(Guild, backref="voice_channels")
    category = ForeignKeyField(ChannelCategory, backref="voice_channels")

    # pylint: disable=[missing-docstring, too-few-public-methods]
    class Meta:
        table_name = "voice_channel"


class ChannelOwner(BaseModel):
    """
    A class representing a Discord member and the channel they own.
    """

    id = AutoField()
    discord_id = IntegerField(unique=True)
    channel_id = IntegerField(unique=True)

    # pylint: disable=[missing-docstring, too-few-public-methods]
    class Meta:
        table_name = "channel_owner"
