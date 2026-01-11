import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Note: We changed reset_channels to setup_channels in the previous step
from message_handler import roles_message, setup_channels, general_message
from reaction_handler import handle_reaction_add, handle_reaction_remove
from code_handler import code_verification
from role_handler import give_role, remove_role
from command_handler import gulag_command, padawan_command, code_command
from heartbeat_monitor import monitor_heartbeat_logs

class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reaction_message = None
        self.code_message = None
        self.heartbeat_task = None
    
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        
        # Hardcoded Guild ID (Ideally move this to an env var or config later)
        guild = self.get_guild(int(os.getenv('GUILD_ID')))

        if guild is None:
            print("Guild not found! Check the ID.")
            return

        # 1. NEW: Use setup_channels instead of reset_channels
        channels = await setup_channels(guild)
        
        for channel in channels:
            if channel.name == "test-bot":
                found_role_msg = False
                # Search the last 10 messages for our own role message
                async for message in channel.history(limit=10):
                    if message.author == self.user and "React with the following emojis" in message.content:
                        self.reaction_message = message
                        found_role_msg = True
                        print("Found existing Role Message. Linking to it silently.")
                        break
                
                # Only if we NEVER found it, do we purge and send a new one (Ping happens here only once)
                if not found_role_msg:
                    await channel.purge(limit=10)
                    self.reaction_message = await roles_message(channel)

            # --- FIX FOR CODE CHANNEL ---
            elif channel.name == "code":
                found_welcome = False
                # Search for our Welcome message
                async for message in channel.history(limit=10):
                    if message.author == self.user and message.content.startswith("Welcome!"):
                        self.code_message = message
                        found_welcome = True
                        print("Found existing Code Message. Linking to it silently.")
                        break
                
                # Only if missing, send new one
                if not found_welcome:
                    # Do NOT purge here if you want to keep user attempts, 
                    # but if you want it clean:
                    await channel.purge(limit=5) 
                    self.code_message = await general_message(channel, "Welcome! Please enter the access code provided to you in order to explore the rest of the server.")
            elif channel.name == "randoné":
                role_base = discord.utils.get(guild.roles, name="randonneur")
                if role_base:
                    await channel.set_permissions(role_base, read_messages=True, send_messages=True)
        
        # 2. Permission Setup
        restricted_channels = [
            c.strip().lower()
            for c in os.getenv("RESTRICTED_CHANNELS", "").split(",")
            if c.strip()
        ]

        role_base = discord.utils.get(guild.roles, name="padawan")
        role_every = discord.utils.get(guild.roles, name="@everyone")
        role_randonneur = discord.utils.get(guild.roles, name="randonneur")

        # Set permissions for channels
        for channel in guild.channels:
            if channel.name not in restricted_channels:
                # Allow padawan role to read and send messages
                if role_base:
                    await channel.set_permissions(role_base, read_messages=True, send_messages=True)

                # Deny read for @everyone but allow write
                if role_every:
                    await channel.set_permissions(role_every, read_messages=False, send_messages=True)

            # Explicitly grant read/write for randonneur in randoné channel
            elif channel.name == "randoné":
                if role_randonneur:
                    await channel.set_permissions(role_randonneur, read_messages=True, send_messages=True)

        # 3. FIX: Heartbeat Glitching on Reconnect
        # Only start the task if it doesn't exist or if the previous one finished/crashed
        if self.heartbeat_task is None or self.heartbeat_task.done():
            print("Starting Heartbeat Task...")
            self.heartbeat_task = asyncio.create_task(monitor_heartbeat_logs(self))
        else:
            print("Heartbeat Task already running.")

    async def on_reaction_add(self, reaction, user):
        if user == self.user:
            return
        
        # Safety check: ensure reaction_message exists before checking ID
        if self.reaction_message and reaction.message.id == self.reaction_message.id:
            await handle_reaction_add(user, reaction)
    

    async def on_reaction_remove(self, reaction, user):
        if user == self.user:
            return
        
        # Safety check: ensure reaction_message exists before checking ID
        if self.reaction_message and reaction.message.id == self.reaction_message.id:
            await handle_reaction_remove(user, reaction)


    async def on_member_join(self, member):
        guild = member.guild
        role_goulag = discord.utils.get(guild.roles, name="gulag")
        if role_goulag:
            await member.add_roles(role_goulag)     


    async def on_message(self, message):
        # Do not answer itself
        if message.author == self.user:
            return

        # Reaction to different input in the channel test-bot
        if message.channel.name == "test-bot":
            if message.content.startswith('$gulag'):
                await gulag_command(message)
            
            if message.content.startswith('$padawan'):
                await padawan_command(message)

            if message.content.startswith('$ping'):
                await message.channel.send(f'Hello {message.author.mention}!')
            
            if message.content.startswith('$code'):
                await code_command(message)


        # Check for the password in the code channel
        # Added safety check: ensure self.code_message is not None
        if self.code_message and message.channel.id == self.code_message.channel.id:
            if message.author == self.user:
                return

            code_info = code_verification(message.content)
            if code_info:
                role = code_info["role"]
                await give_role(message.author, role)
                await remove_role(message.author, "gulag")
                
            await message.delete()
        
                    
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
intents.guilds = True

client = MyClient(intents=intents)


client.run(os.getenv('DISCORD_TOKEN'))