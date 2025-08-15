import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, UUID, VARCHAR, TIMESTAMP, TEXT, BOOLEAN, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        unique=True,
        comment="Unique user identifier"
    )

    name = Column(
        VARCHAR(100),
        nullable=False,
        comment="User's full name"
    )

    email = Column(
        VARCHAR(150),
        nullable=False,
        unique=True,
        comment="User's email address"
    )

    phone = Column(
        VARCHAR(20),
        nullable=False,
        unique=True,
        comment="User's mobile number with country code"
    )

    password_hash = Column(
        VARCHAR(256),
        nullable=False,
        comment="Hashed password"
    )

    is_phone_verified = Column(
        BOOLEAN,
        nullable=False,
        default=False,
        server_default="false",
        comment="Indicates if the phone number is verified"
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Account creation time"
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Last profile update time"
    )

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"
        
    @classmethod
    async def get(cls, db: AsyncSession, user_id: str):
        result = await db.execute(select(cls).where(cls.user_id == user_id))
        return result.scalar_one_or_none()

class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'
    token_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, comment="Unique token identifier")
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False, comment="Owner user ID")
    token = Column(TEXT, nullable=False, comment="Refresh token string")
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False, comment="Token expiry timestamp")
    revoked = Column(BOOLEAN, nullable=False, default=False, comment="Revocation status")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), comment="Creation time")
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now(), comment="Last update time")

    user = relationship("User", backref="refresh_tokens")

class FCMToken(Base):
    __tablename__ = 'fcm_tokens'
    fcm_token_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, comment="Unique token identifier")
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False, comment="Owner user ID")
    token = Column(TEXT, nullable=False, comment="Firebase Cloud Messaging token")
    device_info = Column(VARCHAR(255), nullable=True, comment="Optional device description")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), comment="Creation time")
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now(), comment="Last update time")

    user = relationship("User", backref="fcm_tokens")

class BankAccount(Base):
    __tablename__ = 'bank_accounts'
    account_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, comment="Unique bank account ID")
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False, comment="Owner user")
    bank_name = Column(VARCHAR(100), nullable=False, comment="Bank name (e.g., SBI)")
    account_mask = Column(VARCHAR(20), nullable=False, comment="Masked account number (e.g., XXXX1234)")
    last_sync = Column(TIMESTAMP(timezone=True), nullable=True, comment="Last synchronization time date")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), comment="Linked Creation time")
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now(), comment="Last update time")

    user = relationship("User", backref="bank_accounts")

class OTPVerification(Base):
    __tablename__ = 'otp_verifications'
    otp_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, comment="Unique OTP ID")
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False, comment="Owner user ID")
    otp_code = Column(VARCHAR(6), nullable=False, comment="One-time password code")
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False, comment="OTP expiry timestamp")
    verified = Column(BOOLEAN, nullable=False, default=False, comment="Verification status")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), comment="Creation time")
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now(), comment="Last update time")
    user = relationship("User", backref="otp_verifications")