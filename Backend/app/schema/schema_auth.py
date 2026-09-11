from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional

class RegisterSchema(BaseModel):
    fullname: str
    username: str
    email: EmailStr
    password: str

class LoginSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str

    @model_validator(mode="before")
    @classmethod
    def check_username_email(cls, data: dict)-> dict:
        if not isinstance(data, dict):
            return data

        if not data.get("username") and not data.get("email"):
            raise ValueError("Username or email one field is required")

        return data

