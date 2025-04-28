from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate
from fastapi import HTTPException, status
import uuid

class AccountService:
    @staticmethod
    def create_account(db: Session, account_data: AccountCreate):
        """Create a new account with initial balance."""
        db_account = Account(
            id=str(uuid.uuid4()),
            account_number=account_data.account_number,
            account_name=account_data.account_name,
            balance=account_data.initial_balance,
            currency=account_data.currency
        )
        
        try:
            db.add(db_account)
            db.commit()
            db.refresh(db_account)
            return db_account
        except IntegrityError as e:
            db.rollback()
            if "account_number" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Account with this account number already exists"
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create account: {str(e)}"
            )
    
    @staticmethod
    def get_account(db: Session, account_id: str):
        """Get account details by ID."""
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        return account
    
    @staticmethod
    def get_account_by_account_number(db: Session, account_number: str):
        """Get account details by account number."""
        account = db.query(Account).filter(Account.account_number == account_number).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        return account
    
    @staticmethod
    def update_account(db: Session, account_id: str, account_data: AccountUpdate):
        """Update account details."""
        account = AccountService.get_account(db, account_id)
        
        if account_data.account_name is not None:
            account.account_name = account_data.account_name
        
        if account_data.is_active is not None:
            account.is_active = account_data.is_active
        
        account.version += 1  # Increment version for optimistic locking
        
        try:
            db.commit()
            db.refresh(account)
            return account
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update account: {str(e)}"
            )
    
    @staticmethod
    def get_account_balance(db: Session, account_id: str):
        """Get account balance."""
        account = AccountService.get_account(db, account_id)
        return {
            "account_id": account.id,
            "account_number": account.account_number,
            "balance": account.balance,
            "currency": account.currency
        } 