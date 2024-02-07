from fastapi import APIRouter, HTTPException
from starlette import status
from fastapicourse.project_3 import models
from fastapicourse.project_3 import jwt_tokens
from fastapicourse.project_3 import database
from fastapicourse.project_3 import types
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapicourse.project_3.database import SessionDep
from jose.exceptions import JWTError

router = APIRouter(prefix="/auth", tags=["auth"])

jwt_token = jwt_tokens.JWTToken()


def authenticate_user(
    username: str, password: str, db: SessionDep
) -> models.Users | None:
    user = db.query(models.Users).filter(models.Users.username == username).first()
    if (user is not None) and (
        types.bcrypt_context.verify(password, user.hashed_password)
    ):
        return user
    else:
        return None


async def get_current_user(token: types.OAuthBearerDep, db: SessionDep):
    try:
        # Decode the token
        payload = jwt_token.decode(token)

        # Get the user from the token payload
        user_name = payload.get("sub")
        user_id = payload.get("id")
        user_role = payload.get("role")

        # Validate that the user exists
        if user_name is None or user_id is None or user_role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user",
            )

        return db.query(models.Users).filter(models.Users.id == user_id).first()

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user"
        )


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(user_request: types.UserRequest, db: SessionDep):
    user = models.Users(**user_request.model_dump())

    # Validate that the username does not already exist
    db_user = (
        db.query(models.Users).filter(models.Users.username == user.username).first()
    )
    if db_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with username '{user.username}' already exists",
        )

    # Validate that the email does not already exist
    db_user = db.query(models.Users).filter(models.Users.email == user.email).first()
    if db_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{user.email}' already exists",
        )

    db.add(user)
    db.commit()


@router.post("/token", status_code=status.HTTP_200_OK)
async def login_user(form_data: types.AuthDep, db: SessionDep):
    user = authenticate_user(form_data.username, form_data.password, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return types.Token(access_token=jwt_token.create(user, 30)).model_dump()
