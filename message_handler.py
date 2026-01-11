import discord

async def general_message(channel, message):
    message = await channel.send(message)
    return message

#channel is the obj
async def roles_message(channel):
    message_content = """
    **React with the following emojis to receive your role:**

    🥾 - **Randonneur**  
    🐉 - **Dofus**  
    🎯 - **Tarkov**  
    ⛏️ - **Minecraft**  

    *Click the emoji corresponding to the role you want, and it will be assigned to you!* 🎉
    """
    message = await channel.send(message_content)
    await message.add_reaction("🥾")
    await message.add_reaction("🐉")
    await message.add_reaction("🎯")
    await message.add_reaction("⛏️")
    
    return message

async def setup_channels(guild):
    """
    Checks if required channels exist. 
    Creates them if missing, but DOES NOT delete existing ones.
    """
    channels_names = ["code", "test-bot", "heartbeat"]
    # Create a dictionary for faster lookups: {"channel_name": channel_object}
    existing_channels = {channel.name: channel for channel in guild.channels}
    final_channels = []

    for name in channels_names:
        if name in existing_channels:
            # Channel already exists, append the existing object
            final_channels.append(existing_channels[name])
        else:
            # Only create it if it's missing
            print(f"Creating missing channel: {name}")
            new_channel = await guild.create_text_channel(name=name)
            final_channels.append(new_channel)
        
    return final_channels
    