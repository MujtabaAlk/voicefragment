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


class ChannelType(BaseModel):
    id = AutoField()
    name = CharField()

    class Meta:
        table_name = 'channel_type'


class Channel(BaseModel):
    id = AutoField()
    discord_id = IntegerField(unique=True)
    name = CharField()
    type = ForeignKeyField(ChannelType, backref='channels')
    guild = ForeignKeyField(Guild, backref='channels')
    category = ForeignKeyField(ChannelCategory, backref='channels')
