from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import db_helper
from auth import api_key_header
from api.schemas import TaskPOST, SubTaskPOST
from models import Task, SubTask, User
import uuid


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
