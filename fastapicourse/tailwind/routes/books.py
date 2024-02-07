from fastapi import APIRouter
from fastapi import Request, HTTPException
from pathlib import Path
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette import status

router = APIRouter(prefix="/books", tags=["books"])

root_dir = Path(__file__).resolve().parent.parent
template_dir = Path.joinpath(root_dir, "templates")
templates = Jinja2Templates(directory=template_dir)


class BookRequest(BaseModel):
    title: str
    author: str
    category: str


class Book:
    title: str
    author: str
    category: str

    def __init__(self, title: str, author: str, category: str):
        self.title = title
        self.author = author
        self.category = category

    def update_with(self, book_request: BookRequest):
        self.title = book_request.title
        self.author = book_request.author
        self.category = book_request.category


BOOKS = [
    Book(title="The Great Gatsby", author="F. Scott Fitzgerald", category="Fiction"),
    Book(title="The Catcher in the Rye", author="J.D. Salinger", category="Fiction"),
    Book(title="1984", author="George Orwell", category="Fiction"),
    Book(title="The Lord of the Rings", author="J.R.R. Tolkien", category="Fiction"),
    Book(title="Pride and Prejudice", author="Jane Austen", category="Fiction"),
    Book(title="To Kill a Mockingbird", author="Harper Lee", category="Fiction"),
    Book(
        title="Harry Potter and the Sorcerer's Stone",
        author="J.K. Rowling",
        category="Fiction",
    ),
    Book(
        title="One Hundred Years of Solitude",
        author="Gabriel García Márquez",
        category="Fiction",
    ),
]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_books(request: Request):
    return templates.TemplateResponse(request, "books.html", {"books": BOOKS})


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest, request: Request):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(new_book)
    return templates.TemplateResponse(request, "books.html", {"books": BOOKS})


@router.get("/{title}", status_code=status.HTTP_200_OK)
async def get_book_by_title(title: str, request: Request):
    books = [book for book in BOOKS if book.title.casefold() == title.casefold()]

    return templates.TemplateResponse(request, "books.html", {"books": books})


@router.put("/update/title/{old}/{new}", status_code=status.HTTP_204_NO_CONTENT)
async def update_book_by_title(old: str, new: str, request: Request):
    for book in BOOKS:
        if book.title.casefold() == old.casefold():
            book.title = new
            return templates.TemplateResponse(request, "books.html", {"books": BOOKS})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@router.delete("/delete/title/{title}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_by_title(title: str, request: Request):
    for book in BOOKS:
        if book.title.casefold() == title.casefold():
            BOOKS.remove(book)
            return None
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
