from fastapicourse.project_3 import database
from typing import Annotated
from fastapi import Depends
from pydantic import BaseModel, Field, field_validator
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

AuthDep = Annotated[OAuth2PasswordRequestForm, Depends()]
OAuthBearerDep = Annotated[str, Depends(oauth_bearer)]

IdType = Annotated[int, Field(gt=0)]

TitleType = Annotated[str, Field(min_length=3, max_length=50)]
DescriptionType = Annotated[str, Field(min_length=3, max_length=100)]
PriorityType = Annotated[int, Field(ge=1, le=5)]
CompletedType = Annotated[bool, Field(default=False)]

EmailType = Annotated[str, Field(min_length=3, max_length=50)]
UsernameType = Annotated[str, Field(min_length=3, max_length=50)]
FirstnameType = Annotated[str, Field(min_length=1, max_length=50)]
LastnameType = Annotated[str, Field(min_length=1, max_length=50)]
PhoneNumberType = Annotated[str, Field(min_length=3, max_length=20)]
PasswordType = Annotated[str, Field(min_length=3, max_length=64, alias="password")]
UnaliasPasswordType = Annotated[str, Field(min_length=3, max_length=64)]
IsActiveType = Annotated[bool, Field(default=False)]
RoleType = Annotated[str, Field(min_length=3, max_length=50)]


class TodoRequest(BaseModel):
    title: TitleType
    description: DescriptionType
    priority: PriorityType
    completed: CompletedType

    class Config:
        json_schema_extra = {
            "example": {
                "title": "This is my ToDo",
                "description": "This is my description of my ToDo",
                "priority": 3,
                "completed": False,
            }
        }


class UserRequest(BaseModel):
    username: UsernameType
    email: EmailType
    first_name: FirstnameType
    last_name: LastnameType
    phone_number: PhoneNumberType
    hashed_password: PasswordType
    is_active: IsActiveType
    role: RoleType

    class Config:
        by_alias = True
        json_schema_extra = {
            "example": {
                "username": "This is my username",
                "email": "my.email@example.com",
                "first_name": "My first name",
                "last_name": "My last name",
                "phone_number": "123-4567-8901",
                "password": "qwe123",
                "is_active": True,
                "role": "admin",
            }
        }

    @field_validator("hashed_password")
    @classmethod
    def hash_password(cls, password: PasswordType) -> PasswordType:
        return bcrypt_context.hash(password)


class PasswordRequest(BaseModel):
    old_password: UnaliasPasswordType
    new_password: UnaliasPasswordType

    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "old password",
                "new_password": "new password",
            }
        }


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
