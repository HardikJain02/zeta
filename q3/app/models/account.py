from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from app.models.base import Base, TimeStampedModel
import uuid

class Account(Base, TimeStampedModel):
    """Model representing a bank account."""
    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_number = Column(String(20), unique=True, nullable=False, index=True)
    account_name = Column(String(100), nullable=False)
    balance = Column(Numeric(precision=18, scale=2), nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="USD")
    is_active = Column(Boolean, nullable=False, default=True)
    version = Column(Integer, nullable=False, default=1)  # For optimistic locking
    
    # Relationships
    transactions = relationship("Transaction", back_populates="account")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('balance >= 0', name='check_balance_non_negative'),
        Index('idx_account_number_currency', 'account_number', 'currency'),
    )
    
    def __repr__(self):
        return f"<Account(id={self.id}, account_number={self.account_number}, balance={self.balance})>" 