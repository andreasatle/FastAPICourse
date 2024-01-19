from fastapi import FastAPI, Path
from pydantic import BaseModel, Field
from typing import Annotated

app = FastAPI()

IdType = Annotated[int, Field(gt=0)]
RatingType = Annotated[int, Field(ge=0, le=5)]
YearType = Annotated[int, Field(ge=1900, le=2024)]

class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_year: int

    def __init__(self, id: int, title: str, author: str, description: str, rating: int, published_year: int):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_year = published_year

class BookRequest(BaseModel):
    id: IdType|None = None
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=3, max_length=100)
    rating: RatingType
    published_year: int = Field(ge=0, le=2024)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "CS Primer",
                "author": "John Doe",
                "description": "A book about computer science",
                "rating": 4,
                "published_year": 2021
            }
        }

BOOKS: list[Book] = [
    Book(1, "CS Primer", "John Doe", "A book about computer science", 5, 1984),
    Book(2, "Math Primer", "Jane Doe", "A book about math", 4, 1995),
    Book(3, "History Primer", "John Doe", "A book about history", 3, 2017),
    Book(4, "Chemistry Primer", "Jane Doe", "A book about chemistry", 2, 2019),
    Book(5, "Physics Primer", "John Doe", "A book about physics", 4, 2019),
    Book(6, "Cooking Primer", "Sven Doe", "A book about cooking", 5, 2017),
]
@app.get('/books')
async def read_all_books():
    return BOOKS

@app.post('/books/create')
async def create_book(book_request: BookRequest):
    # Validate the request and create a Book object
    book = Book(**book_request.model_dump())
    BOOKS.append(next_book_id(book))

@app.get('/books/{id}')
async def read_book(id: IdType):
    for book in BOOKS:
        if book.id == id:
            return book
    return {'error': f'Book with id {id} not found'}

@app.get('/books/byrating/')
async def read_books_by_rating(rating: RatingType):
    return [
        book
        for book in BOOKS
        if book.rating == rating
    ]

@app.get('/books/published_year/')
async def read_books_by_published_year(year: YearType):
    return [
        book
        for book in BOOKS
        if book.published_year == year
    ]   

@app.put('/books/update/')
async def update_book(book_request: BookRequest):
    book = Book(**book_request.model_dump())
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book

@app.delete('/books/delete/{id}')
async def delete_book(id: IdType):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == id:
            BOOKS.pop(i)
            break

def next_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book