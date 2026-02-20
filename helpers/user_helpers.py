import jwt 
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException
from typing import Annotated
from models.user import User
from dotenv import load_dotenv
import os
load_dotenv()
SECRET_KEY =os.getenv("SECRET_KEY")
ALgortithm =os.getenv("ALgortithm")

security = HTTPBearer()


async def read_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    try:
        payload = decode_token(credentials.credentials)
        user = await User.get_or_none(id=payload.get("user_id", None))
        if not user:
            raise HTTPException("user not found")
        return user
    except jwt.exceptions.InvalidSignatureError as e:
            raise HTTPException(404, "User Not Found")


def create_access_token(payload: dict):
    return jwt.encode(payload, SECRET_KEY, ALgortithm)

def decode_token(jwt_token: str):
    return jwt.decode(jwt_token, SECRET_KEY, [ALgortithm] )


if __name__ == "__main__":  
    token = create_access_token({"user_id": 1})
    print(token)

    print(decode_token(token))