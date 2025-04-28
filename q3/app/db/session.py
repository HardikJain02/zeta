from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create engine with connection pooling for high performance
engine = create_engine(
    settings.DATABASE_URI,
    pool_size=settings.DB_POOL_SIZE,  # Maximum number of connections in the pool
    max_overflow=settings.DB_MAX_OVERFLOW,  # Maximum overflow connections when pool is full
    pool_timeout=settings.DB_POOL_TIMEOUT,  # Timeout for getting a connection from pool
    pool_recycle=settings.DB_POOL_RECYCLE,  # Recycle connections after this many seconds
    pool_pre_ping=True,  # Test connections before using them (prevents stale connections)
    isolation_level="REPEATABLE READ"  # Set isolation level for transactions
)

# Create a sessionmaker with the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 