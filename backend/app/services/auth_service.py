"""
Authentication service for user management and JWT handling
"""
import os
import json
import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging

from app.core.config import settings
from app.models.schemas import UserCreate, UserLogin, UserResponse, TokenData

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = settings.SECRET_KEY or "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


class AuthService:
    """Service for user authentication and management"""
    
    def __init__(self):
        self.users_file = os.path.join(settings.DATA_PATH, "users.json")
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        """Ensure users file exists"""
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        if not os.path.exists(self.users_file):
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump({}, f)
    
    def _load_users(self) -> Dict[str, Any]:
        """Load users from file"""
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            return {}
    
    def _save_users(self, users: Dict[str, Any]):
        """Save users to file"""
        try:
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(users, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving users: {e}")
            raise
    
    def _hash_password(self, password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def _get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        users = self._load_users()
        for user_id, user_data in users.items():
            if user_data.get("email") == email:
                user_data["id"] = user_id
                return user_data
        return None
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        # Check if user already exists
        if self._get_user_by_email(user_data.email):
            raise ValueError("User with this email already exists")
        
        # Create user
        user_id = str(uuid.uuid4())
        hashed_password = self._hash_password(user_data.password)
        
        new_user = {
            "email": user_data.email,
            "password_hash": hashed_password,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "company": user_data.company,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True
        }
        
        # Save user
        users = self._load_users()
        users[user_id] = new_user
        self._save_users(users)
        
        # Create user directory
        user_dir = os.path.join(settings.DATA_PATH, "users", user_id)
        os.makedirs(user_dir, exist_ok=True)
        
        logger.info(f"Created new user: {user_data.email}")
        
        return UserResponse(
            id=user_id,
            email=new_user["email"],
            first_name=new_user["first_name"],
            last_name=new_user["last_name"],
            company=new_user["company"],
            created_at=datetime.fromisoformat(new_user["created_at"]),
            is_active=new_user["is_active"]
        )
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user"""
        user = self._get_user_by_email(email)
        if not user or not self._verify_password(password, user["password_hash"]):
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
        """Get user by ID"""
        users = self._load_users()
        user_data = users.get(user_id)
        if not user_data:
            return None
        
        return UserResponse(
            id=user_id,
            email=user_data["email"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            company=user_data["company"],
            created_at=datetime.fromisoformat(user_data["created_at"]),
            is_active=user_data["is_active"]
        )

