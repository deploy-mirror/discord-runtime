import asyncio
import json
import os
import discord
import hashlib
from datetime import datetime

HEARTBEAT_LOGS_DIR = os.getenv('HEARTBEAT_DIR')
HEARTBEAT_CHANNEL_NAME = "heartbeat"
VALID_CODE = os.getenv('HEARTBEAT_CODE')
ALERT_USER_ID = os.getenv('AUTHOR_ID')
hosts_list = [
            c.strip().lower()
            for c in os.getenv("HOSTS_LIST", "").split(",")
            if c.strip()
        ]

def get_file_hash(data):
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

async def monitor_heartbeat_logs(client):
    await client.wait_until_ready()

    # We do not fetch the channel here anymore. We do it inside the loop 
    # to ensure the object is always fresh if the bot reconnects.
    
    previous_hashes = {}
    unchanged_counts = {}
    online_status = {}
    message = None

    print("Heartbeat Monitor: Started.")

    while not client.is_closed():
        # 1. Refresh channel reference (handles reconnects better)
        channel = discord.utils.get(client.get_all_channels(), name=HEARTBEAT_CHANNEL_NAME)
        
        if not channel:
            print(f"Heartbeat Monitor: Channel '{HEARTBEAT_CHANNEL_NAME}' not found. Retrying in 10s...")
            await asyncio.sleep(10)
            continue

        try:
            # Fetch the user for DM alerts (only needs to be done once, but safe to try here)
            user = await client.fetch_user(ALERT_USER_ID)
        except Exception as e:
            print(f"Failed to fetch alert user: {e}")
            user = None

        lines = []

        # 2. Build the Status Message
        if os.path.isdir(HEARTBEAT_LOGS_DIR):
            for filename in sorted(os.listdir(HEARTBEAT_LOGS_DIR)):
                path = os.path.join(HEARTBEAT_LOGS_DIR, filename)
                try:
                    with open(path, "r") as file:
                        data = json.load(file)

                    if data.get("code") != VALID_CODE:
                        raise ValueError("Invalid code")

                    host = data.get("host", "Unknown")
                    received_at_raw = data.get("receivedAT", "")
                    received_at = received_at_raw.split(".")[0].replace("T", " ")

                    data_hash = get_file_hash(data)

                    # Check if file has changed since last check
                    if filename in previous_hashes and previous_hashes[filename] == data_hash:
                        unchanged_counts[filename] = unchanged_counts.get(filename, 1) + 1
                    else:
                        unchanged_counts[filename] = 0

                    previous_hashes[filename] = data_hash

                    # Determine status (Offline if unchanged for 2+ cycles)
                    is_online = unchanged_counts[filename] < 2
                    status = "🟢" if is_online else "🔴"
                    lines.append(f"{status} **{host}** — Last seen: `{received_at}`")

                    # 3. Alert Logic (Send DM)
                    if user and host in online_status:
                        was_online = online_status[host]

                        # Went Offline
                        if was_online and not is_online and host.lower() not in hosts_list:
                            try:
                                await user.send(f"⚠️ **{host}** just went offline!")
                            except Exception as alert_error:
                                print(f"Failed to send offline DM: {alert_error}")

                        # Came Online (Only for PKI as requested)
                        elif not was_online and is_online and host.lower() == "pki":
                            try:
                                await user.send(f"✅ **{host}** is back online!")
                            except Exception as alert_error:
                                print(f"Failed to send online DM for pki: {alert_error}")

                    # Update current status
                    online_status[host] = is_online

                except Exception as e:
                    lines.append(f"❌ **Unknown** — Could not parse `{filename}`: {str(e)}")

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"\n⏱️ **Last update:** `{now}`")
            content = "\n".join(lines)

        else:
            content = "❌ Log directory not found"

        if not content:
            content = "*No heartbeat data.*"

        # 4. Smart Message Handling (The Fix)
        try:
            # If we lost the message reference (e.g. after restart), try to find it in history
            if message is None:
                async for msg in channel.history(limit=10):
                    if msg.author == client.user:
                        message = msg
                        print(f"Heartbeat Monitor: Found existing message {message.id}, resuming edits.")
                        break
            
            # If still None, send a new one. If found, edit it.
            if message is None:
                message = await channel.send(content)
            else:
                await message.edit(content=content)

        except discord.NotFound:
            # Message was deleted manually, force a new one next loop
            print("Heartbeat message deleted. Creating new one next cycle.")
            message = None
        except Exception as e:
            print(f"Failed to send/edit heartbeat message: {e}")
            # Reset message to None so we try to find/send a fresh one next time
            message = None

        await asyncio.sleep(60)
