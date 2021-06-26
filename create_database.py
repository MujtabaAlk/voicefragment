"""
This module initializes the database.
"""
from models import database, Guild, ChannelCategory, VoiceChannel, ChannelOwner


def main():
    """
    Main function of module.
    """
    tables = [Guild, ChannelCategory, VoiceChannel, ChannelOwner]
    print('Creating Tables...')
    database.create_tables(tables)
    print('Database initialized.')


if __name__ == '__main__':
    main()
