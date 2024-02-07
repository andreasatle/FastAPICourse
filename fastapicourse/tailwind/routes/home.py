from fastapi import APIRouter
from fastapi import Request
from pathlib import Path
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/home", tags=["home"])

root_dir = Path(__file__).resolve().parent.parent
template_dir = Path.joinpath(root_dir, "templates")
templates = Jinja2Templates(directory=template_dir)


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {})
