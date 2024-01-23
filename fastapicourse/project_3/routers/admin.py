from fastapi import APIRouter, HTTPException
from starlette import status
from fastapicourse.project_3 import models
from fastapicourse.project_3 import database
from fastapicourse.project_3 import types
from fastapicourse.project_3.database import SessionDep
from .auth import get_current_user

from fastapi import Depends
from typing import Annotated

router = APIRouter(
    prefix = '/admin/todos',
    tags = ['admin']
)

UserDep = Annotated[models.Users, Depends(get_current_user)]

@router.get('/', status_code=status.HTTP_200_OK)
async def read_all_todos(user: UserDep, db: SessionDep):
    if user is None or user.role != "admin":
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Could not validate credentials"
        )

    return db.query(models.Todos).all()

@router.get('/{id}', status_code=status.HTTP_200_OK)
async def read_todo(user: UserDep, id: types.IdType, db: SessionDep):
    if user is None or user.role != "admin":
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Could not validate credentials"
        )

    todo = db.query(models.Todos) \
        .filter(models.Todos.id == id) \
        .first()

    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id {id} not found"
        )

    return todo

@router.delete('/delete/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: UserDep,
    id: types.IdType,
    db: SessionDep
):
    if user is None or user.role != "admin":
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Could not validate credentials"
        )

    todo = db.query(models.Todos) \
        .filter(models.Todos.id == id) \
        .first()
    
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Todo with id {id} not found"
        )

    todo = db.delete(todo)
    db.commit()