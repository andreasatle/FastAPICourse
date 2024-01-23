from jose import jwt
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from fastapicourse.project_3 import models



class JWTToken:
    def __init__(self, jwt_secret_key: str = None, jwt_algorithm: str = None):
        load_dotenv()

        self.secret_key = os.getenv("JWT_SECRET_KEY", None)
        self.algorithm = os.getenv("JWT_ALGORITHM", None)

        if self.secret_key is None:
            raise ValueError("JWT_SECRET_KEY environment variable not set")
        if self.algorithm is None:
            raise ValueError("JWT_ALGORITHM environment variable not set")
        
    def create(self, user: models.Users, minutes: int) -> str:
        payload = {
            "sub": user.username,
            "id": user.id,
            "role": user.role,
            "exp": datetime.utcnow() + timedelta(minutes=minutes)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode(self, token: str) -> dict:
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
