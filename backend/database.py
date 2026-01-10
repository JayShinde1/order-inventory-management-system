from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Annotated
from fastapi import Depends

SQLALCHEMY_DATABASE_URL = 'sqlite:///./books.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread':False})

Session_local = sessionmaker(autoflush=False, autocommit=False, bind=engine)

def get_db():
    db = Session_local()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]