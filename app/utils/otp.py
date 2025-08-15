from app.db.database import get_db
from app.db.models import User, OTPVerification
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy import select
from datetime import datetime, timezone

load_dotenv()



async def send_otp(db, phone: str):
    import random
    from twilio.rest import Client

    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    otp = random.randint(100000, 999999)

    message = client.messages.create(
        body=f"Your OTP code is {otp}",
        from_=TWILIO_PHONE_NUMBER,
        to=phone
    )

    return otp

async def verify_otp(db, user_id: str, otp_code: str):
    user = await User.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
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
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")   
    otp_verification.verified = True
    otp_verification.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "OTP verified successfully"}
    
    