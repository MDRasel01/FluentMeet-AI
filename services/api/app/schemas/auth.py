from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    confirm_password: Optional[str] = None
    full_name: str = Field(..., min_length=2)
    native_language: Optional[str] = "English"
    terms_accepted: bool = Field(True, description="Must accept terms of service")
    privacy_accepted: bool = Field(True, description="Must accept privacy policy")

    @model_validator(mode="after")
    def verify_passwords_match(self):
        if self.confirm_password is not None and self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        if not self.terms_accepted:
            raise ValueError("You must accept the terms of service")
        if not self.privacy_accepted:
            raise ValueError("You must accept the privacy policy")
        return self

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_type: Optional[str] = "desktop"
    session_name: Optional[str] = None

class EmailVerifyRequest(BaseModel):
    token: str = Field(..., min_length=10)

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=8)
    confirm_password: Optional[str] = None

    @model_validator(mode="after")
    def verify_passwords_match(self):
        if self.confirm_password is not None and self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: Optional[str] = None

    @model_validator(mode="after")
    def verify_passwords_match(self):
        if self.confirm_password is not None and self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    native_language: Optional[str]
    role: str
    status: str
    is_active: bool
    is_verified: bool
    email_verified_at: Optional[datetime] = None
    timezone: str = "UTC"

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user: Optional[UserProfileResponse] = None

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class AuthSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_name: Optional[str]
    device_type: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    last_used_at: datetime
    expires_at: datetime
    is_current: bool = False
