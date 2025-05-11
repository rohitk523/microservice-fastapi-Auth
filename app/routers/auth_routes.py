# app/routers/auth_routes.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import UserInDB as UserModel  # Import the SQLAlchemy model
from app.schemas.user_schema import UserInDB, Token, UserResponse, UserCreate  # Import Pydantic schemas
from app.utils.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    verify_password,
    get_password_hash,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)
from app.database.database import get_db
from jose import JWTError, jwt

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_user(username: str, db: AsyncSession) -> UserModel:
    result = await db.execute(select(UserModel).where(UserModel.username == username))
    user = result.scalars().first()
    return user

async def authenticate_user(username: str, password: str, db: AsyncSession) -> UserModel:
    user = await get_user(username, db)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user(username, db)
    if user is None:
        raise credentials_exception
    return user

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")

@router.get("/users/me/", response_model=UserResponse)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    return current_user

@router.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if the user already exists
    existing_user = await get_user(user.username, db)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    # Hash the password
    hashed_password = get_password_hash(user.password)

    # Create a new user instance using the SQLAlchemy model
    new_user = UserModel(
        username=user.username, 
        email=user.email, 
        hashed_password=hashed_password
    )

    # Add the new user to the database
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user