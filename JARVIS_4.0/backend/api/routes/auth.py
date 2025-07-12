"""
JARVIS 4.0 Authentication Routes
JWT-based authentication system
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional

from core.config import settings

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

# Simple in-memory user store (replace with database in production)
USERS_DB = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("jarvis123"),
        "email": "admin@jarvis.ai",
        "is_active": True
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(username: str = Depends(verify_token)):
    """Get current authenticated user"""
    user = USERS_DB.get(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login endpoint"""
    user = USERS_DB.get(request.username)
    
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/register")
async def register(request: UserCreate):
    """Register new user"""
    if request.username in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(request.password)
    
    # Store user (in production, save to database)
    USERS_DB[request.username] = {
        "username": request.username,
        "hashed_password": hashed_password,
        "email": request.email,
        "is_active": True
    }
    
    return {"message": "User created successfully", "username": request.username}

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "username": current_user["username"],
        "email": current_user.get("email"),
        "is_active": current_user.get("is_active", True)
    }

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout endpoint (client should discard token)"""
    return {"message": "Successfully logged out"}

@router.post("/refresh")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh access token"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user["username"]}, expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.get("/verify")
async def verify_current_token(current_user: dict = Depends(get_current_user)):
    """Verify if current token is valid"""
    return {"valid": True, "username": current_user["username"]}