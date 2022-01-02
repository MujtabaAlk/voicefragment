# VoiceFragment

A discord bot that creates temporary voice channels upon joining.

## Installation

To run the bot follow the steps:

1. create a .env file with the same variables found in .env.example file.
    * *note: The DATABASE variable is optional, though it is recommended. without it the bot will use an SQLite
      database.*

2. run the `create_database.py` file to create the tables in the database.

```shell
python create_database.py
```

3. start the bot by running the `main.py` file.

```shell
python main.py
```

## Usage

### Discord setup

Follow these instructions once the bot is running/deployed:

1. added the bot to a Discord server with the following permission:
    - View Channels.
    - Manage Channels.
    - Manage Messages.
    - Send Messages.
    - Move Members.

2. run the command `!init` to initialize the bot to the server.

### Commands

| Command                        | Description                                                  | Example                                         |
|--------------------------------|--------------------------------------------------------------|-------------------------------------------------|
| !add_voice <#channelID>        | enables fragment ability on the voice channel                | !add_voice <#724723778547989516>                |
| !remove_voice <#channelID>     | disables fragment ability on the voice channel               | !remove_voice <#724723778547989516>             |
| !add_category <#categoryID>    | enables fragment ability on all voice channel in a category  | !add_category <#723724768043687501>             |
| !remove_category <#categoryID> | disables fragment ability on all voice channel in a category | !remove_category <#723724768043687501>          |
| !list_voice                    | displays a list of fragment enabled channels                 | !voice_list                                     |
| !voice_limit n                 | changes the user limit of the voice channel to n users       | !voice_limit 5                                  |
| !voice_name  NewName           | changes the name of the voice channel                        | !voice_name ChannelA or !voice_name "Channel A" |

#### notes

1. !voice_limit and !voice_name must be issued by the channel owner.
    * the channel owner is user the temporary channel is created for, if the owner exits ownership will be given to
      another user.
2. channel and category IDs can be obtained by enable developer mode and right-clicking the channel/category.