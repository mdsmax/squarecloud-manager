import squarecloud as square
import os
from dotenv import load_dotenv

load_dotenv()
client = square.Client(api_key=os.getenv("SQUARECLOUD_TOKEN"))

async def upload_bot(bot_path: str):
    file = square.File(f"{bot_path}")
    app = await client.upload_app(file=file)
    return app.id