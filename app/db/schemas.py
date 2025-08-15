import uuid
from pydantic import BaseModel, EmailStr, constr
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: constr(min_length=10, max_length=20)
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    user_id: uuid.UUID
    name: str
    email: EmailStr
    phone: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True