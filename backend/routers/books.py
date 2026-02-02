from fastapi import APIRouter, HTTPException, Depends, Path, Query, Body
from starlette import status
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from database import Session_local, engine
from models import Books, Users, Orders
from schemas.book import Book, updateBook
from database import db_dependency
from sqlalchemy import select
from sqlalchemy.orm import session
import math
from services.ai_search import AISearch, chain


router = APIRouter(
    prefix='/public',
    tags = ['books']
)

    
class AISearchRequest(BaseModel):
    query: str
    page: int = 1
    page_size: int = 10




@router.get('/', status_code = status.HTTP_200_OK)
def get_books(
    db: db_dependency, page: int = Query(default=1, ge=1), page_size: int = Query(default=10, ge=1, le=50),
    domain: str | None = Query(default=None), max_price: int | None = Query(default=None, ge=0),
    sort_by: str | None = Query(default="id"), order: str = Query(default="asc")):
    
    offset = (page - 1) * page_size
    query = db.query(Books)

    if domain:
        query = query.filter(Books.domain.ilike(f"%{domain}%"))
    
    if max_price is not None:
        query = query.filter(Books.price <= max_price)
    
    #sorting
    allowed_sorting_fields = {
        "id": Books.id,
        "price": Books.price,
        "title": Books.title, 
        "created_at": Books.created_at
    }

    if sort_by not in allowed_sorting_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid sort_by field. Allowed: {list(allowed_sorting_fields.keys())}")

    sort_column = allowed_sorting_fields[sort_by]

    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())


    total_items = db.query(Books).count()
    total_pages = math.ceil(total_items/ page_size)
    items = (query.order_by(Books.id).limit(page_size).offset(offset).all())
    return {'current page':page, 'page_size':page_size, 'total_items':total_items, 'total_pages':total_pages, 'items':items}

    

@router.get('/{book_id}', status_code = status.HTTP_200_OK)
def get_book( db: db_dependency, book_id: int = Path(..., description = "Enter the id of the book which you want to fetch.", ge = 1)):
    book_model = db.query(Books).filter(Books.id == book_id).first()
    if not book_model:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not found.")
    return book_model
    


@router.get('/search/', status_code = status.HTTP_200_OK)
def search_book(db: db_dependency, domain: str = Query(..., description = "Enter the domain of the book.")):
    book_model = db.query(Books).filter(Books.domain.ilike(f"%{domain}%")).all()
    if not book_model:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not found.")
    return book_model
    

# @router.get('/{domain}', status_code = status.HTTP_200_OK)
# def get_books_in_budget(db: db_dependency, max_price: int = Query(..., description = 'Enter your budget to buy the domain specific books.', ge = 0), domain: str = Path(..., description = 'Enter the domain.'), 
#                         page: int = Query(default = 1, ge = 1), page_size: int = Query(default = 10, ge = 1, le = 50)):
#     offset = (page - 1) * page_size
#     filtered_items = db.query(Books).filter(Books.domain == domain).filter(Books.price < max_price).all()

#     if not filtered_items:
#         raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not available in your budget or invalid domain.")    
    
#     total_items = filtered_items.count()
    
#     total_pages = math.ceil(total_items/ page_size)
#     filtered_items = filtered_items.order_by(Books).limit(page_size).offset(offset).all()

#     return {'current_page':page, 'page_size':page_size, 'total_items':total_items, 'total_pages':total_pages, 'filtered_items':filtered_items}


#AI Search
def validate_and_forward_output(db, filters: AISearch, page: int, page_size: int):
    query = db.query(Books)

    if filters.domain:
        query = query.filter(Books.domain.ilike(f"%{filters.domain}%"))
    
    if filters.max_price is not None:
        query = query.filter(Books.price <= filters.max_price)

    if filters.sort_by:
        column = getattr(Books, filters.sort_by)

        if filters.order == "desc":
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())
    
    else:
        query = query.order_by(Books.id.asc())

    total_items = query.count()
    total_pages = math.ceil(total_items/ page_size)
    offset = (page - 1) * page_size

    results = query.offset(offset).limit(page_size).all()
    return {'current_page':page, 'page_size':page_size, 'total_items':total_items, 'total_pages':total_pages, 'results':results}



@router.post('/ai-search', status_code = status.HTTP_201_CREATED)
def search_using_ai(request: AISearchRequest, db: db_dependency):
    try:
        filters: AISearch = chain.invoke({"query": request.query})

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"AI parsing failed: {str(e)}")
    
    print(filters.domain, filters.max_price, filters.sort_by, filters.order)

    return validate_and_forward_output(db=db, filters=filters, page=request.page, page_size=request.page_size)
