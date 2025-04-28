from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.transaction import Transaction
from app.schemas.transaction import (
    DebitCreate, CreditCreate, TransactionResponse
)
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/debit", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def debit_account(
    debit_data: DebitCreate,
    db: Session = Depends(get_db)
):
    """
    Debit an account (withdraw money).
    
    - Ensures atomicity (transaction cannot be partially completed)
    - Handles concurrency using database locks
    - Returns a descriptive error in case of failure
    """
    return TransactionService.debit_account(db=db, debit_data=debit_data)

@router.post("/credit", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def credit_account(
    credit_data: CreditCreate,
    db: Session = Depends(get_db)
):
    """
    Credit an account (deposit money).
    
    - Ensures atomicity (transaction cannot be partially completed)
    - Handles concurrency using database locks
    - Returns a descriptive error in case of failure
    """
    return TransactionService.credit_account(db=db, credit_data=credit_data)

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """
    Get transaction details by ID.
    """
    return TransactionService.get_transaction(db=db, transaction_id=transaction_id) 