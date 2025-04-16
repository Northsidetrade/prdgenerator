"""Minimal API server for testing authentication fixes."""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import jwt
import uvicorn

# Configure the app
app = FastAPI(title="Minimal API")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security configuration
SECRET_KEY = "testkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class UserIn(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username: str

# Fake user database
fake_users_db = {
    "testuser": {"username": "testuser", "password": "password123"}
}

# Custom OAuth2 scheme that doesn't enforce auth on specific paths
class OptionalOAuth2PasswordBearer(OAuth2PasswordBearer):
    def __init__(self, tokenUrl: str, auto_error: bool = True):
        super().__init__(tokenUrl=tokenUrl, auto_error=auto_error)
    
    async def __call__(self, request):
        # Skip auth for these paths
        if request.url.path in ["/health", "/auth/login", "/auth/register"]:
            return None
        return await super().__call__(request)

# Create our custom OAuth2 scheme
oauth2_scheme = OptionalOAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=True)

# Helper functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: Optional[str] = Depends(oauth2_scheme)):
    # No token for public endpoints
    if token is None:
        return None
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return None
    except jwt.PyJWTError:
        return None
        
    if username in fake_users_db:
        return fake_users_db[username]
    return None

# Public endpoints
@app.get("/health")
async def health_check():
    """Public health check endpoint - no auth required."""
    return {"status": "healthy"}

@app.get("/")
async def root():
    """Root endpoint - no auth required."""
    return {"message": "Welcome to the Minimal API"}

# Auth endpoints
@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint - no auth required."""
    print(f"Login attempt: {form_data.username}")
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/register", response_model=User)
async def register(user_in: UserIn):
    """Register endpoint - no auth required."""
    print(f"Register attempt: {user_in.username}")
    if user_in.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
        
    fake_users_db[user_in.username] = {
        "username": user_in.username,
        "password": user_in.password
    }
    return {"username": user_in.username}

# Protected endpoint
@app.get("/protected")
async def protected_route(current_user = Depends(get_current_user)):
    """Protected endpoint - auth required."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"message": "This is a protected route", "user": current_user["username"]}

if __name__ == "__main__":
    uvicorn.run("minimal_api:app", host="127.0.0.1", port=8008, reload=True)
