import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from fastapicourse.tailwind.main import app
from fastapicourse.tailwind.routes.auth import get_current_user, CreateUserRequest
from dotenv import load_dotenv
from fastapicourse.tailwind.models import Users, Todos
from sqlalchemy.orm import sessionmaker
from fastapicourse.tailwind.database import Base, get_db
from fastapi.testclient import TestClient
import pytest


load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

# Setting up the tesing database
engine = create_engine(TEST_DATABASE_URL, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    db = TestingSessionLocal()
    user = db.query(Users).filter(Users.username == "Sven").first()
    return user

def create_user():
    user_request1 = CreateUserRequest(
        username = "Sven",
        email = "sven@svenson.com",
        first_name = "Sven",
        last_name = "Svenson",
        phone_number = "123-456-7890",
        password = "qwe123",
        is_active = True,
        role = None
    )
    user_request2 = CreateUserRequest(
        username = "Arne",
        email = "arne@arneson.com",
        first_name = "Arne",
        last_name = "Arneson",
        phone_number = "321-654-9876",
        password = "123ewq",
        is_active = False,
        role = "admin"
    )

    user1 = Users(**user_request1.model_dump(),id=1)
    user2 = Users(**user_request2.model_dump(),id=2)
    db = TestingSessionLocal()
    db.add(user1)
    db.add(user2)
    db.commit()
    db.close()

def create_todos():
    user = override_get_current_user()

    todo1 = Todos(
        id=1,
        title = "Todo1",
        description = "This is a test todo 1",
        priority = 1,
        completed = False,
        owner_id=user.id
    )

    todo2 = Todos(
        id=2,
        title = "Todo2",
        description = "This is a test todo 2",
        priority = 2,
        completed = True,
        owner_id=user.id
    )

    db = TestingSessionLocal()
    db.add(todo1)
    db.add(todo2)
    db.commit()

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def clear_tables():
    with engine.connect() as conn:
        conn.execute(text('DELETE FROM todos;'))
        conn.execute(text('DELETE FROM users;'))
        conn.commit()

@pytest.fixture
def setup_db_todo():
    create_user()
    create_todos()

    yield

    clear_tables()

client = TestClient(app)

def test_get_todos(setup_db_todo):
    user = override_get_current_user()
    assert user.id is not None, 'User should have an id'

    response = client.get("/todos")
    assert response.status_code == 200, 'status code should be 200'
    todos = response.json()
    assert len(todos) == 2, 'There should be 2 todos'

    assert todos[0].get('title') == 'Todo1'
    assert todos[0].get('description') == "This is a test todo 1"
    assert todos[0].get('priority') == 1
    assert todos[0].get('completed') == False
    assert todos[0].get('owner_id') == user.id

    assert todos[1].get('title') == 'Todo2'
    assert todos[1].get('description') == "This is a test todo 2"
    assert todos[1].get('priority') == 2
    assert todos[1].get('completed') == True
    assert todos[1].get('owner_id') == user.id


def test_get_one_todo(setup_db_todo):
    user = override_get_current_user()
    assert user.id is not None, 'User should have an id'

    response = client.get("/todos/1")

    assert response.status_code == 200, 'status code should be 200'
    todo = response.json()
    assert todo.get('title') == 'Todo1'
    assert todo.get('description') == "This is a test todo 1"
    assert todo.get('priority') == 1
    assert todo.get('completed') == False
    assert todo.get('owner_id') == user.id

    response = client.get("/todos/2")

    assert response.status_code == 200, 'status code should be 200'
    todo = response.json()
    assert todo.get('title') == 'Todo2'
    assert todo.get('description') == "This is a test todo 2"
    assert todo.get('priority') == 2
    assert todo.get('completed') == True
    assert todo.get('owner_id') == user.id

    response = client.get("/todos/3")
    assert response.status_code == 404, 'status code should be 404'
    assert response.json().get('detail') == 'Todo with id 3 not found'

def test_create_todo(setup_db_todo):
    user = override_get_current_user()
    assert user.id is not None, 'User should have an id'

    response = client.post("/todos/create", json={
        "title": "Todo3",
        "description": "This is a test todo 3",
        "priority": 3,
        "completed": False,
        "owner_id": user.id
    })

    assert response.status_code == 201, 'status code should be 201'
    db = TestingSessionLocal()
    todo = db.query(Todos).filter(Todos.title == "Todo3").first()
    db.close()

    assert todo.title == 'Todo3'
    assert todo.description == "This is a test todo 3"
    assert todo.priority == 3
    assert todo.completed == False
    assert todo.owner_id == user.id

    response = client.get("/todos")
    assert response.status_code == 200, 'status code should be 200'
    todos = response.json()
    assert len(todos) == 3, 'There should be 3 todos'

def test_update_todo(setup_db_todo):
    user = override_get_current_user()

    assert user.id is not None, 'User should have an id'

    db = TestingSessionLocal()
    assert db.query(Todos).count() == 2, 'There should be 2 todos before the update'
    db.close()

    response = client.put("/todos/update/2", json={
        "title": "Todo3",
        "description": "This is a test todo 3",
        "priority": 3,
        "completed": False,
        "owner_id": user.id
    })
    assert response.status_code == 204, 'status code should be 204'

    db = TestingSessionLocal()
    assert db.query(Todos).count() == 2, 'There should be 2 todos after the update'
    todo = db.query(Todos).filter(Todos.id == 2).first()
    db.close()

    assert todo.title == 'Todo3'
    assert todo.description == "This is a test todo 3"
    assert todo.priority == 3
    assert todo.completed == False
    assert todo.owner_id == user.id

