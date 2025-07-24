import squarecloud as square
import os
from dotenv import load_dotenv

load_dotenv()
client = square.Client(api_key=os.getenv("SQUARECLOUD_TOKEN"))

async def upload_bot(bot_id: str):
    file = square.File(f"{bot_id}")
    app = await client.upload_app(file=file)
    return app.id