"""Simple FastAPI test app to verify auth works properly."""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime
import jwt
from typing import Optional
import uvicorn

# Create FastAPI app
app = FastAPI(title="Auth Test App")

# Configure JWT
SECRET_KEY = "testsecretkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token",
    auto_error=False  # Don't auto-error on missing token
)

# Dummy user database
users_db = {
    "test@example.com": {
        "username": "test@example.com",
        "password": "password123",
        "id": "1234"
    }
}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_optional(token: Optional[str] = Depends(oauth2_scheme)):
    """Get user from token, return None if no token or invalid."""
    if not token:
        return None
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return None
            
        return users_db.get(username)
    except:
        return None
        
def get_user_required(user = Depends(get_user_optional)):
    """Require user to be authenticated."""
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

# Public endpoints
@app.get("/")
def root():
    """Public endpoint (no auth)."""
    return {"message": "Welcome to Auth Test App"}
    
@app.get("/health")
def health():
    """Public endpoint (no auth)."""
    return {"status": "healthy"}
    
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint (no auth)."""
    user = users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
    
@app.post("/register")
def register(username: str, password: str):
    """Register endpoint (no auth)."""
    if username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
        
    users_db[username] = {
        "username": username,
        "password": password,
        "id": "user_" + str(len(users_db) + 1)
    }
    
    return {"username": username, "message": "User registered successfully"}

# Protected endpoints
@app.get("/me")
def read_users_me(current_user = Depends(get_user_required)):
    """Protected endpoint (auth required)."""
    return current_user
    
@app.get("/protected")
def protected_route(current_user = Depends(get_user_required)):
    """Protected endpoint (auth required)."""
    return {"message": "This is protected", "user": current_user["username"]}

if __name__ == "__main__":
    print("Starting test auth app on port 8000...")
    uvicorn.run("auth_test:app", host="0.0.0.0", port=8000, reload=True)
