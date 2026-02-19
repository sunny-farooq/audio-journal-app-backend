import jwt 
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException
from typing import Annotated
from models.admin import Admin
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY =os.getenv("ADMIN_SECRET_KEY")
ALgortithm =os.getenv("ALgortithm")

security = HTTPBearer()

async def read_current_admin(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    payload = decode_token(credentials.credentials)
    user = await Admin.get_or_none(id=payload.get("user_id", None))
    if not user:
        raise HTTPException("admin not found")
    return user

def create_access_token(payload: dict):
    return jwt.encode(payload, SECRET_KEY, ALgortithm)

def decode_token(jwt_token: str):
    return jwt.decode(jwt_token, SECRET_KEY, [ALgortithm] )


if __name__ == "__main__":  
    token = create_access_token({"user_id": 1})
    print(token)

    print(decode_token(token))