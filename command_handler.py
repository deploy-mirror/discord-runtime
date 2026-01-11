import discord
import os

from role_handler import remove_role, give_role
from code_handler import add_code, remove_code_by_command, show_codes, remove_all_codes
from message_handler import general_message

#message is the obj
async def gulag_command(message):
    username = message.content[len("$gulag "):].strip()

    if username:
        member = message.guild.get_member_named(username)
        if member:
            for role in member.roles:
                if role.name != "@everyone":
                    await remove_role(member, role.name)
            await give_role(member, "gulag")
            await message.channel.send(f"user{member.mention} in gulag")
        else:
            await message.channel.send("user not found")
    else:
        await message.channel.send("Please specify a user. ($gulag username)")


#message is the obj
async def padawan_command(message):
    username = message.content[len("$padawan "):].strip()

    if username:
        member = message.guild.get_member_named(username)
        if member:
            for role in member.roles:
                if role.name != "@everyone":
                    await remove_role(member, role.name)
            await give_role(member, "padawan")
            await message.channel.send(f"user{member.mention} is a padawan")
        else:
            await message.channel.send("user not found")
    else:
        await message.channel.send("Please specify a user. ($padawan username)")

#message is the obj
async def code_command(message):
    if message.author.id == int(os.getenv('AUTHOR_ID', 0)):
        list_command = message.content.split()
        if len(list_command) >= 3 and list_command[1] == "add":
            await add_code(message)

        elif len(list_command) == 3 and list_command[1] == "remove":
            if list_command[2] == "all":
                remove_all_codes()
            remove_code_by_command(message)
            await general_message(message.channel,"done")
        
        elif len(list_command) == 2 and list_command[1] == "show":
            await show_codes(message)
        
    
        #send message for help
        elif len(list_command) == 2 and list_command[1] == "help":
            await general_message(message.channel, "to add: $code add [role] [1 (for 1 time use only)] ex: $code role")
            await general_message(message.channel, "to remove: $code remove [code]")
            await general_message(message.channel, "to show codes: $code show")
        else:
            await general_message(message.channel, "missing arguments $code [add or remove] type $code help")