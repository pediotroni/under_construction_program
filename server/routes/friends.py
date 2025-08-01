from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime

router = APIRouter(prefix="/friends", tags=["Friendship"])

@router.post("/request/{receiver_mobile}")
async def send_friend_request(
    receiver_mobile: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # اعتبارسنجی شماره موبایل گیرنده
    if not is_valid_mobile(receiver_mobile):
        raise HTTPException(status_code=400, detail="Invalid mobile number")
    
    # بررسی وجود کاربر گیرنده
    receiver = db.query(User).filter(User.mobile == receiver_mobile).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="User not found")
    
    # بررسی درخواست تکراری
    existing_request = db.query(Friendship).filter(
        ((Friendship.requester_mobile == current_user.mobile) & 
         (Friendship.receiver_mobile == receiver_mobile)) |
        ((Friendship.requester_mobile == receiver_mobile) & 
         (Friendship.receiver_mobile == current_user.mobile))
    ).first()
    
    if existing_request:
        raise HTTPException(status_code=400, detail="Request already exists")
    
    # ایجاد درخواست جدید
    new_request = Friendship(
        requester_mobile=current_user.mobile,
        receiver_mobile=receiver_mobile,
        status=FriendshipStatus.PENDING
    )
    db.add(new_request)
    db.commit()
    
    # ارسال نوتیفیکیشن (WebSocket)
    await notify_user(receiver_mobile, f"New friend request from {current_user.mobile}")
    
    return {"message": "Friend request sent"}

@router.get("/requests", response_model=List[FriendRequest])
async def get_pending_requests(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return db.query(Friendship).filter(
        Friendship.receiver_mobile == current_user.mobile,
        Friendship.status == FriendshipStatus.PENDING
    ).all()

@router.post("/respond/{request_id}")
async def respond_to_request(
    request_id: int,
    response: str,  # "accept" or "reject"
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    request = db.query(Friendship).filter(
        Friendship.id == request_id,
        Friendship.receiver_mobile == current_user.mobile
    ).first()
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if response.lower() == "accept":
        request.status = FriendshipStatus.ACCEPTED
        # ایجاد رابطه دو طرفه
        reverse_friendship = Friendship(
            requester_mobile=current_user.mobile,
            receiver_mobile=request.requester_mobile,
            status=FriendshipStatus.ACCEPTED
        )
        db.add(reverse_friendship)
    else:
        request.status = FriendshipStatus.REJECTED
    
    db.commit()
    return {"message": f"Request {response}ed"}
