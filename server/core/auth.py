from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

# تنظیمات امنیتی
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# مدل‌های داده
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    mobile: Optional[str] = None

class User(BaseModel):
    mobile: str
    disabled: bool = False

class UserInDB(User):
    hashed_password: str

# توابع کمکی
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        os.getenv("JWT_SECRET_KEY"), 
        algorithm=os.getenv("JWT_ALGORITHM", "HS256")
    )
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            os.getenv("JWT_SECRET_KEY"), 
            algorithms=[os.getenv("JWT_ALGORITHM", "HS256")]
        )
        mobile: str = payload.get("sub")
        if mobile is None:
            raise credentials_exception
        token_data = TokenData(mobile=mobile)
    except JWTError:
        raise credentials_exception
    
    # در اینجا باید کاربر را از دیتابیس بخوانید
    # نمونه ساده:
    user = get_user_from_db(mobile=token_data.mobile)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# نمونه تابع برای دسترسی به دیتابیس (باید با دیتابیس واقعی جایگزین شود)
def get_user_from_db(mobile: str):
    # اینجا باید به دیتابیس واقعی متصل شوید
    fake_users_db = {
        "09123456789": {
            "mobile": "09123456789",
            "hashed_password": get_password_hash("1234"),
            "disabled": False
        }
    }
    if mobile in fake_users_db:
        return UserInDB(**fake_users_db[mobile])
    return None
