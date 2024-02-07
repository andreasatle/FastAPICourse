import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from fastapicourse.tailwind.main import app
from fastapicourse.tailwind.routes.auth import CreateUserRequest, get_current_user
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

def get_admin_user():
    db = TestingSessionLocal()
    user = db.query(Users).filter(Users.username == "Arne").first()
    return user

def get_not_admin_user():
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
    admin_user = get_admin_user()
    not_admin_user = get_not_admin_user()

    todo1 = Todos(
        id=1,
        title = "Todo1",
        description = "This is a test todo 1",
        priority = 1,
        completed = False,
        owner_id=not_admin_user.id
    )

    todo2 = Todos(
        id=2,
        title = "Todo2",
        description = "This is a test todo 2",
        priority = 2,
        completed = True,
        owner_id=not_admin_user.id
    )

    todo3 = Todos(
        id=3,
        title = "Todo3",
        description = "This is a test todo 3",
        priority = 3,
        completed = False,
        owner_id=admin_user.id
    )

    todo4 = Todos(
        id=4,
        title = "Todo4",
        description = "This is a test todo 4",
        priority = 4,
        completed = True,
        owner_id=admin_user.id
    )

    db = TestingSessionLocal()
    db.add(todo1)
    db.add(todo2)
    db.add(todo3)
    db.add(todo4)
    db.commit()
    db.close()


def clear_tables():
    with engine.connect() as conn:
        conn.execute(text('DELETE FROM todos;'))
        conn.execute(text('DELETE FROM users;'))
        conn.commit()

@pytest.fixture
def setup_test_db_admin():
    app.dependency_overrides[get_current_user] = get_admin_user

    create_user()
    create_todos()

    yield

    clear_tables()

@pytest.fixture
def setup_test_db_not_admin():
    app.dependency_overrides[get_current_user] = get_not_admin_user

    create_user()
    create_todos()

    yield

    clear_tables()

# Create a test client using the FastAPI app
client = TestClient(app)

# Use the test database, rather than the production one.
app.dependency_overrides[get_db] = override_get_db

# I just want to use the get_current_user function from the routes.auth module.
# Otherwise the linter complains. This should be set in each test module.
app.dependency_overrides[get_current_user] = get_current_user
