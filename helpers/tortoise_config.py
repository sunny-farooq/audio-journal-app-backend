from tortoise import Tortoise
import os 
from dotenv import load_dotenv
load_dotenv()

async def init():
    await Tortoise.init(
        db_url=os.getenv("SUPABASE_DB"),
        modules={'models': ['models.user', 'models.audio',"models.admin"]}
    )
    await Tortoise.generate_schemas(safe=True)


