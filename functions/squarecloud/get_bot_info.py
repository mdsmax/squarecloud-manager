import squarecloud as square
import os
from dotenv import load_dotenv

load_dotenv()
client = square.Client(api_key=os.getenv("SQUARECLOUD_TOKEN"))

async def get_bot_info(bot_id: str):
    app_status = await client.app_status(bot_id)
    return app_status