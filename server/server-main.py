##  SERVER

from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, UploadFile, File, Body
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pydantic import BaseModel
import os
import uuid
import signal
from db.database import SessionLocal, Base, engine, hash_password, verify_password

# تنظیمات پایه
app = FastAPI(
    title="Pedram Social API",
    description="پیام‌رسان پیشرفته با قابلیت چت و ارسال فایل",
    version="1.0.0"
)

# مدل‌های دیتابیس
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    mobile = Column(String(11), unique=True, index=True)
    password_hash = Column(String(256))
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String(11), ForeignKey("users.mobile"))
    receiver = Column(String(11), ForeignKey("users.mobile"))
    content = Column(String(500))
    is_file = Column(Boolean, default=False)
    file_path = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

# ایجاد جداول
Base.metadata.create_all(bind=engine)

# مدیریت اتصالات WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, mobile: str):
        await websocket.accept()
        self.active_connections[mobile] = websocket

    def disconnect(self, mobile: str):
        if mobile in self.active_connections:
            del self.active_connections[mobile]

    async def send_personal_message(self, message: str, mobile: str):
        if mobile in self.active_connections:
            await self.active_connections[mobile].send_text(message)

manager = ConnectionManager()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# تنظیمات JWT
SECRET_KEY = "your-secret-key-here"  # در محیط واقعی از کلید پیچیده استفاده کنید!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# مدل‌های Pydantic
class UserCreate(BaseModel):
    mobile: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class MessageBase(BaseModel):
    sender: str
    receiver: str
    content: str

class FileMessage(BaseModel):
    sender: str
    receiver: str
    filename: str
    file_size: int

# تنظیمات فایل
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_FILE_TYPES = [
    "image/jpeg", 
    "image/png", 
    "application/pdf",
    "text/plain"
]

# Endpoints
@app.get("/", tags=["Root"])
async def root():
    return {"message": "خوش آمدید به پیام‌رسان پدرام"}

@app.post("/register/", tags=["Auth"])
async def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    ثبت‌نام کاربر جدید
    """
    db_user = db.query(User).filter(User.mobile == user.mobile).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="شماره موبایل قبلاً ثبت شده است"
        )
    
    hashed_password = hash_password(user.password)
    new_user = User(mobile=user.mobile, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    return {"message": "ثبت‌نام با موفقیت انجام شد"}

@app.post("/token/", response_model=Token, tags=["Auth"])
async def login(
    mobile: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    """
    ورود کاربر و دریافت توکن
    """
    user = db.query(User).filter(User.mobile == mobile).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="شماره موبایل یا رمز عبور نادرست",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.mobile})
    return {"access_token": access_token, "token_type": "bearer"}

@app.websocket("/ws/{mobile}")
async def websocket_endpoint(
    websocket: WebSocket,
    mobile: str,
    db: Session = Depends(get_db)
):
    """
    اتصال WebSocket برای چت بلادرنگ
    """
    await manager.connect(websocket, mobile)
    try:
        while True:
            data = await websocket.receive_text()
            # پردازش پیام دریافتی
            message = Message(
                sender=mobile,
                receiver=data['receiver'],  # در حالت واقعی از JSON پارس کنید
                content=data['message']
            )
            db.add(message)
            db.commit()
            
            # ارسال به گیرنده اگر آنلاین باشد
            await manager.send_personal_message(
                f"پیام جدید از {mobile}: {data['message']}",
                data['receiver']
            )
    except WebSocketDisconnect:
        manager.disconnect(mobile)
    except Exception as e:
        print(f"خطا در اتصال WebSocket: {e}")

@app.post("/messages/send/", tags=["Messages"])
async def send_message(
    message: MessageBase,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    ارسال پیام متنی
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sender_mobile = payload.get("sub")
        
        if sender_mobile != message.sender:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="عدم تطابق فرستنده با توکن"
            )
            
        db_message = Message(
            sender=message.sender,
            receiver=message.receiver,
            content=message.content
        )
        db.add(db_message)
        db.commit()
        
        # اطلاع به گیرنده از طریق WebSocket
        await manager.send_personal_message(
            f"پیام جدید از {message.sender}",
            message.receiver
        )
        
        return {"status": "پیام ارسال شد"}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن نامعتبر"
        )

@app.post("/uploadfile/", tags=["Files"])
async def upload_file(
    token: str = Depends(oauth2_scheme),
    file: UploadFile = File(...),
    sender: str = Body(...),
    receiver: str = Body(...),
    db: Session = Depends(get_db)
):
    """
    آپلود فایل با اعتبارسنجی
    """
    try:
        # احراز هویت
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # اعتبارسنجی نوع فایل
        if file.content_type not in ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="نوع فایل مجاز نیست"
            )
        
        # ایجاد نام منحصر به فرد
        file_ext = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # ذخیره فایل با کنترل حجم
        file_size = 0
        with open(file_path, "wb") as buffer:
            while content := await file.read(1024):
                file_size += len(content)
                if file_size > MAX_FILE_SIZE:
                    os.remove(file_path)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"حجم فایل نباید بیشتر از {MAX_FILE_SIZE//(1024*1024)} مگابایت باشد"
                    )
                buffer.write(content)
        
        # ذخیره در دیتابیس
        db_message = Message(
            sender=sender,
            receiver=receiver,
            content=f"FILE:{unique_filename}",
            is_file=True,
            file_path=file_path
        )
        db.add(db_message)
        db.commit()
        
        # اطلاع به گیرنده
        await manager.send_personal_message(
            f"فایل جدید از {sender}: {file.filename}",
            receiver
        )
        
        return {
            "filename": file.filename,
            "saved_as": unique_filename,
            "size": file_size,
            "type": file.content_type
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن نامعتبر"
        )

@app.get("/download/{filename}", tags=["Files"])
async def download_file(filename: str):
    """
    دانلود فایل آپلود شده
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="فایل یافت نشد"
        )
    return FileResponse(
        file_path,
        filename=filename,
        media_type="application/octet-stream"
    )

# مدیریت خاموشی سرور
shutdown_router = APIRouter()

@shutdown_router.post("/shutdown", include_in_schema=False)
async def shutdown_server():
    os.kill(os.getpid(), signal.SIGINT)
    return {"message": "سرور در حال خاموش شدن است"}

app.include_router(shutdown_router)


from fastapi import APIRouter
from .core.auth import (
    Token,
    User,
    get_current_active_user,
    create_access_token,
    get_password_hash,
    verify_password
)

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = get_user_from_db(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect mobile or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.mobile},
        expires_delta=timedelta(minutes=int(os.getenv("JWT_EXPIRE_MINUTES", 30)))
    
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/register")
async def register_user(
    mobile: str = Body(...),
    password: str = Body(...)
):
    # بررسی وجود کاربر
    if get_user_from_db(mobile):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile already registered"
        )
    
    # ذخیره کاربر جدید (در دیتابیس واقعی)
    hashed_password = get_password_hash(password)
    new_user = {
        "mobile": mobile,
        "hashed_password": hashed_password,
        "disabled": False
    }
    # اینجا باید کاربر را در دیتابیس ذخیره کنید
    # مثلاً: db.add(User(...)); db.commit()
    
    return {"message": "User registered successfully"}

@auth_router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user