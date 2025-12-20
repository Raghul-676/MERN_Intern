from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from bson import ObjectId
from app.api.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

# CHANGE this secret in .env for real use
SECRET_KEY = "CHANGE_ME_TO_RANDOM_HEX"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def hash_password(pw: str):
    # optional safety for bcrypt 72‑byte limit
    if len(pw) > 72:
        pw = pw[:72]
    return pwd_context.hash(pw)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user_by_email(db, email: str):
    return db.users.find_one({"email": email})


@router.post("/register", response_model=UserOut)
def register_user(payload: UserCreate, db=Depends(get_db)):
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    doc = {
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "role": "user",  # ALWAYS normal user
        "created_at": datetime.utcnow(),
    }
    res = db.users.insert_one(doc)

    return UserOut(id=str(res.inserted_id), email=payload.email, role="user")


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(get_db),
):
    # form_data.username carries email in our case
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user["_id"]), "email": user["email"], "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token, token_type="bearer")


# ---------- default admin helper & one-time init route ----------

def create_default_admin(db):
    email = "admin@bajaj.com"
    if db.users.find_one({"email": email}):
        return  # already exists

    doc = {
        "email": email,
        "password_hash": hash_password("Admin@123"),  # default admin password
        "role": "admin",
        "created_at": datetime.utcnow(),
    }
    db.users.insert_one(doc)


@router.post("/init-admin")
def init_admin(db=Depends(get_db)):
    create_default_admin(db)
    return {"status": "ok"}


# ---------- dependencies to use in other routes ----------

class CurrentUser(BaseModel):
    id: str
    email: EmailStr
    role: str


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db=Depends(get_db),
) -> CurrentUser:
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise cred_exc
    except JWTError:
        raise cred_exc

    try:
        oid = ObjectId(user_id)
    except Exception:
        raise cred_exc

    user = db.users.find_one({"_id": oid})
    if not user:
        raise cred_exc

    return CurrentUser(id=str(user["_id"]), email=user["email"], role=user["role"])

@router.get("/me", response_model=CurrentUser)
def read_me(current_user: CurrentUser = Depends(get_current_user)):
    return current_user

def get_current_admin(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
