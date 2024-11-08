import os
from logging import INFO
from logging.handlers import TimedRotatingFileHandler
# lib
import discord
import sentry_sdk
from discord import Client, Message, DMChannel
# local
from . import VERSION
from .settings import Settings
from .agent import pass_message_to_agent


if Settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=Settings.SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = Client(intents=intents)

# Define a log handler
handler = TimedRotatingFileHandler(
    'logs/discord.log',
    when='d',
    interval=1,
    backupCount=2,
)


@client.event
async def on_ready():
    print('Ready to go o7')
    activity = discord.Game(f'Ping me to ask questions! (v{VERSION})')
    await client.change_presence(status=discord.Status.online, activity=activity)


@client.event
async def on_message(message: Message):
    handle_message = (
        isinstance(message.channel, DMChannel) or 
        (client.user.mentioned_in(message) and not message.mention_everyone)
    )
    if handle_message and message.author.id != client.user.id:
        thread_id = message.author.id
        username = message.author.display_name
        content = message.content.replace(client.user.mention, client.user.name)
        response = pass_message_to_agent(thread_id, username, content)

        if not response:
            await message.reply('The request was sent but the Agent did not return any response', )
        else:
            await message.reply(response)

client.run(Settings.DISCORD_TOKEN, log_handler=handler, log_level=INFO, root_logger=True)
