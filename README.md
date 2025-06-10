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

### Docker Development

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   - Web Interface: http://localhost:4000

### Production Deployment

1. **Build Docker image**
   ```bash
   docker build -t task-manager .
   ```

2. **Run container**
   ```bash
   docker run -p 4000:4000 -e SECRET_KEY=your-production-secret task-manager
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