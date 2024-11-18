from pydantic import BaseModel,  Field, EmailStr, validator
from typing import Optional, List
from fastapi import UploadFile, File
from datetime import date, datetime
from enum import Enum
from sqlalchemy import JSON
import re


######################################## User logiin and register #############################
class LoginInput(BaseModel):
    email: str
    user_password: str


class ChangePassword(BaseModel):
    current_password: str
    new_password: str

    class Config:
        from_attributes = True


class UserType(str, Enum):
    admin = "admin"
    user = "user"
    worker = "worker"
   
   
class UserCreate(BaseModel):
    user_name: str
    user_email: str
    user_password: str
    user_type: UserType = UserType.user
    phone_no: str

    class Config:
        from_attributes = True


class UpdateUser(BaseModel):
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    phone_no: Optional[int] = None
    user_type: Optional[str] = None
    current_password: Optional[str] = None

################################### add material name ###########################

class MaterialCreateSchema(BaseModel):
    name: str
    quantity: int
    description: Optional[str] = None

    class Config:
        orm_mode = True
    
################################### add material name ###########################

class SiteCreateSchema(BaseModel):
    site_name: str
    site_address: str
    

    class Config:
        orm_mode = True

################################## add material name ###########################

class vendorCreateSchema(BaseModel):
    name: str
    contact: int
    email: str
    

    class Config:
        orm_mode = True


