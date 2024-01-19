from fastapi import FastAPI, Body

app = FastAPI()

BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]

@app.get('/books')
async def read_all_books():
    return BOOKS

@app.get('/books/')
async def read_category_by_query(category: str):
    return [
        book
        for book in BOOKS
        if book.get('category').casefold() == category.casefold()
    ]

@app.get('/books/{title}')
async def read_book(title: str):
    for book in BOOKS:
         if book.get('title').casefold() == title.casefold():
             return book
    return {'error': 'Book not found'}


@app.get('/books/{author}/')
async def read_author_category_by_query(author: str, category: str):
    return [
        book
        for book in BOOKS
        if (
            book.get('author').casefold() == author.casefold()
            and
            book.get('category').casefold() == category.casefold()
        )
    ]

@app.post('/books/create')
async def create_book(book=Body()):
    print(f"{book=}")
    BOOKS.append(book)

@app.put('/books/update')
async def update_book(book=Body()):
    print(f"{book=}")
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == book.get('title').casefold():
            BOOKS[i] = book

@app.delete('/books/delete/{title}')
async def delete_book(title: str):
    print(f"{title=}")
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == title.casefold():
            BOOKS.pop(i)
            break

@app.get('/books/author/{author}')
async def read_author(author: str):
    return [
        book
        for book in BOOKS 
        if book.get('author').casefold() == author.casefold()
    ]