from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime
from ..crud_portal_auth import SECRET_KEY, ALGORITHM

bearer = HTTPBearer()

def portal_current_patient(token: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        if payload["role"] != "patient_portal":
            raise HTTPException(status_code=403, detail="Invalid portal token")

        return payload  # contains patient_id, name, etc.

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")