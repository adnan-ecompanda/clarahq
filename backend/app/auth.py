from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer
from jose import jwt, JWTError

from .security import SECRET_KEY, ALGO
from .crud_user import get_user

reusable_oauth2 = HTTPBearer()


def get_current_user(credentials=Depends(reusable_oauth2)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
        user_id = int(payload.get("sub"))
        role = payload.get("role")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = get_user(user_id)
    if not user or user.active is False:
        raise HTTPException(status_code=401, detail="User inactive or not found")

    return {"id": user_id, "role": role}


def require_roles(*allowed_roles):
    def checker(current_user=Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission for this action"
            )
        return current_user
    return checker