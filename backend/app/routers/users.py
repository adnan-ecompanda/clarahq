from fastapi import APIRouter, HTTPException
from ..schemas_user import UserCreate, UserOut, LoginInput, TokenOut
from .. import crud_user
from ..security import verify_password, create_token

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut)
def create_user(payload: UserCreate):
    return crud_user.create_user(payload)


@router.post("/login", response_model=TokenOut)
def login(payload: LoginInput):
    user = crud_user.get_user_by_email(payload.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid login")

    stored_hash = crud_user.get_user_by_email(payload.email).password_hash
    if not verify_password(payload.password, stored_hash):
        raise HTTPException(status_code=401, detail="Invalid login")

    token = create_token(user.id, user.role)
    return TokenOut(access_token=token)