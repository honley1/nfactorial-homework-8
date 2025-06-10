from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import UserCreate
from ..auth import authenticate_user, create_access_token, get_current_user
from ..crud import create_user, get_user_by_username, get_user_by_email, get_tasks_by_user
from ..models import User
from datetime import timedelta
from ..config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(tags=["frontend"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Invalid username or password"}
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Redirect to dashboard with token in cookie
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=access_token, httponly=False, secure=False)
    return response

@router.post("/register", response_class=HTMLResponse)
async def register_form(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if user already exists
    if get_user_by_username(db, username):
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "error": "Username already registered"}
        )
    
    if get_user_by_email(db, email):
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "error": "Email already registered"}
        )
    
    try:
        user_create = UserCreate(username=username, email=email, password=password)
        create_user(db=db, user=user_create)
        
        # Auto login after registration
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="access_token", value=access_token, httponly=False, secure=False)
        return response
        
    except Exception as e:
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "error": "Registration failed"}
        )

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    # Get token from cookie
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login")
    
    try:
        # Token from cookie is just the token without Bearer prefix
        # Mock the HTTPAuthorizationCredentials for our verify_token function
        from fastapi.security import HTTPAuthorizationCredentials
        from ..auth import verify_token
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        token_data = verify_token(credentials)
        
        # Get current user
        user = db.query(User).filter(User.username == token_data.username).first()
        if not user:
            response = RedirectResponse(url="/login")
            response.delete_cookie(key="access_token")
            return response
        
        # Get user's tasks
        tasks = get_tasks_by_user(db, user_id=user.id)
        
        return templates.TemplateResponse(
            "dashboard.html", 
            {"request": request, "user": user, "tasks": tasks}
        )
        
    except Exception as e:
        response = RedirectResponse(url="/login")
        response.delete_cookie(key="access_token")
        return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie(key="access_token")
    return response 