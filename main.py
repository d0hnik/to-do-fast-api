from fastapi import FastAPI, Depends, Form, Request
from fastapi_users import FastAPIUsers
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse

from auth.auth import auth_backend, get_jwt_strategy
from auth.database import User, get_async_session, create_db_and_tables, get_user_db, get_user_tasks
from auth.manager import get_user_manager
from auth.schemas import UserRead, UserCreate

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
current_user = fastapi_users.current_user()

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()


@app.get("/", response_class=HTMLResponse, response_model=False)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register", response_class=HTMLResponse)
async def register_user(
        email: str = Form(...),
        username: str = Form(...),
        password: str = Form(...),
        user_manager=Depends(get_user_manager)
):
    user_create = UserCreate(email=email, username=username, password=password)
    user = await user_manager.create(user_create)
    return RedirectResponse(url="/login", status_code=303)


@app.get('/login', response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login_user(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        user_db=Depends(get_user_db),
        jwt_strategy=Depends(get_jwt_strategy)
):
    user = await user_db.get_by_email(email)
    if user:
        token = await jwt_strategy.write_token(user)
        print(token)
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="fastapiusersauth", value=token, httponly=True)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: User = Depends(current_user)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user.username})
