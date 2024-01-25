from fastapi import APIRouter, HTTPException
from starlette import status
from fastapicourse.project_3 import models
from fastapicourse.project_3 import database
from fastapicourse.project_3 import types
from fastapicourse.project_3.database import SessionDep
from .auth import get_current_user, authenticate_user

from fastapi import Depends
from typing import Annotated

router = APIRouter(
    prefix = '/users',
    tags = ['users']
)

UserDep = Annotated[models.Users, Depends(get_current_user)]

@router.get('/', status_code=status.HTTP_200_OK)
async def read_current_user(user: UserDep, db: SessionDep):
    if user is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Could not validate credentials"
        )

    return user

@router.put('/update/password', status_code=status.HTTP_204_NO_CONTENT)
async def update_password(
    user: UserDep,
    password_request: types.PasswordRequest,
    db: SessionDep
):
    # Validate that the user exists and that the old password is correct
    if user is None or not types.bcrypt_context.verify(password_request.old_password, user.hashed_password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Could not validate credentials"
        )

    # Change password and save to database
    user.hashed_password = types.bcrypt_context.hash(password_request.new_password)
    db.add(user)
    db.commit()

@router.put('/update/phone_number/{phone_number}', status_code=status.HTTP_204_NO_CONTENT)
async def update_phone_number(
    user: UserDep,
    phone_number: types.PhoneNumberType,
    db: SessionDep
):
    # Validate that the user exists
    if user is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Could not validate credentials"
        )

    # Change phone number and save to database
    user.phone_number = phone_number
    db.add(user)
    db.commit()
