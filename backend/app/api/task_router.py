from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import db_helper
from auth import api_key_header
from api.schemas import TaskPOST, SubTaskPOST, TaskPatch, SubTaskPostToMain
from models import Task, SubTask, User
import uuid
from api.utils import get_task_by_id, get_user_by_id


router = APIRouter(prefix="/v1/task")


@router.post("/main-create", tags=["task", "private"])
async def create_task(
    task_data: TaskPOST,
    user_id: str = Depends(api_key_header),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    try:
        subtasks_to_create = []
        subtasks = task_data.__dict__.pop("subtasks")
        main_task = Task(id=uuid.uuid4(), **task_data.model_dump())
        session.add(main_task)
        if len(subtasks) > 0:
            for task in subtasks:
                subtasks_to_create.append(
                    SubTask(parent_id=main_task.id, name=task.name)
                )
        session.add_all(subtasks_to_create)
        await session.commit()
        return {**main_task.__dict__, "subtasks": subtasks_to_create}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/delete/{task_id}", tags=["task", "private"])
async def delete_task(
    task_id: str,
    user_id: str = Depends(api_key_header),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    task = await get_task_by_id(task_id, session)
    if str(task.owner_id) != user_id:
        raise HTTPException(
            status_code=403, detail="Task can be deleted only by its owner"
        )
    await session.delete(task)
    await session.commit()
    return {"success": True}


@router.get("/retrieve/{task_id}")
async def retrieve_task(
    task_id: str,
    user_id: str | None = Depends(api_key_header),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    task = await get_task_by_id(task_id, session)
    if task.is_public is not True and str(task.owner_id) != user_id:
        raise HTTPException(status_code=403, detail="This task is private")
    return task


@router.patch("/update", tags=["task", "private"])
async def update_task(
    task_data: TaskPatch,
    user_id: str = Depends(api_key_header),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    task = await get_task_by_id(str(task_data.id), session)
    if str(task.owner_id) != user_id:
        raise HTTPException(
            status_code=403, detail="Task can be changed only by its owner"
        )
    new_data_dict = task_data.model_dump(exclude_none=True)
    for key, value in new_data_dict.items():
        setattr(task, key, value)
    await session.commit()
    return task


@router.post("/add-subtask", tags=["task", "private"])
async def create_subtasks(
    data: SubTaskPostToMain,
    user_id: str = Depends(api_key_header),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    task = await get_task_by_id(str(data.main_task_id), session)
    if str(task.owner_id) != user_id:
        raise HTTPException(
            status_code=403, detail="Task can be changed only by its owner"
        )
    tasks_to_create = []
    for subtask in data.subtasks:
        tasks_to_create.append(
            SubTask(name=subtask.name, is_completed=subtask.is_completed, parent_id=task.id)
        )
    session.add_all(tasks_to_create)
    await session.commit()
    return task
