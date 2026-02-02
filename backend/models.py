from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func, Date
from datetime import datetime

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True, index = True, nullable = False)
    email = Column(String, unique = True)
    username = Column(String, unique = True, nullable = False)
    hashed_password = Column(String, nullable = False)
    role = Column(String)
    is_active = Column(Boolean, default = True)
    created_at = Column(DateTime(timezone = True), server_default = func.now(), nullable = False)



class Books(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key = True, index = True)
    title = Column(String, nullable = False)
    author = Column(String, nullable = False)
    domain = Column(String)
    price = Column(Integer, nullable = False)
    stock_quantity = Column(Integer, nullable = False)
    created_at = Column(DateTime(timezone = True), server_default = func.now(), nullable = False)



class Orders(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable = False)
    quantity = Column(Integer, nullable = False)
    price_at_purchase = Column(Integer, nullable = False)
    status = Column(String, nullable = False, default = "PLACED")
    created_at = Column(DateTime(timezone = True), server_default = func.now(), nullable = False)


class Sales(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key = True, index = True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable = False)
    quantity = Column(Integer, nullable = False)
    price_at_sale = Column(Integer, nullable = False)
    domain = Column(String, nullable = False)
    sale_date = Column(Date, nullable = False)
    created_at = Column(DateTime(timezone = True), server_default = func.now(), nullable = False)


class HistoricalSales(Base):
    __tablename__ = "historical_sales"

    id = Column(Integer, primary_key = True, index = True)
    domain = Column(String, nullable = False)
    quantity = Column(Integer, nullable = False)
    sale_date = Column(Date, nullable = False)
