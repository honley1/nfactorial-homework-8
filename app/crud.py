from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from .models import User, Task
from .schemas import UserCreate, TaskCreate, TaskUpdate
from .auth import get_password_hash

# User CRUD
def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

# Task CRUD
def get_task(db: Session, task_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
    return db.query(Task).filter(Task.owner_id == user_id).offset(skip).limit(limit).all()

def create_task(db: Session, task: TaskCreate, user_id: int) -> Task:
    db_task = Task(**task.dict(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_update: TaskUpdate, user_id: int) -> Optional[Task]:
    db_task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user_id).first()
    if db_task:
        for key, value in task_update.dict(exclude_unset=True).items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int, user_id: int) -> bool:
    db_task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False

# Расширенные CRUD операции

def get_tasks_with_filters(
    db: Session, 
    user_id: int,
    completed: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    skip: int = 0,
    limit: int = 100
) -> List[Task]:
    """
    Получить задачи с фильтрацией, поиском и сортировкой
    """
    query = db.query(Task).filter(Task.owner_id == user_id)
    
    # Фильтр по статусу
    if completed is not None:
        query = query.filter(Task.completed == completed)
    
    # Поиск по заголовку и описанию
    if search:
        search_filter = or_(
            Task.title.ilike(f"%{search}%"),
            Task.description.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Сортировка
    if sort_order.lower() == "desc":
        query = query.order_by(desc(getattr(Task, sort_by)))
    else:
        query = query.order_by(asc(getattr(Task, sort_by)))
    
    return query.offset(skip).limit(limit).all()

def get_task_statistics(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Получить статистику по задачам пользователя
    """
    total_tasks = db.query(Task).filter(Task.owner_id == user_id).count()
    completed_tasks = db.query(Task).filter(
        and_(Task.owner_id == user_id, Task.completed == True)
    ).count()
    pending_tasks = total_tasks - completed_tasks
    
    # Задачи за последнюю неделю
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_tasks = db.query(Task).filter(
        and_(Task.owner_id == user_id, Task.created_at >= week_ago)
    ).count()
    
    # Задачи по дням недели
    tasks_by_day = db.query(
        func.date(Task.created_at).label('date'),
        func.count(Task.id).label('count')
    ).filter(
        and_(Task.owner_id == user_id, Task.created_at >= week_ago)
    ).group_by(func.date(Task.created_at)).all()
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "completion_rate": round((completed_tasks / total_tasks * 100), 2) if total_tasks > 0 else 0,
        "recent_tasks_week": recent_tasks,
        "tasks_by_day": [{"date": str(day.date), "count": day.count} for day in tasks_by_day]
    }

def bulk_update_tasks(db: Session, task_ids: List[int], user_id: int, update_data: Dict[str, Any]) -> int:
    """
    Массовое обновление задач
    """
    updated_count = db.query(Task).filter(
        and_(Task.id.in_(task_ids), Task.owner_id == user_id)
    ).update(update_data, synchronize_session=False)
    
    db.commit()
    return updated_count

def bulk_delete_tasks(db: Session, task_ids: List[int], user_id: int) -> int:
    """
    Массовое удаление задач
    """
    deleted_count = db.query(Task).filter(
        and_(Task.id.in_(task_ids), Task.owner_id == user_id)
    ).delete(synchronize_session=False)
    
    db.commit()
    return deleted_count

def get_tasks_by_date_range(
    db: Session, 
    user_id: int, 
    start_date: datetime, 
    end_date: datetime
) -> List[Task]:
    """
    Получить задачи за определенный период
    """
    return db.query(Task).filter(
        and_(
            Task.owner_id == user_id,
            Task.created_at >= start_date,
            Task.created_at <= end_date
        )
    ).order_by(desc(Task.created_at)).all()

def mark_overdue_tasks(db: Session, user_id: int) -> int:
    """
    Пометить просроченные задачи (если добавите поле due_date)
    Пока что просто пример функции
    """
    # В будущем можно добавить поле due_date в модель Task
    # overdue_count = db.query(Task).filter(
    #     and_(
    #         Task.owner_id == user_id,
    #         Task.due_date < datetime.utcnow(),
    #         Task.completed == False
    #     )
    # ).update({"is_overdue": True})
    
    return 0  # Placeholder

def duplicate_task(db: Session, task_id: int, user_id: int) -> Optional[Task]:
    """
    Дублировать задачу
    """
    original_task = db.query(Task).filter(
        and_(Task.id == task_id, Task.owner_id == user_id)
    ).first()
    
    if not original_task:
        return None
    
    new_task = Task(
        title=f"Copy of {original_task.title}",
        description=original_task.description,
        owner_id=user_id,
        completed=False
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return new_task

def get_user_activity_summary(db: Session, user_id: int, days: int = 30) -> Dict[str, Any]:
    """
    Получить сводку активности пользователя
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Общая статистика
    total_tasks = db.query(Task).filter(Task.owner_id == user_id).count()
    tasks_period = db.query(Task).filter(
        and_(Task.owner_id == user_id, Task.created_at >= start_date)
    ).count()
    
    completed_period = db.query(Task).filter(
        and_(
            Task.owner_id == user_id,
            Task.completed == True,
            Task.updated_at >= start_date
        )
    ).count()
    
    # Самые длинные заголовки задач
    longest_titles = db.query(Task).filter(Task.owner_id == user_id).order_by(
        desc(func.length(Task.title))
    ).limit(5).all()
    
    return {
        "period_days": days,
        "total_tasks_all_time": total_tasks,
        "tasks_created_period": tasks_period,
        "tasks_completed_period": completed_period,
        "avg_tasks_per_day": round(tasks_period / days, 2),
        "longest_task_titles": [
            {"title": task.title, "length": len(task.title)} 
            for task in longest_titles
        ]
    } 