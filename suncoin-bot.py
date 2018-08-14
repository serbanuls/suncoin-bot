import os
import time
import datetime
import random
import asyncio
import aiohttp
import json
import discord
import logging
import traceback

from utils.dataIO import dataIO
from random import randint
from random import choice
from discord.ext import commands
from discord.ext.commands import Bot
from datetime import datetime, timedelta
from tinydb import TinyDB, Query
from tinydb_serialization import Serializer, SerializationMiddleware

#Enable Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

# Create DiscordHandler and StreamHandler
discord_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
asyncio_handler = logging.FileHandler(filename='asyncio.log', encoding='utf-8', mode='w')
stream_handler = logging.StreamHandler()

# Add log level to handlers
discord_handler.setLevel(logging.WARNING)
asyncio_handler.setLevel(logging.DEBUG)
stream_handler.setLevel(logging.DEBUG)

# Add format to handlers
FORMAT = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
discord_handler.setFormatter(FORMAT)
asyncio_handler.setFormatter(FORMAT)
stream_handler.setFormatter(FORMAT)

# Add the handlers to the Logger
logger.addHandler(discord_handler)
logger.addHandler(asyncio_handler)
logger.addHandler(stream_handler)

logger.debug("Logger created")

class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime  # The class this serializer handles

    def encode(self, obj):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')

    def decode(self, s):
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')

#Create bot instance
BOT_PREFIX = ("?", "!")
TOKEN = "NDY0MDEwMzc4NDMxNjkyODAw.Dh4vRw.EVVLMjl5gcgHF7J4HHsV_WPDUSE"  # Get at discordapp.com/developers/applications/me

client = Bot(command_prefix=BOT_PREFIX)
serialization = SerializationMiddleware()
serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
client.remove_command("help")
updating = False

@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name="with humans"))
    print("Logged in as " + client.user.name)

@client.event
async def on_message(message):
    if(not updating):
        db = TinyDB('data/activity.json', storage=serialization)
        d = datetime.now()
        if((message.author != client.user) and not message.content.startswith('!')):
            message_type = "short"
            if '@' in message.content:
                message_type = "mention"
            elif len(message.content):
                message_type = "long"
            db.insert({'server':message.server.id,'channel':message.channel.id,'author':message.author.id,'message':message.id, 'date':datetime(d.year, d.month, d.day, d.hour, d.minute, d.second),'type':message_type})
        db.close()

    if (message.channel.name == "sun-bot"):
        await client.process_commands(message)

@client.event
async def on_error(event, *args, **kwargs):
    message = args[0] #Gets the message object
    logging.warning(traceback.format_exc()) #logs the error

@client.command()
async def help():
    url = 'https://sun.overemo.com/api/getblockcount'
    embed = discord.Embed(title="SunCoin Network ($SUN)", description="SUN Bot Help", type="rich", color=0xfdb813)
    help_text="**!profile** - Display your $SUN profile.\n**!status** - Returns current user status.\n**!rank** - Displays user rank according to your activity in server.\n**!exchanges** - Gives a list of exchanges where you can buy/sell $SUN\n**!explorer** - Gives you an explorer to view the $SUN blockchain. \n**!block** - Shows the current block height for $SUN.\n**!ann** - Gives you a link to the SunCoin Network announcement thread.\n**!website** - Gives you a link to the SunCoin Network website.\n**!guides** - Links to guides to follow when setting up a masternode.\n**!exchanges** - Gives you links where you can buy/sell $SUN.\n**!sun** - Returns current $SUN price. \n**!btc** - Returns current $BTC price."
    embed.add_field(name="Commands", value=help_text)
    await client.say(embed=embed)

