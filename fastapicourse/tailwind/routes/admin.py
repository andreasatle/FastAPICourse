from fastapi import APIRouter
from fastapi import Request, HTTPException
from pathlib import Path
from fastapi.templating import Jinja2Templates
from starlette import status
from fastapicourse.tailwind.database import SessionDep
from fastapicourse.tailwind.models import Todos, Users
from typing import Annotated
from fastapicourse.tailwind.routes.auth import get_current_user
from fastapi import Depends

router = APIRouter(prefix="/admin", tags=["admin"])

UserDep = Annotated[Users, Depends(get_current_user)]

root_dir = Path(__file__).resolve().parent.parent
template_dir = Path.joinpath(root_dir, "templates")
templates = Jinja2Templates(directory=template_dir)


@router.get("/todos", status_code=status.HTTP_200_OK)
async def get_all_todos(request: Request, user: UserDep, db: SessionDep):
    if user is None or user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    todos = db.query(Todos).all()

    # return templates.TemplateResponse(
        # request, "todos.html", {"todos": todos, "admin": True}
    # )
    return todos


@router.delete("/todos/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(request: Request, user: UserDep, db: SessionDep, todo_id: int):
    if user is None or user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id {todo_id} not found",
        )
    db.delete(todo)
    db.commit()


@router.get("/users", status_code=status.HTTP_200_OK)
async def get_users(request: Request, user: UserDep, db: SessionDep):
    if user is None or user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    users = db.query(Users).all()

    # return templates.TemplateResponse(request, "users.html", {"users": users})
    return users
