from fastapi import FastAPI
import models
from database import engine
from routers import books, auth, admin, orders

app = FastAPI()

@app.get('/')
def health_check():
    return {'status':'OK'}

models.Base.metadata.create_all(bind = engine)
app.include_router(books.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(orders.router)