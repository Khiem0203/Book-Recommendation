from sqlalchemy.orm import Session
from sqlalchemy import or_
from model import UserInDB, FavoriteInDB

def create_user(db: Session,email: str, username: str, password: str):
    db_user = UserInDB(email = email,username=username, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username_or_email(db: Session, identifier: str):
    return db.query(UserInDB).filter(
        or_(UserInDB.username == identifier, UserInDB.email == identifier)
    ).first()

def add_to_favorites(db: Session, user_id: int, book_id: int):
    db_favorite = FavoriteInDB(user_id=user_id, book_id=book_id)
    db.add(db_favorite)
    db.commit()
    return db_favorite

def is_favorites(db: Session, user_id: int, book_id: str):
    return db.query(FavoriteInDB).filter_by(user_id=user_id, book_id=book_id).first() is not None

def remove_from_favorites(db: Session, user_id: int, book_id: str):
    favorite = db.query(FavoriteInDB).filter_by(user_id=user_id, book_id=book_id).first()
    if favorite:
        db.delete(favorite)
        db.commit()
        return True
    return False
