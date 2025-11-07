from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection URL with defaults
DATABASE_URL = (
    f"postgresql://{os.getenv('DB_USER', 'admin')}:{os.getenv('DB_PASSWORD', 'admin123')}@"
    f"{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'construction_db')}"
)

def init_db():
    """Create the database engine, create tables, and return (engine, SessionLocal).

    Returns:
        engine: SQLAlchemy Engine instance
        SessionLocal: sessionmaker factory
    """
    engine = create_engine(DATABASE_URL)
    # Create all tables
    Base.metadata.create_all(engine)
    # Create sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal


# Initialize database and sessionmaker globally
engine, SessionLocal = init_db()


# Dependency for FastAPI
def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    engine, SessionLocal = init_db()
    print("Database initialization complete!")