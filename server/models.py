from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, DateTime
from enum import Enum as PyEnum


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    sender = Column(String(11), ForeignKey("users.mobile"))
    receiver = Column(String(11), ForeignKey("users.mobile"))
    content = Column(String(500))  # محدودیت 500 کاراکتر
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    

class FriendshipStatus(PyEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    BLOCKED = "blocked"

class Friendship(Base):
    __tablename__ = "friendships"
    
    id = Column(Integer, primary_key=True, index=True)
    requester_mobile = Column(String(11), ForeignKey("users.mobile"))
    receiver_mobile = Column(String(11), ForeignKey("users.mobile"))
    status = Column(Enum(FriendshipStatus), default=FriendshipStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)