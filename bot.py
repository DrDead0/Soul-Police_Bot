import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
import os
from collections import defaultdict
import time
from datetime import timedelta
import asyncio  # For timing operations and sleeping
import sys  # For system calls, used in the reload command

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
APPLICATION_ID = os.getenv("APPLICATION_ID")
GUILD_ID = int(os.getenv("GUILD_ID"))  # Replace with your guild ID

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

class ModerationBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            application_id=APPLICATION_ID
        )
        self.message_log = defaultdict(list)
        self.warnings = defaultdict(list)
        self.banned_users = set()
        self.filters = set()

    async def setup_hook(self):
        await self.tree.sync()

bot = ModerationBot()

SPAM_THRESHOLD = 50  # Messages in a minute for spam detection
MUTE_DURATION = 10  # Default mute duration (minutes)
TEMPBAN_DURATION = 10  # Default tempban duration (minutes)

# Event: Bot Ready
@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready to moderate!")
    await bot.change_presence(activity=discord.Game(name="⚔️ Moderating the server! ⚔️"))
    auto_moderation.start()

# Task: Auto Moderation Loop
@tasks.loop(seconds=60)
async def auto_moderation():
    for user_id, timestamps in bot.message_log.items():
        if len(timestamps) > SPAM_THRESHOLD:
            guild = bot.get_guild(GUILD_ID)
            member = guild.get_member(user_id)
            if member:
                await auto_mute(member, guild, reason="Spamming detected.")
                bot.message_log[user_id].clear()

# Helper Functions
def get_moderation_channel(guild):
    for channel in guild.text_channels:
        if channel.name == "moderation-log":
            return channel
    return None

async def auto_mute(member, guild, reason):
    try:
        duration = MUTE_DURATION * 60
        await member.timeout(discord.utils.utcnow() + timedelta(seconds=duration), reason=reason)
        moderation_log = get_moderation_channel(guild)
        if moderation_log:
            await moderation_log.send(f"🔇 **Auto-moderation**: Muted {member.mention} for **{reason}**.")
    except Exception as e:
        print(f"Error muting {member}: {e}")

# Event: Message Spam Detection
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    current_time = time.time()
    bot.message_log[message.author.id].append(current_time)

    bot.message_log[message.author.id] = [
        msg_time for msg_time in bot.message_log[message.author.id]
        if current_time - msg_time <= 60
    ]

    if len(bot.message_log[message.author.id]) > SPAM_THRESHOLD:
        await auto_mute(message.author, message.guild, reason="Spamming detected.")
        bot.message_log[message.author.id].clear()


    if message.content.lower() == "!rules":
        rules_message = """
    **📜 Server Rules 📜**

    **1️⃣ Follow Discord's TOS & Guidelines**  
    Respect Discord's Terms of Service and community guidelines. This is the foundation for everything

    **2️⃣ Use Bots Responsibly**  
    Bots are here to assist, not to be spammed or abused. Be respectful in their usage

    **3️⃣ Zero Tolerance for Racism**  
    Racism, hate speech, or any discriminatory behavior will not be tolerated. Keep it respectful and kind

    **4️⃣ Stay Organized**  
    Use the appropriate channels for your discussions. It helps keep the server tidy and everyone informed

    **5️⃣ No NSFW Content**  
    Keep content appropriate for all ages. No adult content, explicit language, or offensive material

    **6️⃣ Respect in Voice Channels**  
    No screaming, spamming, or disrupting others in voice channels. Keep it fun for everyone

    **7️⃣ No Spamming**  
    Whether it's text, images, emojis, or links—avoid excessive spamming. Keep conversations clear and engaging

    **8️⃣ No Begging**  
    Don’t ask for currency, roles, Nitro, or other in-game advantages. Be patient and work for your goals

    **9️⃣ Advertisements Only in Designated Channels**  
    Want to promote something? Please do so in the channels created for that purpose only
    
    **🔟 Use Common Sense**  
    Treat others how you want to be treated. Be respectful, considerate, and kind
    Let's create a friendly, fun, and respectful environment for everyone! 🙌
    """
    await message.channel.send(rules_message)



    if message.content.lower() == "!welcome":
        welcome_message = """
        🎉 **Welcome to the Server!** 🎉  
        We're so excited to have you here! 🥳  
        Take a moment to read our rules and enjoy your time. If you have questions, don't hesitate to ask! 😄  
        """
        await message.channel.send(welcome_message)

    await bot.process_commands(message)

