from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: str = Field(default = "customer")


class Token(BaseModel):
    access_token: str
    token_type: str