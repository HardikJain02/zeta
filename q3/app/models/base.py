from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, func
from datetime import datetime

Base = declarative_base()

class TimeStampedModel:
    """Base model class that includes created_at and updated_at columns."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False) 