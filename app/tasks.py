from celery import current_task
from .celery_app import celery_app
from .database import SessionLocal
from .models import Task, User
from datetime import datetime, timedelta
import time
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def send_email_notification(self, user_id: int, task_title: str, notification_type: str):
    """
    Асинхронная отправка email уведомлений
    """
    try:
        # Simulate email sending delay
        for i in range(5):
            time.sleep(1)
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': i + 1, 
                    'total': 5, 
                    'status': f'Sending email notification... {i+1}/5'
                }
            )
        
        # Here you would integrate with actual email service (SendGrid, AWS SES, etc.)
        logger.info(f"Email notification sent to user {user_id} for task '{task_title}'")
        
        return {
            'current': 5,
            'total': 5,
            'status': f'Email notification sent successfully for task: {task_title}',
            'result': f'Notification sent to user {user_id}'
        }
    except Exception as exc:
        logger.error(f"Email notification failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)

@celery_app.task(bind=True)
def process_bulk_tasks(self, user_id: int, tasks_data: list):
    """
    Массовая обработка задач
    """
    try:
        db = SessionLocal()
        processed_tasks = []
        total_tasks = len(tasks_data)
        
        for i, task_data in enumerate(tasks_data):
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': i + 1,
                    'total': total_tasks,
                    'status': f'Processing task {i+1}/{total_tasks}: {task_data.get("title", "Unnamed")}'
                }
            )
            
            # Create task
            new_task = Task(
                title=task_data['title'],
                description=task_data.get('description', ''),
                owner_id=user_id
            )
            db.add(new_task)
            db.commit()
            db.refresh(new_task)
            
            processed_tasks.append({
                'id': new_task.id,
                'title': new_task.title,
                'created_at': new_task.created_at.isoformat()
            })
            
            # Simulate processing time
            time.sleep(0.5)
        
        db.close()
        
        return {
            'current': total_tasks,
            'total': total_tasks,
            'status': 'Bulk task processing completed',
            'result': f'Successfully processed {len(processed_tasks)} tasks',
            'tasks': processed_tasks
        }
        
    except Exception as exc:
        db.close()
        logger.error(f"Bulk task processing failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)

@celery_app.task
def cleanup_old_tasks():
    """
    Очистка старых завершенных задач (старше 30 дней)
    """
    try:
        db = SessionLocal()
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Find old completed tasks
        old_tasks = db.query(Task).filter(
            Task.completed == True,
            Task.updated_at < cutoff_date
        ).all()
        
        deleted_count = len(old_tasks)
        
        # Delete old tasks
        for task in old_tasks:
            db.delete(task)
        
        db.commit()
        db.close()
        
        logger.info(f"Cleaned up {deleted_count} old completed tasks")
        return f"Successfully cleaned up {deleted_count} old tasks"
        
    except Exception as exc:
        db.close()
        logger.error(f"Cleanup task failed: {str(exc)}")
        raise exc

@celery_app.task(bind=True)
def generate_task_report(self, user_id: int):
    """
    Генерация отчета по задачам пользователя
    """
    try:
        db = SessionLocal()
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 1, 'total': 4, 'status': 'Fetching user tasks...'}
        )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        tasks = db.query(Task).filter(Task.owner_id == user_id).all()
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 2, 'total': 4, 'status': 'Analyzing task data...'}
        )
        
        time.sleep(1)  # Simulate processing
        
        # Calculate statistics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.completed])
        pending_tasks = total_tasks - completed_tasks
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 3, 'total': 4, 'status': 'Generating report...'}
        )
        
        time.sleep(1)  # Simulate report generation
        
        report = {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'statistics': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'pending_tasks': pending_tasks,
                'completion_rate': round((completed_tasks / total_tasks * 100), 2) if total_tasks > 0 else 0
            },
            'recent_tasks': [
                {
                    'id': task.id,
                    'title': task.title,
                    'completed': task.completed,
                    'created_at': task.created_at.isoformat()
                }
                for task in sorted(tasks, key=lambda x: x.created_at, reverse=True)[:5]
            ],
            'generated_at': datetime.utcnow().isoformat()
        }
        
        db.close()
        
        # Update progress - completed
        self.update_state(
            state='PROGRESS',
            meta={'current': 4, 'total': 4, 'status': 'Report generated successfully'}
        )
        
        return {
            'current': 4,
            'total': 4,
            'status': 'Task report generated successfully',
            'result': report
        }
        
    except Exception as exc:
        db.close()
        logger.error(f"Report generation failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3) 