# All Slash Commands (Basic, Advanced, Utility, and More)
@bot.tree.command(name="kick", description="Kick a user from the server.")
@app_commands.describe(member="The user to kick", reason="Reason for the kick")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ You lack permission to kick members.", ephemeral=True)
        return
    await member.kick(reason=reason)
    await interaction.response.send_message(f"✅ {member.mention} has been kicked. **Reason**: {reason}")

@bot.tree.command(name="ban", description="Ban a user from the server.")
@app_commands.describe(member="The user to ban", reason="Reason for the ban")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ You lack permission to ban members.", ephemeral=True)
        return
    await member.ban(reason=reason)
    await interaction.response.send_message(f"✅ {member.mention} has been banned. **Reason**: {reason}")

@bot.tree.command(name="unban", description="Unban a user from the server.")
@app_commands.describe(member="The user to unban")
async def unban(interaction: discord.Interaction, member: discord.User):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ You lack permission to unban members.", ephemeral=True)
        return
    await interaction.guild.unban(member)
    await interaction.response.send_message(f"✅ {member.mention} has been unbanned.")

# Utility Command: /userinfo
@bot.tree.command(name="userinfo", description="Get information about a user.")
@app_commands.describe(user="The user to get information about")
async def userinfo(interaction: discord.Interaction, user: discord.Member):
    embed = discord.Embed(title=f"User Info: {user.name}", color=discord.Color.blue())
    embed.add_field(name="ID", value=user.id, inline=False)
    embed.add_field(name="Joined Server", value=user.joined_at.strftime('%Y-%m-%d %H:%M:%S'), inline=False)
    embed.add_field(name="Account Created", value=user.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=False)
    embed.set_thumbnail(url=user.avatar.url)
    await interaction.response.send_message(embed=embed)

# Utility Command: /serverinfo
@bot.tree.command(name="serverinfo", description="Get information about the server.")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"Server Info: {guild.name}", color=discord.Color.green())
    embed.add_field(name="Server ID", value=guild.id, inline=False)
    embed.add_field(name="Member Count", value=guild.member_count, inline=False)
    embed.add_field(name="Created At", value=guild.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=False)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else "")
    await interaction.response.send_message(embed=embed)

