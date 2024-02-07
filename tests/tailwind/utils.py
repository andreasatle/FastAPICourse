import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from fastapicourse.tailwind.main import app
from fastapicourse.tailwind.routes.auth import CreateUserRequest
from dotenv import load_dotenv
from fastapicourse.tailwind.models import Users, Todos
from sqlalchemy.orm import sessionmaker
from fastapicourse.tailwind.database import Base
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
    db.close()


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
