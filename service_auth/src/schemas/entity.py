import re

from uuid import UUID
from pydantic import BaseModel, EmailStr, validator, Field
from pydantic.class_validators import root_validator
from datetime import datetime


def validate_password(cls, values: dict):
    passwd = values.get('password', None)
    if not passwd:
        raise ValueError('The password is None')
    password_length = len(values['password'])
    if password_length < 8:
        raise ValueError('The password must be between 8 long')
    if not re.search('[A-Z]', passwd):
        raise ValueError('The password must be have one upper letter')
    if not re.search('[a-z]', passwd):
        raise ValueError('The password must be have one lower letter')
    if not re.search('[0-9]', passwd):
        raise ValueError('The password must be have one digit')
    return values


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

    # validators
    _password_validator = root_validator(allow_reuse=True)(validate_password)

    @validator('first_name', each_item=False)
    @classmethod
    def first_name_contains_only_letters(cls, value):
        if not value.isalpha():
            raise ValueError(
                'The first name must contain only alphabethical symbols'
            )
        return value

    @validator('last_name', each_item=False)
    @classmethod
    def last_name_contains_only_letters(cls, value):
        if not value.isalpha():
            raise ValueError(
                'The last name must contain only alphabethical symbols'
            )
        return value

    class Config:
        orm_mode = True


class UserInDB(BaseModel):
    id: UUID
    email: str

    class Config:
        orm_mode = True


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str
    set_cookie: bool = False

    _password_validator = root_validator(allow_reuse=True)(validate_password)

    class Config:
        orm_mode = True


class Roles(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True


class Status(BaseModel):
    status: str

    class Config:
        orm_mode = True


class ShemaAccountHistory(BaseModel):
    user_agent: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True


class ChangePassword(BaseModel):
    current_password: str
    password: str
    repeat_password: str

    # validators
    _password_validator = root_validator(allow_reuse=True)(validate_password)
