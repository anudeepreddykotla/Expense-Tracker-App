from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import User
from app.db.schemas import UserCreate, UserOut, UserLogin
from app.utils.security import get_password_hash, authenticate_user, create_access_token, create_refresh_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check if user with email already exists
    existing_user_email = await db.execute(select(User).where(User.email == user.email))
    if existing_user_email.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if user with phone already exists
    existing_user_phone = await db.execute(select(User).where(User.phone == user.phone))
    if existing_user_phone.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )

    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        password_hash=hashed_password
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user

@router.post("/login", status_code=status.HTTP_200_OK)
async def login_for_access_token(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}