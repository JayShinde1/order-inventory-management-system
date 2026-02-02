from fastapi import APIRouter, HTTPException, Depends, Path, Query, Body
from starlette import status
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from database import Session_local, engine
from models import Books, Users, Orders, Sales
from schemas.book import Book, updateBook
from routers.auth import get_current_user, user_dependency
from database import db_dependency
from datetime import datetime, timezone


router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

class UpdateOrderStatus(BaseModel):
    status: str


@router.post('/', status_code=status.HTTP_201_CREATED)
def add_book(new_book : Book, db: db_dependency, user: user_dependency):
    db_user = db.query(Users).filter(Users.id == user["id"]).first()

    if db_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, detail = "Admin privilages are required")
    
    book_model = Books(**new_book.model_dump())
    db.add(book_model)
    db.commit()
    db.refresh(book_model)

    return book_model




@router.put('/{book_id}', status_code = status.HTTP_200_OK)
def update_book(user: user_dependency, db: db_dependency, updated_book : Book, book_id: int):
    db_user = db.query(Users).filter(Users.id == user["id"]).first()

    if db_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, detail = "Admin privilages are required")

    book_model = db.query(Books).filter(Books.id == book_id).first()
    if not book_model:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book ID not found.")

    book_model.title = updated_book.title
    book_model.author = updated_book.author
    book_model.domain = updated_book.domain
    book_model.price = updated_book.price
    book_model.stock_quantity = updated_book.stock_quantity
    db.commit()
        
        

@router.patch("/{book_id}", status_code = status.HTTP_200_OK)
def patch_book(user: user_dependency, db: db_dependency, book_id: int, updated_book: updateBook):
    db_user = db.query(Users).filter(Users.id == user["id"]).first()

    if db_user.role != "admin":
        raise HTTPException(status_code = status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, detail = "Admin privilages are required")

    book_model = db.query(Books).filter(Books.id == book_id).first()
    if not book_model:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Book not found.")

    update_data = updated_book.model_dump(exclude_unset = True)

    for field, value in update_data.items():
        setattr(book_model, field, value)

    db.commit()
    db.refresh(book_model)
    return book_model



@router.delete('/{book_id}', status_code = status.HTTP_204_NO_CONTENT)
def delete_book(user: user_dependency, db: db_dependency, book_id: int):
    if user.get('role') != 'admin' and not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")

    book_model = db.query(Books).filter(Books.id == book_id).first()
    if not book_model:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Book not found.")
    
    db.delete(book_model)
    db.commit()



@router.get('/get-all-orders', status_code=status.HTTP_200_OK)
async def get_my_orders(user: user_dependency, db: db_dependency):
    if user.get('role') != 'admin' and not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    
    user_order = db.query(Orders).all()
    return user_order



@router.patch("/orders/{order_id}/status", status_code=status.HTTP_200_OK)
async def update_status(user: user_dependency, update_status: UpdateOrderStatus, db: db_dependency, order_id: int):

    db_user =  db.query(Users).filter(Users.id == user['id']).first()
    if db_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin privilages are required")
    
    valid_statuses = ['PLACED', 'CANCELLED', 'CONFIRMED', 'SHIPPED', 'DELIVERED']
    new_status = update_status.status
    if new_status not in valid_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order status")
    
    allowed_transitions = {
        "PLACED": {"CONFIRMED", "CANCELLED"},
        "CONFIRMED":{"SHIPPED", "CANCELLED"},
        "SHIPPED": {"DELIVERED"},
        "CANCELLED": set(),
        "DELIVERED": set()
    }

    req_order = db.query(Orders).filter(Orders.id == order_id).first()
    if not req_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    current_status = req_order.status

    if current_status not in allowed_transitions:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invalid order status transition")
    
    allowed_next = allowed_transitions[current_status]

    if new_status not in allowed_next:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invalid order status transition")
    
    if new_status == "CANCELLED":
        fetched_book = db.query(Books).filter(Books.id == req_order.book_id).first()
        if not fetched_book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Book not found")
        fetched_book.stock_quantity += req_order.quantity
    
    if new_status == "DELIVERED":

        fetched_book = db.query(Books).filter(Books.id == req_order.book_id).first()
        if not fetched_book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

        sale_model = Sales(
            book_id = fetched_book.id,
            quantity = req_order.quantity,
            price_at_sale = req_order.price_at_purchase,
            domain = fetched_book.domain,
            sale_date = datetime.now(timezone.utc).date()
        )
        
        db.add(sale_model)


    req_order.status = new_status
    db.commit()
    db.refresh(req_order)
    return {"message": "Order status updated successfully", "order_id": req_order.id, "status": req_order.status}
