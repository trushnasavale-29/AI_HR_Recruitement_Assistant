import os
from dotenv import load_dotenv

load_dotenv()

# Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Database URL (Defaults to local SQLite if not set)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./resume.db")

# Render / Neon compatibility fix for SQLAlchemy
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)