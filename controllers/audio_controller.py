from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends
from helpers.user_helpers import read_current_user
from typing import Annotated
from models.user import User
from fastapi import UploadFile, File
import shutil
import uuid
import os
import mutagen
from models.audio import Audio
from fastapi.responses import FileResponse
from fastapi import status

ALLOWED_CONTENT_TYPES = {
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/mp4",
    "audio/x-m4a"
}


class audio_api_response(BaseModel):
    name: str
    space_taken: int

audio_router = APIRouter(prefix="/audio",tags=["Audio"])

@audio_router.get("/")
def index(user: Annotated[User, Depends(read_current_user)]):
    return {"status": "working"}

@audio_router.post("/upload-file")
async def upload_file(user: Annotated[User,Depends(read_current_user)], file: UploadFile=File(...)):
    try:
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Content-Type must be an audio file."
            )
        ext=file.filename[-4:]
        coded=uuid.uuid4()
        coded_str=str(coded)
        file_name=coded_str+ext
        file_location=f'uploads/{file_name}'
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size_bytes = os.path.getsize(file_location)
        file_size_mb = file_size_bytes / (1024 * 1024)
        rounded_size = round(file_size_mb, 2)
        size_of_audio=str(rounded_size)
        audio=mutagen.File(file_location)
        duration_seconds = audio.info.length
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        

        total_duration=f"{minutes}:{seconds:02d}"
        await Audio.create(audio_path=file_location, size_of_audio=size_of_audio,format_type=file.content_type,duration=total_duration,user=user)
        uploaded_audio = await Audio.get(user=user,audio_path=file_location).values("format_type","duration","audio_path","size_of_audio","audio_id")
        return uploaded_audio
    except Exception as e:
        raise HTTPException(status=status.HTTP_404_NOT_FOUND)


@audio_router.get("/get-audio")
async def get_audio(user: Annotated[User,Depends(read_current_user)],audio_id:str):
    try:
        requested_audio=await Audio.get(audio_id=audio_id,user=user).values("audio_path")
        if not requested_audio:
            raise HTTPException(status_code=404, detail="Audio file not found.")
        file_path=requested_audio["audio_path"]
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Audio file not found.")
        return FileResponse(path=file_path)
    except Exception as e:
        raise HTTPException(404, "Not Found")


@audio_router.post("/test_audio")
async def upload_test_file(file: UploadFile=File(...)):
    try:
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Content-Type must be an audio file."
            )
        ext=file.filename[-4:]
        coded=uuid.uuid4()
        coded_str=str(coded)
        file_name=coded_str+ext
        file_location=f'uploads/{file_name}'
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size_bytes = os.path.getsize(file_location)
        file_size_mb = file_size_bytes / (1024 * 1024)
        rounded_size = round(file_size_mb, 2)
        size_of_audio=str(rounded_size)
        audio=mutagen.File(file_location)
        duration_seconds = audio.info.length
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        total_duration=f"{minutes}:{seconds:02d}"
        os.remove(file_location)
        return {"filename": file_name, "content_type": file.content_type,"file_size":rounded_size, "duration":total_duration}
    except Exception as e:
        raise HTTPException(status=status.HTTP_404_NOT_FOUND)

@audio_router.get("/get-all-audio")
async def get_all_audio(user: Annotated[User,Depends(read_current_user)]):
    try:
        all_audio_path= await Audio.filter(user=user)
        return all_audio_path
    except Exception as e:
        raise HTTPException(status=status.HTTP_404_NOT_FOUND)

@audio_router.delete("/delete-audio")
async def delete_audio(user: Annotated[User,Depends(read_current_user)],audio_id:str):
    try:
        requested_audio=await Audio.get(audio_id=audio_id,user=user).values("audio_path")
        if not requested_audio:
            raise HTTPException("Audio doesn't exist")
        audio_path=requested_audio["audio_path"]
        if not audio_path:
            raise HTTPException("File doesn't exist")
        os.remove(audio_path)
        await Audio.filter(audio_id=audio_id,user=user).delete()
        return {"status":"Successfully Deleted"}
    except Exception as e:
        raise HTTPException(404, "File not Found")

@audio_router.post("/create-category")
async def create_category(user: Annotated[User,Depends(read_current_user)], category_name:str, audio_id:str):
    try:
        await Audio.filter(audio_id=audio_id, user=user).update(category=category_name) 
        return {"status":"category assigned"}
    except Exception as e:
        raise HTTPException(status=status.HTTP_404_NOT_FOUND)

@audio_router.delete("/delete-category")
async def delete_category(user: Annotated[User,Depends(read_current_user)],category_name:str):
    try:
        get_category= await Audio.filter(category=category_name, user=user)
        if not get_category:
            raise HTTPException("Category Doesn't Exists")
        await Audio.filter(category=category_name, user=user).update(category=None)
        return {"status":"Deleted Successfully"}
    except Exception as e:
        raise HTTPException(status=status.HTTP_404_NOT_FOUND)

@audio_router.delete("/delete-audio-category")
async def delete_audio(user: Annotated[User,Depends(read_current_user)],category:str,audio_id:str):
    try:
        get_audio=await Audio.get_or_none(category=category, user=user, audio_id=audio_id).values('audio_path')
        if not get_audio:
            raise HTTPException("audio not in given category")
        audio_path=get_audio['audio_path']
        await Audio.filter(category=category, user=user, audio_id=audio_id).delete()
        os.remove(audio_path)
        return {"status": "successfully deleted the audio"}
    except Exception as e:
        raise HTTPException(404, "File not FOund")
    


