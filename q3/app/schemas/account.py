from pydantic import BaseModel, Field, validator
from decimal import Decimal
from typing import Optional
import uuid

class AccountBase(BaseModel):
    account_number: str = Field(..., min_length=5, max_length=20)
    account_name: str = Field(..., min_length=1, max_length=100)
    currency: str = Field(..., min_length=3, max_length=3)
    
    @validator('currency')
    def validate_currency(cls, v):
        if v not in ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR']:
            raise ValueError('Invalid currency code')
        return v.upper()

class AccountCreate(AccountBase):
    initial_balance: Optional[Decimal] = Field(0, ge=0)

class AccountUpdate(BaseModel):
    account_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None

class AccountInDB(AccountBase):
    id: str
    balance: Decimal
    is_active: bool
    version: int
    created_at: str
    updated_at: str
    
    class Config:
        orm_mode = True

class AccountResponse(AccountInDB):
    pass

class AccountBalance(BaseModel):
    account_id: str
    account_number: str
    balance: Decimal
    currency: str
    
    class Config:
        orm_mode = True 