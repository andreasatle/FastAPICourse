"""
This code is a part of a Python module called database.py that is responsible for setting up a database connection using SQLAlchemy, a popular Python library for working with databases.

Let's go through the code step by step:

The code begins by importing necessary modules:

create_engine from sqlalchemy module: This function is used to create a database engine, which is responsible for managing the connection to the database.
declarative_base from sqlalchemy.ext.declarative module: This function is used to create a base class for declarative class definitions. It allows us to define database models as Python classes.
load_dotenv from dotenv module: This function is used to load environment variables from a .env file. Environment variables are used to store sensitive information like database credentials.
The load_dotenv() function is called to load environment variables from the .env file. This file should be present in the same directory as the database.py file and contain the necessary database configuration variables.

The code defines several variables (DB_BASE, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME) that store the values of the corresponding environment variables. These variables are used to construct the database URL.

The DB_URL variable is created by concatenating the values of the above variables in a specific format. This URL will be used by SQLAlchemy to connect to the database.

The engine variable is created by calling the create_engine() function with the DB_URL as an argument. This sets up the database engine using the provided URL.

The SessionLocal variable is created by calling the sessionmaker() function with some additional arguments (autocommit=False, autoflush=False, bind=engine). This function creates a session factory that will be used to create individual database sessions.

The Base variable is created by calling the declarative_base() function. This creates a base class for declarative class definitions. Any database models will inherit from this base class.

The get_db() function is defined. This function is a generator function that yields a database session. It is used as a dependency for other functions that need a database session. The yield keyword allows the function to be used as a context manager, ensuring that the session is properly closed after it is used.

Finally, the DBSession variable is defined as an annotation [Annotated[Session, Depends(get_db)]]. This is likely a type hint indicating that the DBSession variable is of type Session and depends on the get_db() function to provide the session.

Overall, this code sets up the database connection and provides a way to obtain a database session when needed. The DBSession variable can be used in other parts of the code to access the database session and perform database operations.
"""

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
from sqlalchemy.orm import Session, sessionmaker
from typing import Annotated


load_dotenv()

DB_DRIVER = os.getenv("DB_DRIVER")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SessionDep = Annotated[Session, Depends(get_db)]
