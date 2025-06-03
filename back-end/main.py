from fastapi import FastAPI, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from crud import create_user, get_user_by_username_or_email, add_to_favorites, is_favorites, remove_from_favorites
from userdb import get_db
from model import RegisterUser, User, Favorite, TokenData, UserInDB, FavoriteInDB
from data.openai.query import recommend_books
from pydantic import BaseModel
from openai import AsyncOpenAI
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from suggest_words import fetch_book_suggestions
from pymilvus import connections, Collection
import os
import getpass

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("YOUR_OPENAI_API_KEY: ")
connections.connect(alias = "default", uri = "http://127.0.0.1:19530")
milvus_collection = Collection("books_dataset")
milvus_collection.load()
print(" [FastAPI] Milvus contains:", milvus_collection.num_entities, "vectors")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://192.168.1.190:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user_by_username_or_email(db, identifier=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/register/")
def register_user(user: RegisterUser, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db_user = create_user(db=db, username=user.username, email=user.email, password=hashed_password)
    return {"message": "User created successfully", "user_id": db_user.id}

@app.post("/login/")
def login_user(user: User, db: Session = Depends(get_db)):
    db_user = get_user_by_username_or_email(db=db, identifier=user.identifier)
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/logininfo")
def get_user_info(current_user: UserInDB = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email
    }

@app.post("/favorites/")
def add_to_favorites_api(favorite: Favorite, db: Session = Depends(get_db), current_user: UserInDB = Depends(get_current_user)):
    db_favorite = add_to_favorites(db=db, user_id=current_user.id, book_id=favorite.book_id)
    return {"message": "Book added to favorites"}

@app.get("/userfavorites")
def get_user_favorites(db: Session = Depends(get_db), current_user: UserInDB = Depends(get_current_user)):
    favorites = db.query(FavoriteInDB).filter(FavoriteInDB.user_id == current_user.id).all()
    books = []
    for fav in favorites:
        result = milvus_collection.query(
            expr = f'id == "{fav.book_id}"',
            output_fields=[
                "id", "title", "author", "publishing_year", "thumbnail",
                "description", "publisher", "num_pages", "language", "categories", "link"
            ],
            limit=1
        )
        if result:
            books.append(result[0])
    return {"favorites": books}

@app.get("/is_favorite/{book_id}")
def check_if_favorite(book_id: str, db: Session = Depends(get_db), current_user: UserInDB = Depends(get_current_user)):
    is_fav = is_favorites(db, current_user.id, book_id)
    return {"is_favorite": is_fav}

@app.delete("/favorites/{book_id}")
def delete_favorite(book_id: str, db: Session = Depends(get_db), current_user: UserInDB = Depends(get_current_user)):
    success = remove_from_favorites(db, current_user.id, book_id)
    if success:
        return {"message": "Removed from favorites"}
    else:
        raise HTTPException(status_code=404, detail="Book not found in favorites")

@app.get("/bookrcm")
def get_recommendations(query: str = Query(..., description="Search text")):
    try:
        results = recommend_books(query)
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}

class ExplainRequest(BaseModel):
    title: str
    author: str
    description: str

@app.get("/suggestions")
def get_suggestions(query: str = Query(..., description="User query for book suggestions")):
    try:
        suggestions = fetch_book_suggestions(query)
        return {"suggestions": suggestions}
    except Exception as e:
        return {"error": str(e)}

@app.post("/explain")
async def explain_book(data: ExplainRequest):
    prompt = f"""You're a helpful book recommender.
Given this book:

Title: {data.title}
Author(s): {data.author}
Description: {data.description}

Explain to the reader why they might like this book in 2-3 sentences in Vietnamese.
"""

    try:
        client = AsyncOpenAI()
        chat_response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You're a friendly and helpful book expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=120
        )
        return {"reason": chat_response.choices[0].message.content.strip()}
    except Exception as e:
        return {"error": str(e)}