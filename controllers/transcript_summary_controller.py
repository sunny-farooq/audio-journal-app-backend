from fastapi import APIRouter, HTTPException, Depends
from helpers.user_helpers import read_current_user
from typing import Annotated
from models.user import User
import os
from models.audio import Audio
from helpers.transcript_helper import transcript_helper
from helpers.summary_helper import summary_helper
from dotenv import load_dotenv
import os
from datetime import date

today = date.today()
print(today)

load_dotenv()

os.environ['api_key']=os.getenv('GEMINI_API_KEY')

transcript_router = APIRouter(prefix="/transcript",tags=["Transcript & Summary"])

@transcript_router.post("/get-transcript")
async def get_transcript(user: Annotated[User, Depends(read_current_user)], audio_id:str, today=today):
    get_audio = await Audio.get(audio_id=audio_id,user=user)
    if not get_audio:
        raise HTTPException("The files doesn't exists.")
    path = get_audio.audio_path
    transcript_text = await transcript_helper(path)
    await Audio.get_or_none(audio_id=audio_id,user=user).update(transcripted=True,transcript=transcript_text, transcript_created_at=today)
    return transcript_text

@transcript_router.post("/get-summary")
async def get_summary(user: Annotated[User, Depends(read_current_user)], audio_id:str, today=today):
    get_audio = await Audio.get(audio_id=audio_id,user=user)
    if not get_audio:
        raise HTTPException("The files doesn't exists.")
    path = get_audio.audio_path
    summary_text = await summary_helper(path)
    await Audio.get_or_none(audio_id=audio_id,user=user).update(summary_created=True,summary=summary_text, summary_created_at=today)
    return summary_text
    