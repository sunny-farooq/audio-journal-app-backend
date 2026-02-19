from dotenv import load_dotenv
from fastapi import FastAPI
from controllers import user_controller
from controllers import audio_controller
from controllers import transcript_summary_controller
from controllers import admin_controller
from helpers.tortoise_config import init
import os
from models.user import User

load_dotenv()

async def lifespan(app: FastAPI):
    await init()
    print("Starting Db")

    yield
    print("Closing")


app = FastAPI(lifespan=lifespan)




app.include_router(router=user_controller.user_router)
app.include_router(router=audio_controller.audio_router)
app.include_router(router=transcript_summary_controller.transcript_router)
app.include_router(router=admin_controller.admin_router)