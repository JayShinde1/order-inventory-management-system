from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from database import Session_local
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer 
from jose import JWTError, jwt
from datetime import timedelta, timezone, datetime
from database import db_dependency
from schemas.user import CreateUserRequest, Token


router = APIRouter()


#command to generate a random secret-key: openssl rand -hex 32
SECRET_KEY = 'b04b071d127fde3262128e3468fca276e7dfc71c33b2de063bf068e826c8d93f'
ALGORITHM = 'HS256' 


bcrypt_context = CryptContext(schemes = ['bcrypt'], deprecated = 'auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl = '/login')


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user
    

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta 
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm = ALGORITHM) 


async def get_current_user(token:Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Could not validate user.")
        return {'username':username, 'id':user_id}
    except JWTError:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Could not validate user.")
        

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/create-user", status_code = status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):

    existing_user = db.query(Users).filter(Users.username == create_user_request.username).first()
    if existing_user:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Username already exists")

    create_user_request = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        role = create_user_request.role,
        is_active = True
    )
    db.add(create_user_request)
    db.commit()
    db.refresh(create_user_request)
    return {"message": "User created successfully"}



@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid username or password!")
    token = create_access_token(user.username, user.id, timedelta(minutes = 20))
    return {'access_token': token, 'token_type': 'bearer'}



@router.get('/get-details', status_code = status.HTTP_200_OK)
async def get_user_details(user: user_dependency, db: db_dependency):
    verify = (db.query(Users).filter(Users.id == user["id"]).first())
    if not verify:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")
    return verify


