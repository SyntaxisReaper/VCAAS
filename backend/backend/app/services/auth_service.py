"""
Authentication Service

Handles user authentication, JWT token generation, and password management.
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, ValidationError
from loguru import logger

from app.models.mongo.user import User


# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30


class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    username: str
    email: str
    subscription_tier: str


class AuthTokens(BaseModel):
    """Authentication tokens response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str
    remember_me: bool = False


class SignupRequest(BaseModel):
    """Signup request model"""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    terms_accepted: bool


class AuthService:
    """Authentication service class"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storing"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_verification_token() -> str:
        """Generate a secure verification token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
        """Verify JWT token and extract data"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Check token type
            if payload.get("type") != token_type:
                return None
            
            # Extract user data
            user_id = payload.get("user_id")
            username = payload.get("username")
            email = payload.get("email")
            subscription_tier = payload.get("subscription_tier", "free")
            
            if not user_id or not username or not email:
                return None
            
            return TokenData(
                user_id=user_id,
                username=username,
                email=email,
                subscription_tier=subscription_tier
            )
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
        except ValidationError as e:
            logger.warning(f"Token data validation failed: {e}")
            return None
    
    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            # Find user by email
            user = await User.find_one(User.email == email)
            if not user:
                return None
            
            # Check if account is locked
            if user.is_account_locked():
                logger.warning(f"Login attempt on locked account: {email}")
                return None
            
            # Verify password
            if not AuthService.verify_password(password, user.password_hash):
                # Record failed login attempt
                await user.record_failed_login()
                return None
            
            # Check if account is active
            if not user.is_active:
                logger.warning(f"Login attempt on inactive account: {email}")
                return None
            
            # Record successful login
            await user.record_login()
            
            return user
            
        except Exception as e:
            logger.error(f"Authentication error for {email}: {e}")
            return None
    
    @staticmethod
    async def create_user(signup_data: SignupRequest) -> Optional[User]:
        """Create new user account"""
        try:
            # Check if terms are accepted
            if not signup_data.terms_accepted:
                raise ValueError("Terms and conditions must be accepted")
            
            # Check if user already exists
            existing_user = await User.find_one(
                {"$or": [
                    {"email": signup_data.email},
                    {"username": signup_data.username}
                ]}
            )
            
            if existing_user:
                if existing_user.email == signup_data.email:
                    raise ValueError("Email already registered")
                if existing_user.username == signup_data.username:
                    raise ValueError("Username already taken")
            
            # Validate password strength
            if len(signup_data.password) < 8:
                raise ValueError("Password must be at least 8 characters long")
            
            # Create user
            user = User(
                email=signup_data.email,
                username=signup_data.username,
                full_name=signup_data.full_name,
                password_hash=AuthService.hash_password(signup_data.password),
                verification_token=AuthService.generate_verification_token(),
                is_verified=False  # Require email verification
            )
            
            await user.save()
            
            logger.info(f"New user created: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"User creation error: {e}")
            raise
    
    @staticmethod
    def create_auth_tokens(user: User, remember_me: bool = False) -> AuthTokens:
        """Create access and refresh tokens for user"""
        # Token payload
        token_data = {
            "user_id": str(user.id),
            "username": user.username,
            "email": user.email,
            "subscription_tier": user.subscription_tier
        }
        
        # Create access token
        access_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        if remember_me:
            access_expire = timedelta(hours=24)  # Longer expiry if remember me
        
        access_token = AuthService.create_access_token(
            data=token_data,
            expires_delta=access_expire
        )
        
        # Create refresh token
        refresh_token = AuthService.create_refresh_token(data=token_data)
        
        return AuthTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(access_expire.total_seconds())
        )
    
    @staticmethod
    async def refresh_access_token(refresh_token: str) -> Optional[AuthTokens]:
        """Refresh access token using refresh token"""
        try:
            # Verify refresh token
            token_data = AuthService.verify_token(refresh_token, "refresh")
            if not token_data:
                return None
            
            # Get user from database
            user = await User.get(token_data.user_id)
            if not user or not user.is_active:
                return None
            
            # Create new tokens
            return AuthService.create_auth_tokens(user)
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return None
    
    @staticmethod
    async def verify_email(token: str) -> bool:
        """Verify user email with verification token"""
        try:
            user = await User.find_one(User.verification_token == token)
            if not user:
                return False
            
            # Verify email and clear token
            user.is_verified = True
            user.verification_token = None
            await user.save()
            
            logger.info(f"Email verified for user: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Email verification error: {e}")
            return False
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            return await User.get(user_id)
        except Exception:
            return None
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength and return feedback"""
        checks = {
            "length": len(password) >= 8,
            "uppercase": any(c.isupper() for c in password),
            "lowercase": any(c.islower() for c in password),
            "numbers": any(c.isdigit() for c in password),
            "special": any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        }
        
        score = sum(checks.values())
        
        if score < 3:
            strength = "weak"
        elif score < 4:
            strength = "medium"
        else:
            strength = "strong"
        
        return {
            "strength": strength,
            "score": score,
            "checks": checks,
            "suggestions": [
                "At least 8 characters" if not checks["length"] else None,
                "Include uppercase letters" if not checks["uppercase"] else None,
                "Include lowercase letters" if not checks["lowercase"] else None,
                "Include numbers" if not checks["numbers"] else None,
                "Include special characters" if not checks["special"] else None
            ]
        }