from fastapi import APIRouter, HTTPException
from starlette import status
from fastapicourse.project_3 import models
from fastapicourse.project_3 import database
from fastapicourse.project_3 import types
from fastapi.security import OAuth2PasswordRequestForm
router = APIRouter()

def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()
    return (user is not None) and (types.bcrypt_context.verify(password, user.hashed_password))

@router.get('/auth/')
async def auth():
    return {"message": "Hello World"}

@router.post('/auth/create', status_code=status.HTTP_201_CREATED)
async def create_user(user_request: types.UserRequest, db: types.SessionType):
    user = models.Users(**user_request.model_dump())
    db.add(user)
    db.commit()

@router.post('/auth/login', status_code=status.HTTP_200_OK)
async def login_user(form_data: types.AuthType, db: types.SessionType):
    if authenticate_user(form_data.username, form_data.password, db):
        return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Login unsuccessful")
