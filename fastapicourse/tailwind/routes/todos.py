from fastapi import APIRouter
from fastapi import Request, HTTPException
from pathlib import Path
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette import status
from fastapicourse.tailwind.database import SessionDep
from fastapicourse.tailwind.models import Todos, Users
from typing import Annotated
from pydantic import Field
from fastapicourse.tailwind.routes.auth import get_current_user
from fastapi import Depends

router = APIRouter(prefix="/todos", tags=["todos"])

UserDep = Annotated[Users, Depends(get_current_user)]

root_dir = Path(__file__).resolve().parent.parent
template_dir = Path.joinpath(root_dir, "templates")
templates = Jinja2Templates(directory=template_dir)

StringType = Annotated[str, Field(min_length=1)]
PriorityType = Annotated[int, Field(ge=1, le=5)]


class TodoRequest(BaseModel):
    title: StringType
    description: StringType
    priority: PriorityType
    completed: bool = False

    # I don't want to put this in the model, because the TodoRequest is local to this file.
    def dump_into(self, todo: Todos):
        if todo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id {todo_id} not found",
            )

        todo.title = self.title
        todo.description = self.description
        todo.priority = self.priority
        todo.completed = self.completed


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_todos(request: Request, user: UserDep, db: SessionDep):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    todos = db.query(Todos).filter(Todos.owner_id == user.id).all()
    #todos = user.todos
    #return templates.TemplateResponse(request, "todos.html", {"todos": todos})
    return todos


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def get_one_todo(request: Request, user: UserDep, db: SessionDep, todo_id: int):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    todo = (
        db.query(Todos)
        .filter(Todos.owner_id == user.id)
        .filter(Todos.id == todo_id)
        .first()
    )

    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id {todo_id} not found",
        )
    #todos = user.todos
    #return templates.TemplateResponse(request, "todos.html", {"todos": todos})
    return todo

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_todo(
    request: Request, user: UserDep, db: SessionDep, todo_request: TodoRequest
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    todo = Todos(**todo_request.model_dump(), owner_id=user.id)
    todo_request.dump_into(todo)
    db.add(todo)
    db.commit()


@router.delete("/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(request: Request, user: UserDep, db: SessionDep, todo_id: int):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    todo = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.id)
        .first()
    )
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id {todo_id} not found",
        )

    db.delete(todo)
    db.commit()


@router.put("/update/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    request: Request,
    user: UserDep,
    db: SessionDep,
    todo_request: TodoRequest,
    todo_id: int,
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    todo = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.id)
        .first()
    )
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id {todo_id} not found",
        )

    todo_request.dump_into(todo)
    db.add(todo)
    db.commit()
