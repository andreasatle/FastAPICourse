from jose import jwt
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from fastapicourse.tailwind.models import Users
from jose import jwt
from jose import jwt


class JWTToken:
    def __init__(self, jwt_secret_key: str = None, jwt_algorithm: str = None):
        load_dotenv()

        self.secret_key = os.getenv("JWT_SECRET_KEY", jwt_secret_key)
        self.algorithm = os.getenv("JWT_ALGORITHM", jwt_algorithm)

        if self.secret_key is None:
            raise ValueError("JWT_SECRET_KEY environment variable not set")
        if self.algorithm is None:
            raise ValueError("JWT_ALGORITHM environment variable not set")

    def encode(self, user: Users, tdelta: timedelta) -> str:
        payload = {
            "sub": user.username,
            "id": user.id,
            "exp": (datetime.utcnow() + tdelta).timestamp(),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode(self, token: str) -> dict:
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
