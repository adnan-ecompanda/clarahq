from fastapi import APIRouter, HTTPException
from ..schemas_user import UserCreate, UserOut, LoginInput, TokenOut
from ..security import verify_password, create_token
from .. import schemas, crud_user


router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut)
def create_user(payload: UserCreate):
    return crud_user.create_user(payload)


@router.post("/login")
def login(payload: schemas.UserLogin):
    user = crud_user.get_user_by_email(payload.email)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Compare password
    stored_hash = user["password_hash"]
    if not verify_password(payload.password, stored_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create JWT token
    token = create_token(user["id"], user["role"])

    return {
        "access_token": token,
        "token_type": "bearer"
    }