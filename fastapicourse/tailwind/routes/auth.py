from fastapi import APIRouter
from fastapi import Request, HTTPException

from pydantic import BaseModel, Field, field_validator
from starlette import status

from typing import Annotated

from fastapicourse.tailwind.database import SessionDep
from fastapicourse.tailwind.models import Users
from fastapicourse.tailwind.jwt_tokens import JWTToken

import bcrypt
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer

from email_validator import validate_email, EmailNotValidError
from datetime import datetime, timedelta
router = APIRouter(prefix="/auth", tags=["auth"])

jwt_token = JWTToken()


def authenticate_user(username: str, password: str, db) -> Users | None:
    user = db.query(Users).filter(Users.username == username).first()

    if user is not None and bcrypt.checkpw(
        password.encode(), user.hashed_password.encode()
    ):
        return user
    else:
        return None


PasswordType = Annotated[str, Field(min_length=3, alias="password")]


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    phone_number: str
    hashed_password: PasswordType
    is_active: bool = True
    role: str | None = None

    @field_validator("hashed_password")
    @classmethod
    def hash_password(cls, password: PasswordType) -> PasswordType:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @field_validator("email")
    @classmethod
    def valid_email(cls, email: str) -> str:
        try:
            validate_email(email)
        except EmailNotValidError:
            raise ValueError("Invalid email format")
        return email


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# This is a somewhat cryptic way to get the authorization
TokenDep = Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="/auth/token"))]
RequestFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]


def get_current_user(token: TokenDep, db: SessionDep) -> Users:
    try:
        payload = jwt_token.decode(token)
        user_id = payload["id"]
        exp = payload["exp"]
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid jwt-token"
        )

    if exp < datetime.utcnow().timestamp():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )

    user = db.query(Users).filter(Users.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user"
        )

    return user


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request, db: SessionDep, user_request: CreateUserRequest
):
    user = Users(**user_request.model_dump())

    # Validate that the username does not already exist
    db_user = db.query(Users).filter(Users.username == user.username).first()
    if db_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with username '{user.username}' already exists",
        )

    # Validate that the email does not already exist
    db_user = db.query(Users).filter(Users.email == user.email).first()
    if db_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{user.email}' already exists",
        )

    db.add(user)
    db.commit()


@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def create_token(request: Request, db: SessionDep, form_data: RequestFormDep):
    user = authenticate_user(form_data.username, form_data.password, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Set the token expiration to 15 minutes
    token_expiration_delta = timedelta(minutes=15)

    access_token = jwt_token.encode(user, token_expiration_delta)
    return Token(access_token=access_token).model_dump()
