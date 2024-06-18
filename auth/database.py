import uuid
from typing import AsyncGenerator
from uuid import UUID

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Integer, Column, String, Boolean, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker
from sqlalchemy.future import select

DATABASE_URL = "sqlite+aiosqlite:///./data.db"


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_superuser = Column(Boolean, nullable=False, default=False)
    is_verified = Column(Boolean, nullable=False, default=False)

    tasks = relationship("Task", back_populates="owner")


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # Define relationship to User
    owner = relationship("User", back_populates="tasks")


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_by_username(username: str, session: AsyncSession):
    """ Fetches a user from the database by username """
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_tasks(user_id: int, session: AsyncSession):
    # No need to explicitly begin a transaction since we're using async session
    stmt = select(Task).where(Task.user_id == user_id)
    result = await session.execute(stmt)
    tasks = result.scalars().all()
    return tasks


async def delete_task_by_id(session: AsyncSession, task_id: int, user_id: int):
    task = await session.get(Task, task_id)

    if task is None or task.user_id != user_id:
        return False

    await session.delete(task)
    await session.commit()  # Salvestame muudatused andmebaasi
    return True


async def update_task_by_id(session: AsyncSession, task_id: int, user_id: int, new_title: str, new_description: str):
    task = await session.get(Task, task_id)
    if task is None or task.user_id != user_id:
        return False

    task.title = new_title
    task.description = new_description
    await session.commit()
    return True
