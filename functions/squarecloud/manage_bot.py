import squarecloud as square
import os
from dotenv import load_dotenv

load_dotenv()
client = square.Client(api_key=os.getenv("SQUARECLOUD_TOKEN"))

async def start_bot(bot_id: str):
    await client.start_app(bot_id)

async def stop_bot(bot_id: str):
    await client.stop_app(bot_id)

async def restart_bot(bot_id: str):
    await client.restart_app(bot_id)

async def delete_bot(bot_id: str):
    await client.delete_app(bot_id)