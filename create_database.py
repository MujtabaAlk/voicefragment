"""
This module initializes the database.
"""
from models import *


def main():
    tables = [Guild, ChannelCategory, ChannelType, Channel]
    print('Creating Tables...')
    database.create_tables(tables)
    print('Database initialized.')

    # Create channel types
    ChannelType.create(name='text channel')
    ChannelType.create(name='voice channel')


if __name__ == '__main__':
    main()