# Moderation Command: /purge
@bot.tree.command(name="purge", description="Delete a number of messages in a channel.")
@app_commands.describe(number="Number of messages to delete")
async def purge(interaction: discord.Interaction, number: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ You lack permission to manage messages.", ephemeral=True)
        return

    await interaction.channel.purge(limit=number)
    await interaction.response.send_message(f"✅ Purged {number} messages.", ephemeral=True)

# Moderation Command: /lock
@bot.tree.command(name="lock", description="Lock a channel.")
@app_commands.describe(channel="The channel to lock")
async def lock(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ You lack permission to manage channels.", ephemeral=True)
        return

    channel = channel or interaction.channel
    overwrite = channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = False
    await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message(f"✅ Locked channel {channel.mention}.")

# Command to Reload the Bot
@bot.command()
async def reload(ctx):
    """Reloads the bot (useful for development)."""
    if ctx.author.id != 1234567890:  # Replace with your Discord ID
        await ctx.send("You don't have permission to reload the bot.")
        return

    try:
        await ctx.send("Reloading bot...")
        await bot.close()
        os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e:
        await ctx.send(f"Error reloading the bot: {e}")

#warn
# Dictionary to track warnings
warnings = defaultdict(list)

# Slash Command: Warn
@bot.tree.command(name="warn", description="Warn a user for breaking the rules.")
@app_commands.describe(member="The user to warn", reason="Reason for the warning")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("You don't have permission to warn members.", ephemeral=True)
        return

    # Store the warning
    warnings[member.id].append(reason)

    # Send feedback to the moderator
    await interaction.response.send_message(
        f"{member.mention} has been warned for: **{reason}**. This is warning #{len(warnings[member.id])}."
    )

    # Notify the user privately
    try:
        await member.send(
            f"⚠️ You have been warned in **{interaction.guild.name}**.\n"
            f"**Reason:** {reason}\n"
            f"Please adhere to the server rules to avoid further action."
        )
    except discord.Forbidden:
        await interaction.followup.send(f"Could not DM {member.mention} about the warning.", ephemeral=True)
#logs
# Dictionary to keep track of the number of warnings, bans, and mutes
class ModerationBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            application_id=APPLICATION_ID
        )
        self.warned_count = 0  # Keep track of warned users
        self.banned_count = 0  # Keep track of banned users
        self.muted_count = 0  # Keep track of muted users

    # Add these to the respective actions when warnings, bans, or mutes are triggered
    async def on_warning(self, member):
        self.warned_count += 1

    async def on_ban(self, member):
        self.banned_count += 1

    async def on_mute(self, member):
        self.muted_count += 1

# Adding the logs command to the bot
@bot.tree.command(name="logs", description="Display bot moderation logs.")
async def logs(interaction: discord.Interaction):
    # Create an embed to show the logs in a fancy format
    embed = discord.Embed(
        title="Bot Moderation Logs",
        description="Detailed moderation logs for the bot.",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="Total Warnings",
        value=f"⚠️ **{bot.warned_count}** users have been warned.",
        inline=False
    )
    embed.add_field(
        name="Total Bans",
        value=f"🚫 **{bot.banned_count}** users have been banned.",
        inline=False
    )
    embed.add_field(
        name="Total Mutes",
        value=f"🔇 **{bot.muted_count}** users have been muted.",
        inline=False
    )

    embed.add_field(
        name="Additional Info",
        value="The bot tracks warnings, bans, and mutes as part of its moderation system.",
        inline=False
    )

    await interaction.response.send_message(embed=embed)

# When a warning is issued (as an example of how to use the logs)
async def issue_warning(member, reason="No reason provided"):
    await bot.on_warning(member)  # Update the count for warnings
    # Log warning message (This can be logged to a log channel or simply printed)
    print(f"Warning issued to {member.name}: {reason}")
    await member.send(f"You have been warned: {reason}")

# When a user is banned (similarly, updating the banned count)
async def issue_ban(member, reason="No reason provided"):
    await bot.on_ban(member)  # Update the count for bans
    # Log the ban
    print(f"Ban issued to {member.name}: {reason}")
    await member.send(f"You have been banned: {reason}")

# When a user is muted (similarly, updating the muted count)
async def issue_mute(member, reason="No reason provided"):
    await bot.on_mute(member)  # Update the count for mutes
    # Log the mute
    print(f"Mute issued to {member.name}: {reason}")
    await member.send(f"You have been muted: {reason}")

#fakeban and Fake kick
@bot.tree.command(name="fakeban", description="Simulate banning a user without actually banning them.")
async def fakeban(interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):
    # Simulate the fake ban by sending a message
    await interaction.response.send_message(
        f"🚫 **{user.name}** has been **FAKE-BANNED** for: {reason}",
        ephemeral=True  # The message is only visible to the user who used the command
    )
    # Optionally, you can also send a fake ban message to the server or log the event
    print(f"Fake ban simulated for {user.name} due to: {reason}")
    # Sending the fake ban to the server (optional)
    channel = discord.utils.get(interaction.guild.text_channels, name="general")
    if channel:
        await channel.send(f"🚫 **{user.name}** has been **FAKE-BANNED** for: {reason}")

@bot.tree.command(name="fakekick", description="Simulate kicking a user without actually kicking them.")
async def fakekick(interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):
    # Simulate the fake kick by sending a message
    await interaction.response.send_message(
        f"👢 **{user.name}** has been **FAKE-KICKED** for: {reason}",
        ephemeral=True  # The message is only visible to the user who used the command
    )
    # Optionally, you can also send a fake kick message to the server or log the event
    print(f"Fake kick simulated for {user.name} due to: {reason}")
    # Sending the fake kick to the server (optional)
    channel = discord.utils.get(interaction.guild.text_channels, name="general")
    if channel:
        await channel.send(f"👢 **{user.name}** has been **FAKE-KICKED** for: {reason}")
#slowmode
@bot.tree.command(name="slowmode", description="Set the slowmode in the channel.")
async def slowmode(interaction: discord.Interaction, duration: int):
    # Ensure the user has permission to manage messages (moderator check)
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    # Check if the duration is valid (between 0 and 21600 seconds, Discord's limit for slowmode)
    if duration < 0 or duration > 21600:
        await interaction.response.send_message("Please provide a valid duration (between 0 and 21600 seconds).", ephemeral=True)
        return

    # Set the slowmode in the current channel
    await interaction.channel.edit(slowmode_delay=duration)

    # Send a confirmation message
    if duration == 0:
        await interaction.response.send_message(f"Slowmode has been disabled in {interaction.channel.mention}.", ephemeral=True)
    else:
        await interaction.response.send_message(f"Slowmode has been set to {duration} seconds in {interaction.channel.mention}.", ephemeral=True)



bot.run(BOT_TOKEN)
