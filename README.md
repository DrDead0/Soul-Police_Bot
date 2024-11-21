

# Captain Deity Discord Bot 
![Captain Deity Bot Logo](https://github.com/YourRepo/Captain-Deity-Bot/blob/main/Assets/logo.png)  

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Table of Contents

- [Captain Deity Discord Bot](#captain-deity-discord-bot)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Configuration](#configuration)
  - [Commands](#commands)
    - [Moderation Commands](#moderation-commands)
    - [Utility Commands](#utility-commands)
    - [Fun \& Engagement Commands](#fun--engagement-commands)
    - [Default Message Commands](#default-message-commands)
  - [Contribution](#contribution)
    - [How to Contribute](#how-to-contribute)
  - [Support](#support)
  - [Contact](#contact)
  - [License](#license)



## Introduction

**Captain Deity** is a robust Discord bot designed to help server admins maintain order and engage their communities. From moderating unruly shipmates (members) to delivering critical server commands, Captain Deity brings the **spirit of a pirate captain** to your Discord server. ⚓️🏴‍☠️  

Whether you’re looking to automatically moderate spam, manage roles, or even simulate some fun “fake punishments,” this bot is ready to command your ship (server) with flair.



## Features

- 🏴 **Auto-Moderation**: Detects and prevents spam, issues warnings, mutes, or bans troublesome users.  
- 📜 **Rule Management**: Quickly display server rules to new and existing members.  
- 🎉 **Welcome Messages**: Greets new users in style.  
- 📊 **Detailed Moderation Logs**: Track all warnings, bans, and mutes for better transparency.  
- ⚙️ **Server Utility**: Commands for locking channels, purging messages, setting slow modes, and more.  
- ⚠️ **Fake Punishments**: Simulate a fake ban or kick for fun, or as a warning to others.  
- 🚨 **Customizable Commands**: Tailor Captain Deity to meet your server’s unique needs.



## Installation

Follow these steps to set up Captain Deity on your server:

1. Clone the repository:  

    ```bash
    git clone https://github.com/DrDead0/Soul-Police_Bot.git
    ```

2. Navigate to the project directory:  

    ```bash
    cd Captain-Deity-Bot
    ```

3. Install the dependencies:  

    ```bash
    pip install -r requirements.txt
    ```

4. Set up your environment variables in a `.env` file:  

    ```bash
    BOT_TOKEN=your_bot_token
    APPLICATION_ID=your_application_id
    GUILD_ID=your_guild_id
    ```

5. Run the bot:  

    ```bash
    python bot.py
    ```



## Usage

Once installed and running, Captain Deity will come online and begin moderating your server.  
Use the available commands for moderation, user engagement, and fun pirate-themed interactions.



## Configuration

You can tweak Captain Deity’s behavior through the `.env` file or by modifying settings directly in the code.  

Key variables:  

- `BOT_TOKEN`: Your bot's unique token.  
- `GUILD_ID`: Your server's unique ID.  
- `MUTE_DURATION`: Default mute duration in minutes (e.g., `10`).  
- `TEMPBAN_DURATION`: Default temporary ban duration in minutes (e.g., `10`).  



## Commands

Here’s a list of Captain Deity’s core commands:  

### Moderation Commands
- **/kick [member] [reason]**: Kick a member from the server.  
- **/ban [member] [reason]**: Ban a member from the server.  
- **/unban [user]**: Unban a previously banned user.  
- **/warn [member] [reason]**: Issue a warning to a member.  
- **/purge [number]**: Delete a specified number of messages.  
- **/lock [channel]**: Lock a channel to prevent sending messages.  
- **/slowmode [duration]**: Set the slow mode duration for a channel.  

### Utility Commands
- **/userinfo [user]**: Display details about a user.  
- **/serverinfo**: Get detailed information about the server.  

### Fun & Engagement Commands
- **/fakeban [user] [reason]**: Pretend to ban a user.  
- **/fakekick [user] [reason]**: Pretend to kick a user.  

### Default Message Commands
- `!welcome`: Sends a pirate-themed welcome message.  
- `!rules`: Posts the server rules in chat.  



## Contribution

We believe that the best ships are built by the hands of many skilled sailors! 🛠️  
Contributions to **Captain Deity** are welcome and highly appreciated. Whether it's fixing bugs, adding new features, or improving documentation, every effort helps this bot grow stronger.

### How to Contribute

1. Fork the repository to your own GitHub account.  
2. Create a new branch for your changes:  

    ```bash
    git checkout -b feature/new-feature
    ```

3. Make your changes and commit them with a clear message:  

    ```bash
    git commit -m "Add new feature: ..."
    ```

4. Push your changes to your forked repository:  

    ```bash
    git push origin feature/new-feature
    ```

5. Submit a pull request to this repository's main branch.  


## Support

Having trouble with Captain Deity? Raise an issue on the [GitHub repository](https://github.com/YourRepo/Captain-Deity-Bot/issues).  

For immediate assistance, contact the developer directly.  



## Contact

Created by **[Ashish Chaurasiya](https://github.com/DrDead0)**, inspired by the high seas and the pirate’s code! 🏴‍☠️  

Feel free to reach out with questions, feedback, or collaboration ideas.



## License

Captain Deity is licensed under the MIT License. See the [LICENSE](https://github.com/YourRepo/Captain-Deity-Bot/blob/main/LICENSE) file for more details.  

