from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Task, SubTask
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload


async def get_task(session: AsyncSession, **attributes) -> Task:
    """Метод для получения модели таска из бд по его аттрибутам"""
    query = select(Task).filter_by(**attributes).options(selectinload(Task.subtasks))
    task = await session.scalar(query)
    if not task:
        raise HTTPException(status_code=404, detail="Task with this attributes was not found")
    return task


async def get_subtask(session: AsyncSession, **attributes) -> SubTask:
    """Метод для получения модели сабтаска из бд по его аттрибутам"""
    query = select(SubTask).filter_by(**attributes).options(joinedload(SubTask.parent)) # joinedload так как 
    subtask = await session.scalar(query)
    if not subtask:
        raise HTTPException(status_code=404, detail="SubTask with this attributes was not found")
    return subtask


async def get_user(session: AsyncSession, **attributes) -> User:
    """Метод для получения юзера из базы данных по его аттрибутам"""
    query = select(User).filter_by(**attributes).options(selectinload(User.tasks))
    user = await session.scalar(query)
    if not user:
        raise HTTPException(status_code=404, detail="User with this attributes was not found")
    return user
