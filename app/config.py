from decouple import config
import os

# Database
DATABASE_URL = config("DATABASE_URL", default="sqlite:///./test.db")

# JWT Settings
SECRET_KEY = config("SECRET_KEY", default="your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# App Settings
DEBUG = config("DEBUG", default=True, cast=bool) 