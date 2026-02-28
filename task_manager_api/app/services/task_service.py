from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.db.models import Task
from app.schemas.task import TaskCreate, TaskUpdate

class TaskService:
    @staticmethod
    async def create_task(
        db: AsyncSession,
        task_data: TaskCreate,
        owner_id: int,
    ) -> Task:
        task = Task(**task_data.model_dump(), owner_id=owner_id)
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task
    
    @staticmethod
    async def get_task(
        db: AsyncSession,
        task_id: int,
        owner_id: Optional[int] = None,
        is_admin: bool = False,
    ) -> Optional[Task]:
        query = select(Task).where(Task.id == task_id)
        if not is_admin and owner_id:
            query = query.where(Task.owner_id == owner_id)
        result = await db.execute(query.options(selectinload(Task.owner)))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_tasks(
        db: AsyncSession,
        owner_id: Optional[int] = None,
        is_admin: bool = False,
        skip: int = 0,
        limit: int = 10,
        completed: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> tuple[list[Task], int]:
        query = select(Task)
        count_query = select(func.count()).select_from(Task)
        conditions = []
        if not is_admin and owner_id:
            conditions.append(Task.owner_id == owner_id)
        if completed is not None:
            conditions.append(Task.completed == completed)
        if search:
            search_condition = or_(
                Task.title.ilike(f"%{search}%"),
                Task.description.ilike(f"%{search}%"),
            )
            conditions.append(search_condition)
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query.options(selectinload(Task.owner)))
        tasks = result.scalars().all()
        return tasks, total
    
    @staticmethod
    async def update_task(
        db: AsyncSession,
        task_id: int,
        task_data: TaskUpdate,
        owner_id: Optional[int] = None,
        is_admin: bool = False,
    ) -> Optional[Task]:
        task = await TaskService.get_task(db, task_id, owner_id, is_admin)
        if not task:
            return None
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        await db.commit()
        await db.refresh(task)
        return task
    
    @staticmethod
    async def delete_task(
        db: AsyncSession,
        task_id: int,
        owner_id: Optional[int] = None,
        is_admin: bool = False,
    ) -> bool:
        task = await TaskService.get_task(db, task_id, owner_id, is_admin)
        if not task:
            return False
        await db.delete(task)
        await db.commit()
        return True
