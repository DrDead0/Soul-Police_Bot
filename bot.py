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
        📜 **Server Rules** 📜
        1️⃣ **Discord TOS & Guidelines**: Follow Discord's rules!  
        2️⃣ **Bot Rules**: Use bots appropriately.  
        3️⃣ **No Racism**: Zero tolerance policy.  
        4️⃣ **Stay Organized**: Use channels correctly.  
        5️⃣ **No NSFW Content**: Keep it clean!  
        6️⃣ **Respect Voice Channels**: No screaming or spam.  
        7️⃣ **No Spam**: Text, image, or emoji spamming is not allowed.  
        8️⃣ **No Begging**: For currency or Nitro.  
        9️⃣ **Advertisements**: Use proper channels.  
        🔟 **Common Sense**: Be respectful and kind!  
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

bot.run(BOT_TOKEN)
