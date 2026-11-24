import os 
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv() #loaded .env file

DATABASE_URL = os.getenv("DATABASE_URL") #get the DATABASE_URL from .env file 

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set .env file")

engine = create_engine(DATABASE_URL) #creates the engine and connection pool

SessionLocal = sessionmaker(
    bind=engine,
    autocommit = False,
    autoflush=False,
    expire_on_commit=False,
    ) #it creates db sessions using the engine


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

