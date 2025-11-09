#https://discordpy.readthedocs.io/en/stable/faq.html#how-can-i-add-a-reaction-to-a-message
#https://discordpy.readthedocs.io/en/stable/api.html#discord.Guild.get_channel
#https://discordpy.readthedocs.io/en/stable/api.html#discord.utils.find

CATEGORIES = ("NMMNG", "The Hero's Journey")

import sys
import asyncio
import discord
import datetime

import server_keys

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def Print(msg):
    msg = '{} {}'.format(datetime.datetime.now(), msg)
    print(msg)

def GetNextChannels(channel):
    if channel.category is None or channel.category.name not in CATEGORIES:
        return []

    # Get all channels in this category
    channels = channel.category.channels
    if channel not in channels:
        Print('Channel not found: {}'.format(channel))
        
    start = channels.index(channel) + 1

    # Add find the next channels (including optionals)
    result = []
    for curChannel in channels[start:]:
        result.append(curChannel)
        if 'optional' not in curChannel.name:
            break

    return result

@client.event
async def on_ready():
    Print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    # message.guild.members[0].roles[2].permissions.manage_roles
    if message.author == client.user:
        return

    # If the member is messaging in the 5th BFA then assign him the Brother role
    if message.channel.name == 'bfa-5':
        # Get the brother role
        roles = [x for x in message.guild.roles if x.name == 'Brother']
        if roles:
            role = roles[0]

            if role not in message.author.roles:
                Print('Giving {} the role {}'.format(message.author, role.name))
                await message.author.add_roles(role)

    # Get the next channels
    channels = GetNextChannels(message.channel)

    changed = False
    for channel in channels:
        # Skip if already in channel
        if channel.permissions_for(message.author).read_messages:
            continue

        # Get user's permissions and add access
        perms = channel.overwrites_for(message.author)
        perms.read_messages = True

        # Set persmissions on the channel
        msg = "Giving {} access to {}"
        msg = msg.format(message.author, channel.name)
        Print(msg)
        await channel.set_permissions(message.author, overwrite=perms)
        changed = True

    if changed:
        await message.add_reaction('\U0001f440')
        msg = "Finished giving {} access to new channels"
        msg = msg.format(message.author)
        Print(msg)

def Main():
    if '-test' in sys.argv:
        k = server_keys.test
    else:
        k = server_keys.prod
    client.run(k)

if __name__ == '__main__':
    Main()
