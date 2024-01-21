from fastapi import APIRouter, HTTPException
from starlette import status
from fastapicourse.project_3 import models
from fastapicourse.project_3 import database
from fastapicourse.project_3 import types
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

load_dotenv()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "")

if JWT_SECRET_KEY == "":
    raise ValueError("JWT_SECRET_KEY environment variable not set")
if JWT_ALGORITHM == "":
    raise ValueError("JWT_ALGORITHM environment variable not set")

print(JWT_SECRET_KEY, JWT_ALGORITHM)

def authenticate_user(username: str, password: str, db) -> models.Users | None:
    user = db.query(models.Users).filter(models.Users.username == username).first()
    if (user is not None) and (types.bcrypt_context.verify(password, user.hashed_password)):
        return user
    else:
        return None

def create_jwt_token(user: models.Users, tdelta: timedelta) -> str:
    jwt_payload = {
        "sub": user.username,
        "id": user.id,
        "exp": datetime.utcnow() + tdelta
    }
    return jwt.encode(jwt_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_user(user_request: types.UserRequest, db: types.SessionType):
    user = models.Users(**user_request.model_dump())

    # Validate that the username does not already exist
    db_user = db.query(models.Users).filter(models.Users.username == user.username).first()
    if db_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with username '{user.username}' already exists")

    # Validate that the email does not already exist
    db_user = db.query(models.Users).filter(models.Users.email == user.email).first()
    if db_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with email '{user.email}' already exists")

    db.add(user)
    db.commit()

@router.post('/login', status_code=status.HTTP_200_OK)
async def login_user(form_data: types.AuthType, db: types.SessionType):
    user = authenticate_user(form_data.username, form_data.password, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Login unsuccessful")
    token = create_jwt_token(user, timedelta(minutes=30))
    return types.Token(access_token=token).model_dump()
    

