from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from math import ceil 

from app.api.deps import get_db, get_current_active_user, require_admin
from app.db.models import User, UserRole
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.services.task_service import TaskService
from app.core.config import settings

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db) 
):
    task = await TaskService.create_task(db, task_data, current_user.id)
    return task

@router.get("", response_model=TaskListResponse)
async def get_tasks(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Размер страницы"),
    completed: Optional[bool] = Query(None, description="Фильтр по статусу выполнения"),
    search: Optional[str] = Query(None, description="Поиск по названию и описанию"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    skip = (page - 1) * page_size
    
    is_admin = current_user.role == UserRole.ADMIN
    
    tasks, total = await TaskService.get_tasks(
        db=db,
        owner_id=current_user.id,
        is_admin=is_admin,
        skip=skip,
        limit=page_size,
        completed=completed,
        search=search
    )
    
    pages = ceil(total / page_size) if total > 0 else 0
    
    return TaskListResponse(
        items=tasks,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    is_admin = current_user.role == UserRole.ADMIN
    task = await TaskService.get_task(db, task_id, current_user.id, is_admin)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    is_admin = current_user.role == UserRole.ADMIN
    task = await TaskService.update_task(
        db, task_id, task_data, current_user.id, is_admin
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    is_admin = current_user.role == UserRole.ADMIN
    deleted = await TaskService.delete_task(
        db, task_id, current_user.id, is_admin
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return None
