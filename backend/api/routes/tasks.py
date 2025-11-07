"""
Task management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from core.database import get_db, Task
from pydantic import BaseModel

router = APIRouter()


class TaskCreate(BaseModel):
    description: str
    user_id: str
    workspace_path: str


class TaskResponse(BaseModel):
    task_id: str
    status: str
    description: str
    assigned_agent: str = None
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new task"""
    new_task = Task(
        task_id=str(uuid.uuid4()),
        user_id=task.user_id,
        description=task.description,
        status="pending"
    )
    
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    return TaskResponse(
        task_id=new_task.task_id,
        status=new_task.status,
        description=new_task.description,
        created_at=new_task.created_at.isoformat()
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get task by ID"""
    result = await db.execute(
        select(Task).where(Task.task_id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(
        task_id=task.task_id,
        status=task.status,
        description=task.description,
        assigned_agent=task.assigned_agent,
        created_at=task.created_at.isoformat()
    )


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    user_id: str = None,
    status: str = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List tasks with optional filters"""
    query = select(Task)
    
    if user_id:
        query = query.where(Task.user_id == user_id)
    if status:
        query = query.where(Task.status == status)
    
    query = query.limit(limit).order_by(Task.created_at.desc())
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    return [
        TaskResponse(
            task_id=task.task_id,
            status=task.status,
            description=task.description,
            assigned_agent=task.assigned_agent,
            created_at=task.created_at.isoformat()
        )
        for task in tasks
    ]
