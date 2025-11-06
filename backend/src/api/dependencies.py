"""
API Dependencies
Common dependencies for API endpoints
"""
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

# Prefer pg8000, fallback to psycopg2
try:
    import pg8000
    DB_DRIVER = 'pg8000'
except Exception:
    try:
        import psycopg2
        DB_DRIVER = 'psycopg2'
    except Exception:
        DB_DRIVER = None


def get_db_connection():
    """Get database connection using available driver"""
    if DB_DRIVER == 'pg8000':
        return pg8000.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME')
        )
    elif DB_DRIVER == 'psycopg2':
        return psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', 5432),
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
    else:
        raise RuntimeError('No DB driver available')
