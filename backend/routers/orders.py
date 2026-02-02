from fastapi import APIRouter, HTTPException, Depends, Path, Query, Body
from starlette import status
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from database import Session_local, engine
from models import Books, Users, Orders
from schemas.book import Book, updateBook
from routers.auth import get_current_user, user_dependency
from database import db_dependency


class CreateOrder(BaseModel):
    book_id: int = Field(..., description="Id of the book you want to puchase.")
    quantity: int = Field(..., description="Quantity of the book you want to purchase.")


router = APIRouter(
    prefix='/orders',
    tags = ['orders']
)

@router.post('/', status_code=status.HTTP_201_CREATED) 
def create_order(user: user_dependency, db: db_dependency, order_request: CreateOrder):
    
    # verify_user = db.query(Users).filter(Users.id == user.get('id')).first()
    # if not verify_user:
    #     raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Not Authenticated.")

    required_book = db.query(Books).filter(Books.id == order_request.book_id).first()
    if not required_book:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not found.")
    
    quantity_in_stock = required_book.stock_quantity
    if quantity_in_stock < order_request.quantity:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail = "Insufficient stock.")

    order_model = Orders(**order_request.model_dump(),
                        user_id = user.get('id'),
                        price_at_purchase = required_book.price)
    
    # reducing the stock in Books table
    required_book.stock_quantity -= order_request.quantity

    db.add(order_model)
    db.commit()
    db.refresh(order_model)

    return order_model
    


@router.get('/get-my-orders', status_code=status.HTTP_200_OK)
async def get_my_orders(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Not Authenticated.")
    
    user_order = db.query(Orders).filter(Orders.user_id == user.get('id')).all()
    
    return user_order

