from fastapi import FastAPI
from fastapicourse.project_3 import models
from fastapicourse.project_3 import database
from fastapicourse.project_3.routers import auth, todos, users, admin

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(users.router)
app.include_router(admin.router)

