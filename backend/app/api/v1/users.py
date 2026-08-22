from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.firebase_auth import get_current_user
from app.models.user import User
from app.schemas.user import UserSyncIn, UserOut

router = APIRouter()

@router.post('/users/sync', response_model=UserOut)
def sync_user(payload: UserSyncIn, db: Session = Depends(get_db), claims: dict = Depends(get_current_user)):
    # Prefer claims for uid/email if not provided
    uid = payload.uid or claims.get('uid') or claims.get('user_id')
    email = payload.email or claims.get('email')

    if not uid and not email:
        raise HTTPException(status_code=400, detail='uid or email required')

    # Find existing by uid or email
    user = None
    if uid:
        user = db.query(User).filter(User.firebase_uid == uid).first()
    if not user and email:
        user = db.query(User).filter(User.email == email).first()

    fields = {
        'firebase_uid': uid,
        'email': email,
        'full_name': payload.name,
    }

    if user:
        for k, v in fields.items():
            if v is not None:
                setattr(user, k, v)
    else:
        user = User(**fields)
        db.add(user)

    db.commit()
    db.refresh(user)
    return user