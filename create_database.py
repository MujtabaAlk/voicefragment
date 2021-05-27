"""
This module initializes the database.
"""
from models import *


def main():
    tables = [Guild, ChannelCategory, VoiceChannel, TextChannel]
    print('Creating Tables...')
    database.create_tables(tables)
    print('Database initialized.')


if __name__ == '__main__':
    main()
