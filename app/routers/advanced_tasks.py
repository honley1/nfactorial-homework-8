from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import TaskResponse
from ..auth import get_current_user
from ..models import User
from ..crud import (
    get_tasks_with_filters,
    get_task_statistics,
    bulk_update_tasks,
    bulk_delete_tasks,
    get_tasks_by_date_range,
    duplicate_task,
    get_user_activity_summary
)
from pydantic import BaseModel

router = APIRouter(prefix="/advanced-tasks", tags=["advanced-tasks"])

class BulkTaskUpdate(BaseModel):
    task_ids: List[int]
    completed: Optional[bool] = None
    title: Optional[str] = None
    description: Optional[str] = None

class BulkTaskDelete(BaseModel):
    task_ids: List[int]

class DateRangeQuery(BaseModel):
    start_date: datetime
    end_date: datetime

@router.get("/search", response_model=List[TaskResponse])
def search_tasks(
    search: Optional[str] = Query(None, description="Search in title and description"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    sort_by: str = Query("created_at", description="Sort by field"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of tasks to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Поиск и фильтрация задач с расширенными возможностями
    """
    valid_sort_fields = ["created_at", "updated_at", "title", "completed"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort field. Use: {valid_sort_fields}")
    
    tasks = get_tasks_with_filters(
        db=db,
        user_id=current_user.id,
        completed=completed,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )
    
    return tasks

@router.get("/statistics")
def get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить детальную статистику по задачам
    """
    stats = get_task_statistics(db=db, user_id=current_user.id)
    return stats

@router.put("/bulk-update")
def bulk_update(
    bulk_data: BulkTaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Массовое обновление задач
    """
    if not bulk_data.task_ids:
        raise HTTPException(status_code=400, detail="No task IDs provided")
    
    if len(bulk_data.task_ids) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 tasks allowed per bulk operation")
    
    # Подготовка данных для обновления
    update_data = {}
    if bulk_data.completed is not None:
        update_data["completed"] = bulk_data.completed
        update_data["updated_at"] = datetime.utcnow()
    
    if bulk_data.title is not None:
        update_data["title"] = bulk_data.title
        update_data["updated_at"] = datetime.utcnow()
    
    if bulk_data.description is not None:
        update_data["description"] = bulk_data.description
        update_data["updated_at"] = datetime.utcnow()
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    updated_count = bulk_update_tasks(
        db=db,
        task_ids=bulk_data.task_ids,
        user_id=current_user.id,
        update_data=update_data
    )
    
    return {
        "message": f"Successfully updated {updated_count} tasks",
        "updated_count": updated_count,
        "task_ids": bulk_data.task_ids
    }

@router.delete("/bulk-delete")
def bulk_delete(
    bulk_data: BulkTaskDelete,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Массовое удаление задач
    """
    if not bulk_data.task_ids:
        raise HTTPException(status_code=400, detail="No task IDs provided")
    
    if len(bulk_data.task_ids) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 tasks allowed per bulk operation")
    
    deleted_count = bulk_delete_tasks(
        db=db,
        task_ids=bulk_data.task_ids,
        user_id=current_user.id
    )
    
    return {
        "message": f"Successfully deleted {deleted_count} tasks",
        "deleted_count": deleted_count,
        "task_ids": bulk_data.task_ids
    }

@router.get("/date-range", response_model=List[TaskResponse])
def get_tasks_by_date(
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    end_date: datetime = Query(..., description="End date (ISO format)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить задачи за определенный период времени
    """
    if start_date >= end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    # Ограничим период максимум 1 годом
    if (end_date - start_date).days > 365:
        raise HTTPException(status_code=400, detail="Date range cannot exceed 365 days")
    
    tasks = get_tasks_by_date_range(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    return tasks

@router.post("/duplicate/{task_id}", response_model=TaskResponse)
def duplicate_task_endpoint(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Дублировать существующую задачу
    """
    duplicated_task = duplicate_task(
        db=db,
        task_id=task_id,
        user_id=current_user.id
    )
    
    if not duplicated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return duplicated_task

@router.get("/activity-summary")
def get_activity_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days for activity summary"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить сводку активности пользователя за указанный период
    """
    summary = get_user_activity_summary(
        db=db,
        user_id=current_user.id,
        days=days
    )
    
    return summary

@router.get("/export")
def export_tasks(
    format: str = Query("json", regex="^(json|csv)$", description="Export format: json or csv"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Экспорт задач в различных форматах
    """
    tasks = get_tasks_with_filters(
        db=db,
        user_id=current_user.id,
        completed=completed,
        limit=10000  # Большой лимит для экспорта
    )
    
    if format == "json":
        return {
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
                for task in tasks
            ],
            "total_count": len(tasks),
            "export_date": datetime.utcnow().isoformat(),
            "format": "json"
        }
    
    elif format == "csv":
        # В реальном приложении здесь можно использовать pandas или csv модуль
        csv_data = "id,title,description,completed,created_at,updated_at\n"
        for task in tasks:
            csv_data += f"{task.id},\"{task.title}\",\"{task.description or ''}\",{task.completed},{task.created_at},{task.updated_at}\n"
        
        return {
            "csv_data": csv_data,
            "total_count": len(tasks),
            "export_date": datetime.utcnow().isoformat(),
            "format": "csv"
        }

@router.get("/analytics")
def get_task_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить аналитику по задачам
    """
    # Базовая статистика
    stats = get_task_statistics(db=db, user_id=current_user.id)
    
    # Активность за разные периоды
    activity_7d = get_user_activity_summary(db=db, user_id=current_user.id, days=7)
    activity_30d = get_user_activity_summary(db=db, user_id=current_user.id, days=30)
    
    return {
        "basic_statistics": stats,
        "activity_last_7_days": activity_7d,
        "activity_last_30_days": activity_30d,
        "generated_at": datetime.utcnow().isoformat()
    } 