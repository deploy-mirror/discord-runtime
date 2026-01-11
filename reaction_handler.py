import discord
from role_handler import remove_role, give_role

#user and reaction is the obj
async def handle_reaction_add(user, reaction):

    #check the emoji
    if reaction.emoji  == "\U0001f97e":
        print(f"role randonneur added to {user}")
        await give_role(user, "randonneur")

    elif reaction.emoji  == "\U0001f409":
        print(f"role dofus added to {user}")
        await give_role(user, "dofus")
    
    elif reaction.emoji  == "\U0001f3af":
        print(f"role tarkov added to {user}")
        await give_role(user, "tarkov")

    elif reaction.emoji  == "\u26cf\ufe0f":
        print(f"role minecraft added to {user}")
        await give_role(user, "minecraft")

    else:
        await reaction.remove(user)

#user and reaction is the obj
async def handle_reaction_remove(user, reaction):

    # Check the emoji
    if reaction.emoji == "🥾":
        print(f'role randonneur removed from {user}!')
        await remove_role(user, "randonneur")

    elif reaction.emoji == "🐉":
        print(f'role dofus removed from {user}!')
        await remove_role(user, "dofus")
    
    elif reaction.emoji == "🎯":
        print(f'role tarkov removed from {user}!')
        await remove_role(user, "tarkov")

    elif reaction.emoji == "⛏️":
        print(f'role minecraft removed from {user}!')
        await remove_role(user, "minecraft")

    else:
        return