@client.command()
async def btc():
    url = 'https://api.coindesk.com/v1/bpi/currentprice.json'
    async with aiohttp.ClientSession() as session:  # Async HTTP request
        raw_response = await session.get(url)
        response = await raw_response.text()
        response = json.loads(response)
        #{"time":{"updated":"Jul 5, 2018 08:59:00 UTC","updatedISO":"2018-07-05T08:59:00+00:00","updateduk":"Jul 5, 2018 at 09:59 BST"},"disclaimer":"This data was produced from the CoinDesk Bitcoin Price Index (USD). Non-USD currency data converted using hourly conversion rate from openexchangerates.org","bpi":{"USD":{"code":"USD","rate":"6,617.6325","description":"United States Dollar","rate_float":6617.6325},"BTC":{"code":"BTC","rate":"1.0000","description":"Bitcoin","rate_float":1}}}
        embed = discord.Embed(title="$BTC", description="Bitcoin current price", type="rich", color=0xfdb813)

        embed.add_field(name="Price (USD)", value="```"+response['bpi']['USD']['rate']+"$```", inline=False)
        embed.add_field(name="Price (EUR)", value="```"+response['bpi']['EUR']['rate']+"€```", inline=False)

        # Shows the number of servers the bot is member of.
        #embed.add_field(name="Server count", value=f"{len(client.guilds)}")
        # give users a link to invite thsi bot to their server
        await client.say(embed=embed)
        #await client.say("$BTC price is: " + response['bpi']['USD']['rate']+"$")

@client.command()
async def sun():
    url = 'https://graviex.net:443//api/v2/tickers/sunbtc.json'
    async with aiohttp.ClientSession() as session:  # Async HTTP request
        raw_response = await session.get(url)
        response = await raw_response.text()
        response = json.loads(response)
        #{"at":1398410899, "ticker":{"buy":"3000.0","sell":"3100.0","low":"3000.0","high":"3000.0","last":"3000.0","vol":"0.11"}}
        embed = discord.Embed(title="SUN/BTC", description="SunCoin price", type="rich", color=0xfdb813)

        # give info about you here
        embed.add_field(name="Last", value=response['ticker']['last'], inline=True)
        embed.add_field(name="Volume", value=response['ticker']['vol'], inline=True)
        embed.add_field(name="Graviex", value="[SUN/BTC](https://graviex.net/markets/sunbtc?markets=all&column=name&order=asc&unit=volume&pinned=false)", inline=True)

        embed.add_field(name="Buy", value="```"+response['ticker']['buy']+"```", inline=True)
        embed.add_field(name="Sell", value="```"+response['ticker']['sell']+"```", inline=True)

        # Shows the number of servers the bot is member of.
        #embed.add_field(name="Server count", value=f"{len(client.guilds)}")
        # give users a link to invite thsi bot to their server
        await client.say(embed=embed)
        #await client.say("$SUN price is: " + response['ticker']['buy']+" BTC")

@client.command()
async def block():
    url = 'https://sun.overemo.com/api/getblockcount'
    async with aiohttp.ClientSession() as session:  # Async HTTP request
        raw_response = await session.get(url)
        response_raw = await raw_response.text()
        response = json.loads(response_raw)
        #{"at":1398410899, "ticker":{"buy":"3000.0","sell":"3100.0","low":"3000.0","high":"3000.0","last":"3000.0","vol":"0.11"}}
        embed = discord.Embed(title="SunCoin Network ($SUN)", description="Current block count", type="rich", color=0xfdb813)
        embed.add_field(name="Block", value=response_raw, inline=True)

        # Shows the number of servers the bot is member of.
        #embed.add_field(name="Server count", value=f"{len(client.guilds)}")
        # give users a link to invite thsi bot to their server
        await client.say(embed=embed)
        #await client.say("$SUN price is: " + response['ticker']['buy']+" BTC")

@client.command()
async def explorer():
    url = 'https://sun.overemo.com'
    embed = discord.Embed(title="SunCoin Network ($SUN)", description="Network explorer for $SUN.\n You can do the following and more!\n - See current info about the coin such as difficulty, coin supply and blockchain height \n- Search for transactions using criteria such as block height, tx hash (TXID), blockhash or wallet addresses\n- See the latest transactions on the blockchain\n- See the list of top 100 addresses\n- Get access to usefull API calls", type="rich", color=0xfdb813)
    embed.add_field(name="Explorer", value=url, inline=True)

    await client.say(embed=embed)

