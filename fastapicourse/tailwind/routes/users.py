from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from pathlib import Path
from starlette import status
from fastapicourse.tailwind.models import Users
from fastapicourse.tailwind.routes.auth import get_current_user
from typing import Annotated
from fastapicourse.tailwind.database import SessionDep
from pydantic import BaseModel, Field
import bcrypt

router = APIRouter(prefix="/users", tags=["users"])

UserDep = Annotated[Users, Depends(get_current_user)]

root_dir = Path(__file__).resolve().parent.parent
template_dir = Path.joinpath(root_dir, "templates")
templates = Jinja2Templates(directory=template_dir)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(request: Request, user: UserDep, db: SessionDep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return templates.TemplateResponse(request, "users.html", {"users": [user]})

PasswordType = Annotated[str, Field(min_length=3)]

class PasswordRequest(BaseModel):
    old_password: PasswordType
    new_password: PasswordType


@router.put('/update_password', status_code=status.HTTP_204_NO_CONTENT)
async def update_password(request: Request, user: UserDep, db: SessionDep, password_request: PasswordRequest):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    if not bcrypt.checkpw(password_request.old_password.encode(), user.hashed_password.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong password",
        )

    user.hashed_password = bcrypt.hashpw(password_request.new_password.encode(), bcrypt.gensalt()).decode()
    db.add(user)
    db.commit()
