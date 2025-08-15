from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from datetime import datetime, timedelta, timezone

from app.db.database import get_db
from app.db.models import User, OTPVerification
from app.db.schemas import UserCreate, UserOut, UserLogin
from app.utils.security import get_password_hash, authenticate_user, create_access_token, create_refresh_token
from app.utils.otp import send_otp

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

@router.post("/otp/request", status_code=status.HTTP_200_OK)
async def request_otp(
    user_email: str,
    db: AsyncSession = Depends(get_db)
):
    user = await db.execute(select(User).where(User.email == user_email))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # In a real app, use a proper OTP service
    otp_code = await send_otp(db, user.phone)

    # Store OTP in database
    otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10) # OTP expires in 10 minutes
    db_otp = OTPVerification(
        user_id=user.user_id,
        otp_code=str(otp_code),
        expires_at=otp_expires_at
    )
    db.add(db_otp)
    await db.commit()
    await db.refresh(db_otp)

    return {"message": "OTP sent successfully"}

@router.post("/otp/verify", status_code=status.HTTP_200_OK)
async def verify_otp(
    user_email: str,
    otp_code: str,
    db: AsyncSession = Depends(get_db)
):
    user = await db.execute(select(User).where(User.email == user_email))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    otp_verification = await db.execute(
        select(OTPVerification).where(
            OTPVerification.user_id == user.user_id,
            OTPVerification.otp_code == otp_code,
            OTPVerification.verified == False,
            OTPVerification.expires_at > datetime.now(timezone.utc)
        )
    )
    otp_verification = otp_verification.scalar_one_or_none()
    if not otp_verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

    # Mark OTP as verified and update user status
    otp_verification.verified = True
    user.is_phone_verified = True
    await db.commit()
    await db.refresh(user)

    return {"message": "Phone number verified successfully"}