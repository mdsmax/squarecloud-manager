import squarecloud
import os

async def get_account_informations():
    client = squarecloud.Client(os.getenv("SQUARECLOUD_TOKEN"))
    
    account = await client.user()
    plan = account.plan
    apps = await client.all_apps()

    return {
        "plan": {
            "name": plan['name'],
            "memory": plan['memory'],
            "duration": plan['duration'],
        },
        "apps": len(apps),
        "user_id": account.id,
        "email": account.email,
    }