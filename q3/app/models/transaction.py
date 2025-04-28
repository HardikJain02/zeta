from sqlalchemy import Column, String, Numeric, ForeignKey, Enum, Index, Text
from sqlalchemy.orm import relationship
from app.models.base import Base, TimeStampedModel
import enum
import uuid

class TransactionType(str, enum.Enum):
    DEBIT = "debit"
    CREDIT = "credit"

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"

class Transaction(Base, TimeStampedModel):
    """Model representing a financial transaction."""
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(36), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    reference = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    metadata = Column(Text, nullable=True)  # JSON data
    
    # Relationships
    account = relationship("Account", back_populates="transactions")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_transaction_account_id', 'account_id'),
        Index('idx_transaction_status', 'status'),
        Index('idx_transaction_created_at', 'created_at'),
        Index('idx_transaction_reference', 'reference'),
    )
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, account_id={self.account_id}, type={self.transaction_type}, amount={self.amount}, status={self.status})>" 