import os
import random
from datetime import datetime, timezone

from twilio.rest import Client
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, OTPVerification

load_dotenv()

async def send_otp(db: AsyncSession, phone: str):
    """
    Generates and sends an OTP to the specified phone number using Twilio.
    """
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    otp = random.randint(100000, 999999)

    # In a production app, you would handle the Twilio response and errors
    try:
        message = client.messages.create(
            body=f"Your OTP code is {otp}",
            from_=TWILIO_PHONE_NUMBER,
            to=phone
        )
        print(f"OTP message sent successfully with SID: {message.sid}")
    except Exception as e:
        print(f"Failed to send OTP message: {e}")
        # Depending on your app's logic, you might want to raise an HTTPException here
        # raise HTTPException(status_code=500, detail="Failed to send OTP")

    return otp

async def verify_otp(db: AsyncSession, user_id: str, otp_code: str):
    """
    Verifies the provided OTP code against the database.
    """
    otp_verification = await db.execute(
        select(OTPVerification).where(
            OTPVerification.user_id == user_id,
            OTPVerification.otp_code == otp_code,
            OTPVerification.verified == False,
            OTPVerification.expires_at > datetime.now(timezone.utc)
        )
    )
    otp_verification = otp_verification.scalar_one_or_none()
    if not otp_verification:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Mark OTP as verified and update user's phone verification status
    otp_verification.verified = True
    user = await User.get(db, user_id)
    if user:
        user.is_phone_verified = True
    
    await db.commit()
    await db.refresh(otp_verification)
    if user:
        await db.refresh(user)

    return {"message": "OTP verified successfully"}