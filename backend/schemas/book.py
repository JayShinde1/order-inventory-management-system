from typing import Annotated, Optional
from pydantic import BaseModel, Field


class Book(BaseModel):
    title: Annotated[str, Field(..., title = 'Title', description = 'Title of the book.')]
    author: Annotated[str, Field(..., title = 'Author', description = 'Author of the book.')]
    domain: Annotated[str, Field(..., title = 'Domain', description = 'Domain of the book.')]
    price: Annotated[int, Field(..., title = 'Price', description = 'Price of the book.')]
    stock_quantity: Annotated[int, Field(..., title = 'Stock Quantity', description = 'Quantity avaliable in stock.')]


class updateBook(BaseModel):
    title: Annotated[str, Field(Optional, title = 'Title', description = 'Title of the book.')]
    author: Annotated[str, Field(Optional, title = 'Author', description = 'Author of the book.')]
    domain: Annotated[str, Field(Optional, title = 'Domain', description = 'Domain of the book.')]
    price: Annotated[int, Field(Optional, title = 'Price', description = 'Price of the book.')]
    stock_quantity: Annotated[int, Field(Optional, title = 'Stock Quantity', description = 'Quantity avaliable in stock.')]

