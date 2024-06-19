from typing import AsyncGenerator, Annotated

from fastapi import FastAPI, Depends, Form, Request, HTTPException, status
from fastapi_users import FastAPIUsers
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from auth.auth import auth_backend, get_jwt_strategy
from auth.database import User, get_async_session, create_db_and_tables, get_user_db, get_user_tasks, AsyncSessionLocal, Task, delete_task_by_id, update_task_by_id, get_user_by_username
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
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

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


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


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
    await user_manager.create(user_create)
    return RedirectResponse(url="/login", status_code=303)


@app.get('/login', response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@app.post("/login")
async def login(
                form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                session: AsyncSession = Depends(get_async_session),
                jwt_strategy=Depends(get_jwt_strategy)):
    user = await get_user_by_username(form_data.username, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    success = pwd_context.verify(form_data.password, user.hashed_password)
    if user and success:
        token = await jwt_strategy.write_token(user)
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="fastapiusersauth", value=token, httponly=True)
        return response
    raise HTTPException(status_code=400, detail="Username or password incorrect")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request,
                    user: User = Depends(current_user),
                    session: AsyncSession = Depends(get_async_session)):
    tasks = await get_user_tasks(user.id, session)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "tasks": tasks})


@app.post("/add")
async def add(db: AsyncSession = Depends(get_db),
        creatorID: int = Form(...),
        title: str = Form(...),
        body: str = Form(...)):
    new_task = Task(title=title, description=body, user_id=creatorID)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/delete_task/{id}")
async def delete_task(id: int,
                      session: AsyncSession = Depends(get_async_session),
                      user: User = Depends(current_user)):
    success = await delete_task_by_id(session, id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/update_task")
async def update_task(new_title: str = Form(...),
                      new_description: str = Form(...),
                      task_id: int = Form(...),
                      session: AsyncSession = Depends(get_async_session),
                      user: User = Depends(current_user)
                      ):
    success = await update_task_by_id(session, task_id, user.id, new_title, new_description)

    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/logout")
async def logout():
    pass



