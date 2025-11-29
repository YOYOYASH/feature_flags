import os
import io
from dotenv import load_dotenv

load_dotenv()

# --- Your Config class is now much simpler ---
# It will read from the environment variables populated by load_secrets()
class Config:
    # --- General Config ---
    APP_ENV = os.getenv("APP_ENV", "local")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8080))
    PROJECT_ID = os.getenv("PROJECT_ID")

    # --- Database Config ---
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_CONNECTION_STRING = os.getenv("DATABASE_URL")

    # --- Auth & API Keys ---
    SECRET_KEY = os.getenv("SECRET_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # --- Redis ---
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
