"""
This module contains the data models for the system.
"""
import os

from peewee import *
from playhouse.db_url import connect
from dotenv import load_dotenv

load_dotenv()

database = connect(os.getenv('DATABASE') or 'sqlite:///discord.db')


class BaseModel(Model):
    class Meta:
        database = database


class Guild(BaseModel):
    id = AutoField()
    discord_id = IntegerField(unique=True)
    name = CharField()


class ChannelCategory(BaseModel):
    id = AutoField()
    discord_id = IntegerField(unique=True)
    name = CharField()
    guild = ForeignKeyField(Guild, backref='categories')

    class Meta:
        table_name = 'channel_category'


class VoiceChannel(BaseModel):
    id = AutoField()
    discord_id = IntegerField(unique=True)
    name = CharField()
    guild = ForeignKeyField(Guild, backref='voice_channels')
    category = ForeignKeyField(ChannelCategory, backref='voice_channels')

    class Meta:
        table_name = 'voice_channel'


class TextChannel(BaseModel):
    id = AutoField()
    discord_id = IntegerField(unique=True)
    name = CharField()
    guild = ForeignKeyField(Guild, backref='text_channel')
    category = ForeignKeyField(ChannelCategory, backref='text_channel')

    class Meta:
        table_name = 'text_channel'