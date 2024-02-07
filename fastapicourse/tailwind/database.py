from fastapi import Depends
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from typing import Annotated

# The start of any SQLAlchemy application is an object called the Engine.
# This object acts as a central source of connections to a particular database,
# providing both a factory as well as a holding space called a connection pool
# for these database connections. The engine is typically a global object created
# just once for a particular database server, and is configured using a URL string
# which will describe how it should connect to the database host or backend.

# Create the DB engine
load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

# Configure a local session using the DB engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for the DB models
Base = declarative_base()


# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency to get the DB session
SessionDep = Annotated[Session, Depends(get_db)]
