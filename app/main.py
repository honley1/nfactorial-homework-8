from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .database import engine, get_db
from .models import Base
from .routers import auth, tasks, frontend, celery_tasks, advanced_tasks

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Task Manager API",
    description="A modern task management application with JWT authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(celery_tasks.router, prefix="/api")
app.include_router(advanced_tasks.router, prefix="/api")

# Include frontend router (no prefix for SSR routes)
app.include_router(frontend.router)

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "message": "Task Manager API is running"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=4000,
        reload=True
    ) 