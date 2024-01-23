from fastapicourse.project_3.database import Base
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from fastapicourse.project_3 import types

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    email = Column(String(50), unique=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    hashed_password = Column(String(64))
    is_active = Column(Boolean, default=True)
    role = Column(String(50))

    def update_with(self, user_request: types.UserRequest):
        self.username = user_request.username
        self.email = user_request.email
        self.first_name = user_request.first_name
        self.last_name = user_request.last_name
        self.hashed_password = user_request.hashed_password
        self.is_active = user_request.is_active
        self.role = user_request.role

    def __str__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email}, first_name={self.first_name}, last_name={self.last_name}, hashed_password={self.hashed_password}, is_active={self.is_active}, role={self.role})"

class Todos(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50))
    description = Column(String(100))
    priority = Column(Integer)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    def update_with(self, todo_request: types.TodoRequest):
        self.title = todo_request.title
        self.description = todo_request.description
        self.priority = todo_request.priority
        self.completed = todo_request.completed

