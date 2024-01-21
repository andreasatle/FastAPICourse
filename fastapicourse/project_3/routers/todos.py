from fastapi import APIRouter, HTTPException
from starlette import status
from fastapicourse.project_3 import models
from fastapicourse.project_3 import database
from fastapicourse.project_3 import types

router = APIRouter()

@router.get('/todo/', status_code=status.HTTP_200_OK)
async def read_all_todos(db: types.SessionType):
    return db.query(models.Todos).all()

@router.get('/todo/{id}', status_code=status.HTTP_200_OK)
async def read_todo(id: types.IdType, db: types.SessionType):
    todo = db.query(models.Todos).filter(models.Todos.id == id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {id} not found")
    return todo

@router.post('/todo/create', status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_request: types.TodoRequest,
    db: types.SessionType
):
    # Create a todo-model from a validated todo-request
    todo = models.Todos(**todo_request.model_dump())

    # Add the todo-model to the database
    db.add(todo)

    # Commit the changes to the database
    db.commit()

@router.put('/todo/update/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    id: types.IdType,
    db: types.SessionType
):

    # Retrieve the todo-model from the database
    todo_db = db.query(models.Todos).filter(models.Todos.id == id).first()
    if todo_db is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {id} not found")

    # Update the todo-model
    todo_db.update_with(todo_request)

    db.add(todo_db)
    db.commit()

@router.delete('/todo/delete/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    id: types.IdType,
    db: types.SessionType
):
    db.query(models.Todos).filter(models.Todos.id == id).delete()
    db.commit()