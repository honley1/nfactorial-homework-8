from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from ..models import User
from ..celery_app import celery_app
from ..tasks import send_email_notification, process_bulk_tasks, generate_task_report, cleanup_old_tasks
from pydantic import BaseModel

router = APIRouter(prefix="/celery", tags=["celery-tasks"])

class BulkTaskCreate(BaseModel):
    tasks: List[Dict[str, str]]

class TaskProgress(BaseModel):
    task_id: str
    state: str
    current: int = 0
    total: int = 0
    status: str = ""
    result: Any = None

@router.post("/send-notification")
def trigger_email_notification(
    task_title: str,
    notification_type: str = "task_created",
    current_user: User = Depends(get_current_user)
):
    """
    Запустить асинхронную отправку email уведомления
    """
    task = send_email_notification.delay(
        user_id=current_user.id,
        task_title=task_title,
        notification_type=notification_type
    )
    
    return {
        "message": "Email notification task started",
        "task_id": task.id,
        "status": "PENDING"
    }

@router.post("/bulk-create-tasks")
def create_bulk_tasks(
    bulk_data: BulkTaskCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Массовое создание задач через Celery
    """
    if not bulk_data.tasks:
        raise HTTPException(status_code=400, detail="No tasks provided")
    
    if len(bulk_data.tasks) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 tasks allowed per bulk operation")
    
    # Validate task data
    for task_data in bulk_data.tasks:
        if not task_data.get('title'):
            raise HTTPException(status_code=400, detail="Each task must have a title")
    
    task = process_bulk_tasks.delay(
        user_id=current_user.id,
        tasks_data=bulk_data.tasks
    )
    
    return {
        "message": f"Bulk task creation started for {len(bulk_data.tasks)} tasks",
        "task_id": task.id,
        "status": "PENDING",
        "total_tasks": len(bulk_data.tasks)
    }

@router.post("/generate-report")
def generate_user_report(
    current_user: User = Depends(get_current_user)
):
    """
    Генерация отчета по задачам пользователя
    """
    task = generate_task_report.delay(user_id=current_user.id)
    
    return {
        "message": "Report generation started",
        "task_id": task.id,
        "status": "PENDING"
    }

@router.post("/cleanup-old-tasks")
def trigger_cleanup(
    current_user: User = Depends(get_current_user)
):
    """
    Запустить очистку старых задач (только для администраторов)
    """
    # In a real app, you'd check if user is admin
    task = cleanup_old_tasks.delay()
    
    return {
        "message": "Cleanup task started",
        "task_id": task.id,
        "status": "PENDING"
    }

@router.get("/task-status/{task_id}")
def get_task_status(task_id: str):
    """
    Получить статус выполнения задачи
    """
    try:
        task_result = celery_app.AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'current': 0,
                'total': 1,
                'status': 'Pending...'
            }
        elif task_result.state != 'FAILURE':
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'current': task_result.info.get('current', 0),
                'total': task_result.info.get('total', 1),
                'status': task_result.info.get('status', '')
            }
            if 'result' in task_result.info:
                response['result'] = task_result.info['result']
        else:
            # Something went wrong in the background job
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'current': 1,
                'total': 1,
                'status': 'Task failed',
                'error': str(task_result.info)
            }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@router.get("/active-tasks")
def get_active_tasks():
    """
    Получить список активных задач
    """
    try:
        # Get active tasks from Celery
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        
        if not active_tasks:
            return {"active_tasks": [], "message": "No active tasks"}
        
        formatted_tasks = []
        for worker, tasks in active_tasks.items():
            for task in tasks:
                formatted_tasks.append({
                    "task_id": task["id"],
                    "name": task["name"],
                    "worker": worker,
                    "args": task["args"],
                    "kwargs": task["kwargs"]
                })
        
        return {
            "active_tasks": formatted_tasks,
            "total_active": len(formatted_tasks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch active tasks: {str(e)}")

@router.delete("/cancel-task/{task_id}")
def cancel_task(task_id: str):
    """
    Отменить выполнение задачи
    """
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return {
            "message": f"Task {task_id} has been cancelled",
            "task_id": task_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel task: {str(e)}")

@router.get("/worker-stats")
def get_worker_stats():
    """
    Получить статистику worker'ов
    """
    try:
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        registered = inspect.registered()
        
        if not stats:
            return {"workers": [], "message": "No workers available"}
        
        worker_info = []
        for worker_name, worker_stats in stats.items():
            worker_data = {
                "worker": worker_name,
                "status": "online",
                "pool": worker_stats.get("pool", {}),
                "total_tasks": worker_stats.get("total", {}),
                "registered_tasks": registered.get(worker_name, []) if registered else []
            }
            worker_info.append(worker_data)
        
        return {
            "workers": worker_info,
            "total_workers": len(worker_info)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch worker stats: {str(e)}") 