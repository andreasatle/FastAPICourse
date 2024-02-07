from fastapi import APIRouter, HTTPException, Request
from starlette import status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapicourse.project_3 import models
from fastapicourse.project_3 import database
from fastapicourse.project_3 import types
from fastapicourse.project_3.database import SessionDep
from .auth import get_current_user

from fastapi import Depends
from typing import Annotated

from pathlib import Path

# Convoluted (but correct) way to get the path to the templates directory.
root_dir = Path(__file__).resolve().parent.parent
template_dir = Path.joinpath(root_dir, "templates")

router = APIRouter(prefix="/todosv2", tags=["todosv2"])

templates = Jinja2Templates(directory=template_dir)

UserDep = Annotated[models.Users, Depends(get_current_user)]


@router.get("/test")
async def test_page(request: Request):
    return templates.TemplateResponse(request, "test.html", {})


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_todos(user: UserDep, db: SessionDep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    todos = db.query(models.Todos).filter(models.Todos.owner_id == user.id).all()
    return templates.TemplateResponse(request, "test.html", {})


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def read_todo(user: UserDep, id: types.IdType, db: SessionDep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    todo = (
        db.query(models.Todos)
        .filter(models.Todos.id == id)
        .filter(models.Todos.owner_id == user.id)
        .first()
    )

    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id {id} not found"
        )

    return todo


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_todo(
    user: UserDep,
    todo_request: types.TodoRequest,
    db: SessionDep,
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    # Create a todo-model from a validated todo-request
    todo = models.Todos(**todo_request.model_dump(), owner_id=user.id)

    # Add the todo-model to the database
    db.add(todo)

    # Commit the changes to the database
    db.commit()


@router.put("/update/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    user: UserDep, id: types.IdType, todo_request: types.TodoRequest, db: SessionDep
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    # Retrieve the todo-model from the database
    todo_db = (
        db.query(models.Todos)
        .filter(models.Todos.id == id)
        .filter(models.Todos.owner_id == user.id)
        .first()
    )

    if todo_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id {id} not found"
        )

    # Update the todo-model
    todo_db.update_with(todo_request)

    db.add(todo_db)
    db.commit()


@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: UserDep, id: types.IdType, db: SessionDep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    todo = (
        db.query(models.Todos)
        .filter(models.Todos.id == id)
        .filter(models.Todos.owner_id == user.id)
        .first()
    )

    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id {id} not found"
        )

    todo = db.delete(todo)
    db.commit()
