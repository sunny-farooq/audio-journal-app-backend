
from tortoise import Tortoise, run_async
import os 

async def init():
    await Tortoise.init(
        db_url=os.getenv("SUPABASE_DB"),
        modules={'models': ['models.user', 'models.audio',"models.admin"]}
    )
    await Tortoise.generate_schemas(safe=True)


