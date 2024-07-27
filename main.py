import interactions
from interactions import Client, Intents, listen
from interactions.ext import prefixed_commands
from interactions.api.events import MessageCreate

bot = Client(token="ODUyOTMwMzAwMTIzMTUyMzk0.GEAAuR.7z2c0Kbs073jIK0zblLEvCYEvOTR1uGjJO9AsE",
intents=Intents.new(default=True, guild_messages=True, message_content=True))

prefixed_commands.setup(bot)

@listen(MessageCreate)
async def on_message_create(event : MessageCreate):
    print(event.message.content)

bot.start()