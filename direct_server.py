"""Direct FastAPI implementation for PRD Generator API with NO AUTHENTICATION."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# Removed SQLAlchemy import
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import uuid

# Create FastAPI app
app = FastAPI(title="Direct PRD Generator API")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock database
USERS_DB = {}
PRDS_DB = {}

# Config
SECRET_KEY = "directsecretkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class User(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool = True

class PRDCreate(BaseModel):
    title: str
    description: str
    product_type: str

class PRD(BaseModel):
    id: str
    title: str
    description: str
    product_type: str
    created_at: datetime
    user_id: str

# Helper functions
def create_access_token(subject: str, expires_delta: Optional[timedelta] = None):
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_email(email: str):
    return USERS_DB.get(email)

def get_user_by_id(user_id: str):
    for user in USERS_DB.values():
        if user["id"] == user_id:
            return user
    return None

def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        return None
        
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
        
    token = parts[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
            
        user = get_user_by_id(user_id)
        return user
    except jwt.PyJWTError:
        return None

# Public endpoints
@app.get("/")
def root():
    return {"status": "healthy", "message": "Direct PRD Generator API"}

@app.get("/api/v1/health")
def health():
    return {"status": "healthy", "service": "prd-generator", "version": "0.1.0"}

@app.post("/api/v1/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",

@app.post("/api/v1/auth/register", response_model=User)
def register(user_in: UserCreate):
    if user_in.email in USERS_DB:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    user_id = str(uuid.uuid4())
    USERS_DB[user_in.email] = {
        "id": user_id,
        "email": user_in.email,
        "password": user_in.password,
        "full_name": user_in.full_name,
        "is_active": True
    }
    
    return {
        "id": user_id,
        "email": user_in.email,
        "full_name": user_in.full_name,
        "is_active": True
    }

# Protected endpoints
@app.get("/api/v1/users/me", response_model=User)
def get_me(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "is_active": current_user["is_active"]
    }

@app.post("/api/v1/prd/generate", response_model=PRD)
def generate_prd(prd_in: PRDCreate, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    prd_id = str(uuid.uuid4())
    prd = {
        "id": prd_id,
        "title": prd_in.title,
        "description": prd_in.description,
        "product_type": prd_in.product_type,
        "created_at": datetime.utcnow(),
        "user_id": current_user["id"]
    }
    
    PRDS_DB[prd_id] = prd
    return prd

@app.get("/api/v1/prd", response_model=List[PRD])
def get_prds(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_prds = []
    for prd in PRDS_DB.values():
        if prd["user_id"] == current_user["id"]:
            user_prds.append(prd)
            
    return user_prds

if __name__ == "__main__":
    # Add a test user
    USERS_DB["test@example.com"] = {
        "id": str(uuid.uuid4()),
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
        "is_active": True
    }
    
    print("Starting direct server on port 8888, test user: test@example.com / password123")
    import uvicorn
    uvicorn.run("direct_server:app", host="0.0.0.0", port=8888, reload=True)
