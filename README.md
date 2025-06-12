# Task Manager - Full Stack CRUD Application

A modern, full-featured task management application built with FastAPI, SQLite, and Server-Side Rendering (SSR). This project demonstrates all levels of backend development from basic CRUD operations to advanced features like JWT authentication, Docker containerization, and CI/CD pipelines.

## 🚀 Features

### 🥉 Basic Level
- ✅ Complete CRUD operations for tasks
- ✅ Server-Side Rendered frontend with modern UI
- ✅ SQLite database integration
- ✅ RESTful API endpoints

### 🥈 Medium Level
- ✅ Docker containerization with Dockerfile
- ✅ SQLite database connection and ORM (SQLAlchemy)
- ✅ CI/CD pipeline with GitHub Actions
- ✅ Automated testing and linting

### 🥇 Hard Level
- ✅ JWT Authentication and Authorization
- ✅ Docker Compose configuration
- ✅ Secured API endpoints:
  - `/api/auth/me` - Get current user info
  - `/api/tasks/create_task` - Create a new task
  - `/api/tasks/get_tasks` - Get all user tasks
  - And more...

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **Frontend**: Server-Side Rendering with Jinja2 templates
- **Styling**: Bootstrap 5 with custom CSS
- **Async Tasks**: Celery with Redis broker
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Testing**: Pytest

## 📋 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info (Protected)

### Tasks
- `POST /api/tasks/create_task` - Create new task (Protected)
- `GET /api/tasks/get_tasks` - Get all user tasks (Protected)
- `GET /api/tasks/{task_id}` - Get specific task (Protected)
- `PUT /api/tasks/{task_id}` - Update task (Protected)
- `DELETE /api/tasks/{task_id}` - Delete task (Protected)

### Advanced Tasks
- `GET /api/advanced-tasks/search` - Advanced search with filters
- `GET /api/advanced-tasks/statistics` - Task statistics
- `PUT /api/advanced-tasks/bulk-update` - Bulk update tasks
- `DELETE /api/advanced-tasks/bulk-delete` - Bulk delete tasks
- `GET /api/advanced-tasks/date-range` - Get tasks by date range
- `POST /api/advanced-tasks/duplicate/{task_id}` - Duplicate task
- `GET /api/advanced-tasks/activity-summary` - User activity summary
- `GET /api/advanced-tasks/export` - Export tasks (JSON/CSV)
- `GET /api/advanced-tasks/analytics` - Task analytics

### Celery Tasks
- `POST /api/celery/send-notification` - Send async email notification
- `POST /api/celery/bulk-create-tasks` - Bulk create tasks async
- `POST /api/celery/generate-report` - Generate user report async
- `POST /api/celery/cleanup-old-tasks` - Cleanup old tasks
- `GET /api/celery/task-status/{task_id}` - Get task status
- `GET /api/celery/active-tasks` - Get active tasks
- `DELETE /api/celery/cancel-task/{task_id}` - Cancel task
- `GET /api/celery/worker-stats` - Worker statistics

### Frontend Routes
- `GET /` - Homepage
- `GET /login` - Login page
- `GET /register` - Registration page
- `GET /dashboard` - User dashboard (Protected)
- `GET /logout` - Logout

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional)
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd crud-back
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the application**
   - Web Interface: http://localhost:4000
   - API Documentation: http://localhost:4000/docs
   - Alternative API Docs: http://localhost:4000/redoc

### Docker Development (with Celery)

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Services running:**
   - **Web Application**: http://localhost:4000
   - **Redis**: localhost:6379
   - **Celery Worker**: Background task processing
   - **Celery Beat**: Scheduled task scheduler

3. **Access the application**
   - Web Interface: http://localhost:4000

### Local Development with Celery

1. **Start Redis** (required for Celery)
   ```bash
   # Using Docker
   docker run -d -p 6379:6379 redis:7-alpine
   
   # Or install Redis locally
   # macOS: brew install redis && brew services start redis
   # Ubuntu: sudo apt install redis-server && sudo systemctl start redis
   ```

2. **Start FastAPI application**
   ```bash
   uvicorn app.main:app --reload --port 4000
   ```

3. **Start Celery Worker** (in new terminal)
   ```bash
   chmod +x start_celery.sh
   ./start_celery.sh
   
   # Or directly:
   celery -A app.celery_app worker --loglevel=info
   ```

4. **Start Celery Beat** (optional, for scheduled tasks)
   ```bash
   chmod +x start_beat.sh
   ./start_beat.sh
   
   # Or directly:
   celery -A app.celery_app beat --loglevel=info
   ```

## 🔴 Redis Configuration & Monitoring

