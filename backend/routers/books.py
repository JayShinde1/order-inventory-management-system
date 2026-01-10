from fastapi import APIRouter, HTTPException, Depends, Path, Query, Body
from starlette import status
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from database import Session_local, engine
from models import Books, Users, Orders
from schemas.book import Book, updateBook
from routers.auth import get_current_user, user_dependency
from database import db_dependency


router = APIRouter(
    prefix='/public',
    tags = ['books']
)

    

@router.get('/', status_code = status.HTTP_200_OK)
def get_books(db: db_dependency):
    return db.query(Books).all()



@router.get('/{book_id}', status_code = status.HTTP_200_OK)
def get_book( db: db_dependency, book_id: int = Path(..., description = "Enter the id of the book which you want to fetch.", ge = 1)):
    book_model = db.query(Books).filter(Books.id == book_id).first()
    if not book_model:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not found.")
    return book_model
    


@router.get('/search/', status_code = status.HTTP_200_OK)
def search_book(db: db_dependency, domain: str = Query(..., description = "Enter the domain of the book.")):
    book_model = db.query(Books).filter(Books.domain == domain).all()
    if not book_model:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not found.")
    return book_model
    

@router.get('/domain/{domain}', status_code = status.HTTP_200_OK)
def get_books_in_budget(db: db_dependency, max_price: int = Query(..., description = 'Enter your budget to buy the domain specific books.', ge = 0), domain: str = Path(..., description = 'Enter the domain.')):
    book_model = db.query(Books).filter(Books.domain == domain).filter(Books.price < max_price).all()
    if not book_model:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not available in your budget or invalid domain.")    
    return book_model

