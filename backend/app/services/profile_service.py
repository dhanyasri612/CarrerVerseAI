from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.profile import ProfileResponse, ProfileUpdate


def get_profile(current_user: User):
    return current_user

def update_profile(db: Session, current_user: User, profile: ProfileUpdate):
    update_data = profile.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)
    db.commit()
    db.refresh(current_user)
    return current_user
