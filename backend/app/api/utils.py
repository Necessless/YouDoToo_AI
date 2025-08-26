from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Task, SubTask
from fastapi import HTTPException
from sqlalchemy import select


async def get_task_by_id(id: str, session: AsyncSession) -> Task:
    """Метод для получения модели таска из бд по айди"""
    query = select(Task).where(Task.id == id)
    task = await session.scalar(query)
    if not task:
        raise HTTPException(status_code=404, detail="Task with this id was not found")
    return task


async def get_user_by_id(id: str, session: AsyncSession) -> User:
    """Метод для получения юзера из базы данных по его айди"""
    query = select(User).where(User.id == id)
    user = await session.scalar(query)
    if not user:
        raise HTTPException(status_code=404, detail="User with this id was not found")
    return user


async def get_user_by_email(email: str, session: AsyncSession) -> User:
    """Метод для получения юзера из базы данных по email"""
    query = select(User).where(User.email == email)
    user = await session.scalar(query)
    if not user:
        raise HTTPException(404, "User with this email was not found")
    return user