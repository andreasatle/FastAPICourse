from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from fastapicourse.project_3 import models
from fastapicourse.project_3 import database
from fastapicourse.project_3.routers import auth, todos, users, admin, todosv2
from pathlib import Path

app = FastAPI()

# Convoluted (but correct) way to get the path to the static directory.
root_dir = Path(__file__).resolve().parent
static_dir = Path.joinpath(root_dir, "static")

app.mount("/static", StaticFiles(directory=static_dir), name="static")

models.Base.metadata.create_all(bind=database.engine)

# app.include_router(auth.router)
# app.include_router(todos.router)
# app.include_router(users.router)
# app.include_router(admin.router)
app.include_router(todosv2.router)
