from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.account import Account
from app.schemas.account import (
    AccountCreate, AccountUpdate, AccountResponse, AccountBalance
)
from app.services.account_service import AccountService

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    account_data: AccountCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new account.
    """
    return AccountService.create_account(db=db, account_data=account_data)

@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: str,
    db: Session = Depends(get_db)
):
    """
    Get account details by ID.
    """
    return AccountService.get_account(db=db, account_id=account_id)

@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: str,
    account_data: AccountUpdate,
    db: Session = Depends(get_db)
):
    """
    Update account details.
    """
    return AccountService.update_account(db=db, account_id=account_id, account_data=account_data)

@router.get("/{account_id}/balance", response_model=AccountBalance)
def get_account_balance(
    account_id: str,
    db: Session = Depends(get_db)
):
    """
    Get account balance.
    """
    return AccountService.get_account_balance(db=db, account_id=account_id) 