### Redis Setup
Redis is pre-configured in the Docker Compose setup. Configuration file: `redis.conf`

### Redis Commands
```bash
# Connect to Redis (Docker)
docker exec -it task-manager-redis redis-cli

# Connect to Redis (local)
redis-cli -h localhost -p 6379

# Basic Redis operations
INFO                     # Server information
KEYS *                   # All keys (use carefully!)
FLUSHALL                 # Clear all data
```

### Celery Queue Monitoring
```bash
# Check queue lengths
LLEN celery              # Main Celery queue
LLEN email               # Email queue
LLEN reports             # Reports queue
LLEN cleanup             # Cleanup queue

# View queue contents
LRANGE celery 0 -1       # All items in celery queue

# View Celery task results
KEYS celery-task-meta-*  # All task metadata
```

### Redis Monitor Tool
```bash
# Run the custom Redis monitor
python redis_monitor.py

# Or use built-in Redis monitor
redis-cli MONITOR

# Performance monitoring
redis-cli --latency
```

### Production Deployment

#### 🚀 Автоматический деплой на сервер

1. **Первоначальная настройка сервера**
   ```bash
   # На новом сервере Ubuntu
   sudo ./server-setup.sh
   ```

2. **Подготовка проекта**
   ```bash
   # Копируйте env.production.example в .env
   cp env.production.example .env
   
   # Отредактируйте .env файл
   nano .env
   ```

3. **Деплой приложения**
   ```bash
   # Полный деплой
   sudo ./deploy.sh deploy
   
   # Или поэтапно:
   sudo ./deploy.sh install  # Только установка зависимостей
   sudo ./deploy.sh deploy   # Развертывание
   ```

#### 🔧 Ручной деплой

1. **Подготовка сервера**
   ```bash
   # Обновление системы
   sudo apt update && sudo apt upgrade -y
   
   # Установка Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Установка Docker Compose
   sudo apt install docker-compose-plugin
   ```

2. **Клонирование проекта**
   ```bash
   git clone <your-repo-url> /opt/task-manager
   cd /opt/task-manager
   ```

3. **Настройка переменных окружения**
   ```bash
   cp env.production.example .env
   # Отредактируйте .env файл со своими настройками
   ```

4. **Деплой с Docker Compose**
   ```bash
   # Production сборка
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

#### 🔒 SSL сертификаты (Let's Encrypt)

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d yourdomain.com

# Автоматическое обновление
sudo crontab -e
# Добавьте: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🧪 Testing

Run the test suite:
```bash
pytest -v
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## 🔧 Development

### Code Quality
The project includes automated code quality checks:

```bash
# Linting
flake8 app

# Code formatting
black app

# Import sorting
isort app
```

### Database Migrations
The application automatically creates database tables on startup. For production, consider using Alembic for proper migrations.

## 🏗️ Project Structure

```
crud-back/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication utilities
│   ├── crud.py              # Database operations
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication routes
│   │   ├── tasks.py         # Task routes
│   │   └── frontend.py      # SSR routes
│   └── templates/
│       ├── base.html        # Base template
│       ├── index.html       # Homepage
│       ├── login.html       # Login page
│       ├── register.html    # Registration page
│       └── dashboard.html   # Dashboard
├── tests/
│   ├── __init__.py
│   └── test_main.py         # Test suite
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # GitHub Actions
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose
├── requirements.txt         # Python dependencies
├── env.example              # Environment variables example
└── README.md               # This file
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for secure password storage
- **CORS Protection**: Configurable CORS middleware
- **Input Validation**: Pydantic schemas for request validation
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **XSS Protection**: Template escaping in Jinja2

## 🌟 Key Features Explained

### Server-Side Rendering (SSR)
The application uses Jinja2 templates for server-side rendering, providing:
- Fast initial page loads
- SEO-friendly content
- Progressive enhancement with JavaScript
- Responsive design with Bootstrap 5

### JWT Authentication
Secure authentication system with:
- Access token generation
- Token validation middleware
- Protected routes
- Cookie-based session management for web interface

### Modern UI/UX
- Gradient backgrounds and modern design
- Responsive layout for all devices
- Interactive task management
- Real-time filtering and updates
- Smooth animations and transitions

## 📈 CI/CD Pipeline

The GitHub Actions workflow includes:
- **Testing**: Automated test execution
- **Linting**: Code quality checks
- **Building**: Docker image creation
- **Security**: Dependency vulnerability scanning
- **Deployment**: Automated deployment (configurable)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for robust ORM capabilities
- Bootstrap for responsive UI components
- The Python community for amazing tools and libraries

---

**Happy Coding! 🚀** 