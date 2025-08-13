"""
Authentication service using PostgreSQL database
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import logging
import os

from app.models.database import User, get_db
from app.models.schemas import UserCreate, UserLogin, UserResponse, TokenData
from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", settings.SECRET_KEY)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


class AuthServiceDB:
    """Service for user authentication with database"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _hash_password(self, password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user in database"""
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create user
        db_user = User(
            email=user_data.email,
            password_hash=self._hash_password(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            company=user_data.company
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        logger.info(f"Created new user: {user_data.email}")
        
        return UserResponse(
            id=db_user.id,
            email=db_user.email,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            company=db_user.company,
            created_at=db_user.created_at,
            is_active=db_user.is_active
        )
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user"""
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not self._verify_password(password, user.password_hash):
            return None
        return user
    
    def create_access_token(self, user_id: str) -> str:
        """Create JWT access token"""
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"user_id": user_id, "exp": expire}
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("user_id")
            if user_id is None:
                return None
            return TokenData(user_id=user_id)
        except JWTError:
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID from database"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            company=user.company,
            created_at=user.created_at,
            is_active=user.is_active
        )
