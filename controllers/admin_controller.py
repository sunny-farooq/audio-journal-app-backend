from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from models.admin import Admin
from argon2 import PasswordHasher
from helpers.admin_helper import create_access_token
import argon2
from helpers.admin_helper import read_current_admin
from typing import Annotated
from models.user import User
from models.audio import Audio
from collections import Counter
ph = PasswordHasher()

class AdminSignupRequest(BaseModel):
    name: str
    email: str
    password: str

class admin_response(BaseModel):
    name: str
    email:str

class get_admin_response(BaseModel):
    name: str
    email: str
    id: str




admin_router = APIRouter(tags=["Admin"])

@admin_router.get("/")
def index():
    return {"status": "admin_router is Working Properly"}


@admin_router.post("/admin-signup", response_model=admin_response)
async def create_admin(request: AdminSignupRequest):
    new_admin = await Admin.create(name=request.name,
                                  email=request.email,
                                  password=ph.hash(request.password))
    


    return new_admin


@admin_router.get("/admin-login")  
async def login(email: str, password:str ):
    try:
        user = await Admin.get_or_none(email=email)
        if not ph.verify(user.password, password):
            raise HTTPException(400, "Admin not found")
        token = create_access_token({"user_id": str(user.id), 'email': user.email })
        return {"token": token}
    except argon2.exceptions.VerifyMismatchError as e:
            raise HTTPException(400, "Password or Email is Wrong")
    except Exception as e:
        raise HTTPException(400, str(e))


@admin_router.get("/get-users")  
async def get_users(admin: Annotated[Admin, Depends(read_current_admin)]):
    all_users = await User.all().values("id","name","email")
    return all_users



@admin_router.get("/get-total-audio-files-number")
async def get_audio_files_number(admin: Annotated[Admin, Depends(read_current_admin)]):
    try:
        audios = await Audio.all().values("audio_id")
    except Exception as e:
        return {"error occurred"}
    finally:
        return {"Number of audio files": len(audios) }

@admin_router.get("/storage-cost")
async def get_storage_cost(admin: Annotated[Admin, Depends(read_current_admin)]):
    # # try:
    # #     storage = await Audio.all().values("size_of_audio")
    # #     list_of_storage = []
    # #     for store in storage:

    # # finally:
    # #     return total_size
    # storage = await Audio.all().values("size_of_audio")
    
    # for store in storage:
    #     storage_list=[]
    #     storage_list = storage_list.append(store["size_of_audio"])
    # return storage_list
    storage = await Audio.all().values("size_of_audio")
    
    # Method 1: Direct sum (simplest and best)
    total_size = sum(float(store["size_of_audio"]) for store in storage)
    rounded_size = round(total_size, 2)
    in_Gb=rounded_size/1024
    cost = in_Gb*0.1
    round_cost=round(cost,2)
    return {"total_size_gb": round(in_Gb,2), "cost": round_cost, "cost_currency":"Dollar"}


@admin_router.get("/get-format-number")
async def format_analysis(admin: Annotated[Admin, Depends(read_current_admin)]):
    formats = await Audio.all().values("format_type")
    format_counts = Counter(format["format_type"] for format in formats)
    return {"total_files": len(formats), "format_breakdown": dict(format_counts)}

# @admin_router.get("/average-duration")
# async def length_analysis(admin: Annotated[Admin, Depends(read_current_admin)]):
#     durations = await Audio.all().values("duration")
#     return durations

def duration_to_seconds(duration_str):
    """Convert 'MM:SS' format to total seconds"""
    minutes, seconds = duration_str.split(':')
    return int(minutes) * 60 + int(seconds)

def seconds_to_duration(total_seconds):
    """Convert total seconds back to 'MM:SS' format"""
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    return f"{minutes}:{seconds:02d}"

@admin_router.get("/average-duration")
async def get_average_duration(admin: Annotated[Admin, Depends(read_current_admin)]):
    durations = await Audio.all().values("duration")
    
    if not durations:
        raise HTTPException(404, "No audio files found")
    
    # Calculate total seconds
    total_seconds = sum(duration_to_seconds(d["duration"]) for d in durations)
    
    # Calculate average
    average_seconds = total_seconds / len(durations)
    average_duration = seconds_to_duration(average_seconds)
    
    return {
        "average_duration": average_duration,
        "total_files": len(durations),
        "total_duration": seconds_to_duration(total_seconds)
    }