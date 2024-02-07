from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapicourse.tailwind import models, database
from starlette import status
import sys
from fastapi import FastAPI
app = FastAPI()

# Convoluted (but correct) way to get the path to the static directory.
root_dir = Path(__file__).resolve().parent
static_dir = Path.joinpath(root_dir, "static")
sys.path.append(str(Path.joinpath(root_dir, "routes")))

from fastapicourse.tailwind.routes import home, books, auth, users, todos, admin

app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory="templates")

models.Base.metadata.create_all(bind=database.engine)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(todos.router)
app.include_router(home.router)
app.include_router(books.router)

@app.get('/healthy', status_code=status.HTTP_200_OK, tags=['healthcheck'], response_model=dict)
async def healthy():
    return {"status": "ok"}