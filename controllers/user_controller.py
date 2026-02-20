from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends
from models.user import User
from argon2 import PasswordHasher
from helpers.user_helpers import create_access_token
import argon2
from helpers.user_helpers import read_current_user
from typing import Annotated
ph = PasswordHasher()

class user_signup(BaseModel):
    name: str
    email: str
    password: str

class user_response(BaseModel):
    name: str
    email:str

class get_user_response(BaseModel):
    name: str
    email: str
    id: str




user_router = APIRouter(tags=["users"])

@user_router.get("/")
def index():
    return {"status": "user_router is Working Properly"}

@user_router.post("/signup", response_model=user_response)
async def user_signup(request: user_signup):
    new_user = await User.create(name=request.name,
                                  email=request.email,
                                  password=ph.hash(request.password))
    return new_user


@user_router.get("/login")  
async def login(email: str, password:str ):
    try:
        user = await User.get_or_none(email=email)
        if not ph.verify(user.password, password):
            raise HTTPException(400, "Password Doesn't match")
        token = create_access_token({"user_id": str(user.id), 'email': user.email })
        return {"token": token}
    except argon2.exceptions.VerifyMismatchError as e:
            raise HTTPException(400, "Password is wrong")
    except Exception as e:
        raise HTTPException(400, str(e))
@user_router.delete("/delete-user")
async def delete_user(email:str, user: Annotated[User, Depends(read_current_user)]):
    print("User is", user.id, user.email)
    await User.filter(email__contains=email).delete()
    return {'status':"deleted"}

@user_router.put("/update_user")
async def update_user(email: str, password:str, user: Annotated[User, Depends(read_current_user)]):
   user = await User.get_or_none(email=email)
   if not user:
       raise HTTPException(400, "Wrong Email")
   user.password = password
   await user.save()
   return user