@client.command()
async def website():
    url = 'https://suncoin.network.com'
    embed = discord.Embed(title="SunCoin Network ($SUN)", description="Official Website", type="rich", color=0xfdb813)
    embed.add_field(name="Website URL", value=url, inline=True)

    await client.say(embed=embed)

@client.command()
async def exchanges():
    url = 'https://graviex.net/markets/sunbtc'
    embed = discord.Embed(title="SunCoin Network ($SUN)", description="List of current exchanges", type="rich", color=0xfdb813)
    embed.add_field(name="Graviex", value=url, inline=True)

    await client.say(embed=embed)

@client.command()
async def ann():
    url = 'https://bitcointalk.org/index.php?topic=4500891'
    embed = discord.Embed(title="ANN Thread", description="Link to Announcement", type="rich", color=0xfdb813)

    # give info about you here
    embed.add_field(name="Bitcointalk", value=url, inline=True)

    await client.say(embed=embed)

@client.command()
async def guides():
    embed = discord.Embed(title="SunCoin Network ($SUN)", description="Links to Masternode guides", type="rich", color=0xfdb813)
    embed.add_field(name="Guides", value="Guide for MacOS: https://goo.gl/f1ZuDB.\nGuide for MacOS with VPS: https://goo.gl/w6qBEX.\nGuide for Windows with VPS: https://goo.gl/FpxeYv.\n", inline=True)

    await client.say(embed=embed)

@client.command(pass_context=True)
async def joined(ctx):
    """Says when a member joined."""
    author = ctx.message.author
    #print(ctx)
    #print(ctx.message)
    #print(ctx.message.author)
    await client.say('{0.name} joined in {0.joined_at}'.format(author))

@client.command(pass_context=True)
async def status(ctx):
    """Says when a member joined."""
    author = ctx.message.author
    await client.say('{0.name} status is {0.status}'.format(author))

@client.command(pass_context=True)
async def roles(ctx):
    """Says when a member joined."""
    author = ctx.message.author
    await client.say('{0.name} status is {0.status}'.format(author))

@client.command(pass_context=True, no_pm=True)
async def profile(ctx, *, user: discord.Member=None):
    """Shows users's informations"""
    author = ctx.message.author
    server = ctx.message.server

    if not user:
        user = author

    roles = [x.name for x in user.roles if x.name != "@everyone"]

    joined_at = author.joined_at
    since_created = (ctx.message.timestamp - user.created_at).days
    since_joined = (ctx.message.timestamp - joined_at).days
    user_joined = joined_at.strftime("%d %b %Y %H:%M")
    user_created = user.created_at.strftime("%d %b %Y %H:%M")
    member_number = sorted(server.members,
                           key=lambda m: m.joined_at).index(user) + 1

    created_on = "{}\n({} days ago)".format(user_created, since_created)
    joined_on = "{}\n({} days ago)".format(user_joined, since_joined)

    game = "Chilling in {} status".format(user.status)

    if user.game is None:
        pass
    elif user.game.url is None:
        game = "Playing {}".format(user.game)
    else:
        game = "Streaming: [{}]({})".format(user.game, user.game.url)

    if roles:
        roles = sorted(roles, key=[x.name for x in server.role_hierarchy
                                   if x.name != "@everyone"].index)
        roles = ", ".join(roles)
    else:
        roles = "None"

    data = discord.Embed(description=game, colour=user.colour)
    data.add_field(name="Joined Discord on", value=created_on)
    data.add_field(name="Joined this server on", value=joined_on)
    data.add_field(name="Roles", value=roles, inline=False)
    data.set_footer(text="Member #{} | User ID:{}"
                         "".format(member_number, user.id))

    name = str(user)
    name = " ~ ".join((name, user.nick)) if user.nick else name

    if user.avatar_url:
        data.set_author(name=name, url=user.avatar_url)
        data.set_thumbnail(url=user.avatar_url)
    else:
        data.set_author(name=name)

    try:
        await client.say(embed=data)
    except discord.HTTPException:
        await client.say("I need the `Embed links` permission "
                               "to send this")

