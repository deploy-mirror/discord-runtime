import discord

async def give_role(user, role_name):
    guild = user.guild
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        return
    await user.add_roles(role)


async def remove_role(user, role_name):
    guild = user.guild
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        return
    await user.remove_roles(role)

def check_role(guild, role):
    return discord.utils.get(guild.roles, name=role)