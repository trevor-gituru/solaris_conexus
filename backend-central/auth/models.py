# auth/models.py
from pydantic import BaseModel, EmailStr, constr

class RegisterRequest(BaseModel):
    username: constr(min_length=3, pattern=r'^\w+$')
    email: EmailStr
    password: constr(min_length=6)