@client.command(pass_context=True, no_pm=True)
async def server(ctx):
        """Shows server's informations"""
        server = ctx.message.server
        online = len([m.status for m in server.members
                      if m.status != discord.Status.offline])
        total_users = len(server.members)
        text_channels = len([x for x in server.channels
                             if x.type == discord.ChannelType.text])
        voice_channels = len([x for x in server.channels
                             if x.type == discord.ChannelType.voice])
        passed = (ctx.message.timestamp - server.created_at).days
        created_at = ("Since {}. That's over {} days ago!"
                      "".format(server.created_at.strftime("%d %b %Y %H:%M"),
                                passed))

        colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)

        data = discord.Embed(
            description=created_at,
            colour=discord.Colour(value=colour))
        data.add_field(name="Region", value=str(server.region))
        data.add_field(name="Users", value="{}/{}".format(online, total_users))
        data.add_field(name="Text Channels", value=text_channels)
        data.add_field(name="Voice Channels", value=voice_channels)
        data.add_field(name="Roles", value=len(server.roles))
        data.add_field(name="Owner", value=str(server.owner))
        data.set_footer(text="Server ID: " + server.id)

        if server.icon_url:
            data.set_author(name=server.name, url=server.icon_url)
            data.set_thumbnail(url=server.icon_url)
        else:
            data.set_author(name=server.name)

        try:
            await client.say(embed=data)
        except discord.HTTPException:
            await client.say("I need the `Embed links` permission "
                               "to send this")

@client.command(pass_context=True, no_pm=True)
async def rank(ctx, *, user: discord.Member=None):
        """Shows user rank"""

        author = ctx.message.author
        server = ctx.message.server

        if not user:
            user = author

        logger.info('!rank %s', user.name)
        #print("!rank "+user.name)

        online = len([m.status for m in server.members
                      if m.status != discord.Status.offline])
        total_users = len(server.members)
        passed = (ctx.message.timestamp - server.created_at).days
        member_number = sorted(server.members,
                               key=lambda m: m.joined_at).index(user) + 1

        db_ranking = TinyDB('data/ranking-'+server.id+'.json', sort_keys=True,  storage=serialization)
        rankings = db_ranking.all()
        #Rank = Query()
        #rankings = db_ranking.search(Rank.name != "")
        #print(len(rankings))
        sorted_rankings = sorted(rankings, key=lambda x : float(x['points']), reverse=True)

        Ranking = Query()
        if (db_ranking.contains(Ranking.author == user.id)):
            rank = db_ranking.get(Ranking.author == user.id)
            #print(rank)
            pos = sorted_rankings.index(rank) + 1
            #print(pos)
            level = get_level(user.joined_at)
            data = discord.Embed(title="Ranking", description=user.name, colour=user.colour)
            data.add_field(name="$SUN points", value=rank['points'])
            data.add_field(name="Total count", value=rank['count'])
            data.add_field(name="Rank", value=str(pos)+"/"+str(total_users))
            data.add_field(name="Level", value=str(level))
            data.set_footer(text="Member #{} | User ID:{}"
                                 "".format(member_number, user.id))
            db_ranking.close()

            await client.say(embed=data)
        else:
            db_ranking.close()

            await client.say("Hey, you still have not been ranked")
        #update_messages(server)

