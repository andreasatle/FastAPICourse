from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from fastapicourse.tailwind.database import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    email = Column(String(50), unique=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone_number = Column(String(20))
    hashed_password = Column(String(60))
    is_active = Column(Boolean, default=True)
    role = Column(String(50), nullable=True)

    todos = relationship("Todos", back_populates="owner")

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

    owner = relationship("Users", back_populates="todos")

    def __str__(self):
        return f"Todo(id={self.id}, title={self.title}, description={self.description}, priority={self.priority}, completed={self.completed}, owner_id={self.owner_id})"