from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    sender = Column(String(11), ForeignKey("users.mobile"))
    receiver = Column(String(11), ForeignKey("users.mobile"))
    content = Column(String(500))  # محدودیت 500 کاراکتر
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)