async def update_messages(server):
    #print ("Channels: "+len(server.channels))
    for channel in server.channels:
        if(channel.type == discord.ChannelType.text and channel.is_private == False):
            #print (channel.id)
            logger.info('update messages %s', channel.id)
            counter = 0
            for message in client.logs_from(channel, limit=500):
                counter += 1

            """logs = yield from client.logs_from(channel)
            count = 0;
            for message in logs:
                count += 1
                if message.author == client.user:
                    yield from client.edit_message(message, 'goodbye')"""

            #print ("channel: "+channel.id + "["+count+"]")

def get_key(d):
    print(d['points'])
    return d['points']

def increment(field):
    def transform(el):
        el[field] += 1
    return transform

def add(field, value):
    def transform(el):
        el[field] += value
    return transform

def get_level(result):
    # 0-1 days *1
    # 1-7 days *0.75
    # 7-14 days *0.5
    # 14-30 days *0.25
    # >30 days *0.1
    d = datetime.now()
    range_1 = d - timedelta(days=1)
    range_2 = d - timedelta(days=15)
    range_3 = d - timedelta(days=30)
    range_4 = d - timedelta(days=60)
    range_5 = d - timedelta(days=120)

    if (result > range_1):
        return 0
    elif (result < range_1 and result > range_2):
        return 1
    elif (result < range_2 and result > range_3):
        return 2
    elif (result < range_3 and result > range_4):
        return 3
    elif (result < range_3 and result > range_4):
        return 4
    else:
        return 5

def get_points(message_date, message_type):
    # 0-1 days *1
    # 1-7 days *0.75
    # 7-14 days *0.5
    # 14-30 days *0.25
    # >30 days *0.1
    d = datetime.now()
    range_1 = d - timedelta(days=1)
    range_2 = d - timedelta(days=7)
    range_3 = d - timedelta(days=14)
    range_4 = d - timedelta(days=30)
    type_rate = get_type_rate(message_type)
    #print(type_rate)
    if (message_date > range_1):
        return 1*type_rate
    elif (message_date < range_1 and message_date > range_2):
        return 0.75*type_rate
    elif (message_date < range_2 and message_date > range_3):
        return 0.5*type_rate
    elif (message_date < range_3 and message_date > range_4):
        return 0.25*type_rate
    else:
        return 0.1*type_rate

def get_type_rate(message_type):
    if (message_type == '' or message_type == 'short'):
        return 0.25
    elif message_type == 'long':
        return 0.5
    elif message_type == 'mention':
        return 1

async def update_ranking():
    await client.wait_until_ready()
    while not client.is_closed:
        #Loop trough servers
        for server in client.servers:
            updating = True
            #print("update_ranking: "+server.id)
            logger.info('Updating ranking %s', server.id)
            #print(server.member_count)
            db_activity = TinyDB('data/activity.json', storage=serialization)
            Activity = Query()
            result = db_activity.search(Activity.server == server.id)
            #Fill ranking table with authors message count
            db_ranking = TinyDB('data/ranking-'+server.id+'.json', storage=serialization)
            db_ranking.purge()
            for r in result:
                Ranking = Query()
                if (db_ranking.contains(Ranking.author == r['author'])):
                    message_type = r['type']
                    db_ranking.update(increment('count'), Ranking.author == r['author'])
                    db_ranking.update(add('points', get_points(r['date'], message_type)), Ranking.author == r['author'])
                    db_ranking.update({'last': r['date']}, Ranking.author == r['author'])
                else:
                    message_type = r['type']
                    db_ranking.insert({'author':r['author'],'count':1, 'last':r['date'], 'points':get_points(r['date'], message_type)})

            logger.info('Updated ranking %s for %s members', server.id, len(db_ranking))
            db_ranking.close()
            db_activity.close()
            updating = False
        #Wait for 300 seconds to avoid problems in
        await asyncio.sleep(300)

async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        #print("Current servers:")
        for server in client.servers:
            logger.info(server.name)
            #print(server.name)
        await asyncio.sleep(600)

client.loop.create_task(update_ranking())
client.loop.create_task(list_servers())

client.run(TOKEN)
