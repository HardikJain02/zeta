from pydantic import BaseModel, Field, validator
from decimal import Decimal
from typing import Optional, Dict, Any
from app.models.transaction import TransactionType, TransactionStatus

class TransactionBase(BaseModel):
    account_id: str
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    reference: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('currency')
    def validate_currency(cls, v):
        if v not in ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR']:
            raise ValueError('Invalid currency code')
        return v.upper()

class DebitCreate(TransactionBase):
    transaction_type: TransactionType = TransactionType.DEBIT

class CreditCreate(TransactionBase):
    transaction_type: TransactionType = TransactionType.CREDIT

class TransactionInDB(TransactionBase):
    id: str
    transaction_type: TransactionType
    status: TransactionStatus
    created_at: str
    updated_at: str
    
    class Config:
        orm_mode = True

class TransactionResponse(TransactionInDB):
    pass

class TransactionUpdate(BaseModel):
    status: TransactionStatus

# For bulk operations
class BulkTransactionCreate(BaseModel):
    transactions: list[TransactionBase]

# For error responses
class TransactionError(BaseModel):
    error_code: str
    error_message: str
    transaction_id: Optional[str] = None 