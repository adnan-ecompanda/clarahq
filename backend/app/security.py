import hashlib
import time
import jwt

SECRET_KEY = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET"
ALGO = "HS256"


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hash_value: str) -> bool:
    return hash_password(password) == hash_value


def create_token(user_id: int, role: str):
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": int(time.time()) + 60*60*24  # 24 hours
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGO)