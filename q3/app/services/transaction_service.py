from sqlalchemy.orm import Session
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
from decimal import Decimal
from tenacity import retry, stop_after_attempt, retry_if_exception_type, wait_exponential

from app.models.account import Account
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.schemas.transaction import DebitCreate, CreditCreate
from app.core.config import settings
import uuid
import json
import logging

logger = logging.getLogger(__name__)

class TransactionService:
    @staticmethod
    def _record_transaction(
        db: Session,
        transaction_type: TransactionType,
        account_id: str,
        amount: Decimal,
        currency: str,
        reference: str = None,
        description: str = None,
        metadata: dict = None
    ) -> Transaction:
        """Create a transaction record with initial PENDING status."""
        transaction = Transaction(
            id=str(uuid.uuid4()),
            account_id=account_id,
            transaction_type=transaction_type,
            amount=amount,
            currency=currency,
            status=TransactionStatus.PENDING,
            reference=reference,
            description=description,
            metadata=json.dumps(metadata) if metadata else None
        )
        
        db.add(transaction)
        return transaction
    
    @staticmethod
    def _update_transaction_status(
        db: Session,
        transaction_id: str,
        status: TransactionStatus,
        commit: bool = True
    ) -> Transaction:
        """Update transaction status."""
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).with_for_update().first()
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction {transaction_id} not found"
            )
            
        transaction.status = status
        
        if commit:
            db.commit()
            db.refresh(transaction)
            
        return transaction
    
    @staticmethod
    @retry(
        stop=stop_after_attempt(settings.MAX_TRANSACTION_RETRIES),
        retry=retry_if_exception_type(SQLAlchemyError),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    def debit_account(db: Session, debit_data: DebitCreate) -> Transaction:
        """
        Debit an account (withdraw money).
        
        This method:
        1. Locks the account for updates
        2. Checks if the account has sufficient balance
        3. Records the transaction
        4. Updates the account balance
        5. Updates the transaction status
        
        Uses optimistic locking with version field to prevent lost updates.
        """
        try:
            # Start a transaction and lock the account
            account = db.query(Account).filter(Account.id == debit_data.account_id).with_for_update().first()
            
            if not account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Account not found"
                )
            
            if not account.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Account is inactive"
                )
                
            if account.currency != debit_data.currency:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Currency mismatch. Account currency is {account.currency}, transaction currency is {debit_data.currency}"
                )
            
            # Check if account has enough balance
            if account.balance < debit_data.amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient funds"
                )
            
            # Record the transaction with PENDING status
            transaction = TransactionService._record_transaction(
                db=db,
                transaction_type=TransactionType.DEBIT,
                account_id=account.id,
                amount=debit_data.amount,
                currency=account.currency,
                reference=debit_data.reference,
                description=debit_data.description,
                metadata=debit_data.metadata
            )
            
            # Update account balance
            old_version = account.version
            account.balance -= debit_data.amount
            account.version += 1  # Increment version for optimistic concurrency control
            
            # Update the transaction status to COMPLETED
            transaction.status = TransactionStatus.COMPLETED
            
            # Commit the transaction
            db.commit()
            db.refresh(transaction)
            
            return transaction
            
        except HTTPException:
            # Re-raise HTTP exceptions
            db.rollback()
            raise
        except SQLAlchemyError as e:
            # Handle database errors
            db.rollback()
            logger.error(f"Database error during debit operation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process transaction due to database error"
            )
    
    @staticmethod
    @retry(
        stop=stop_after_attempt(settings.MAX_TRANSACTION_RETRIES),
        retry=retry_if_exception_type(SQLAlchemyError),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    def credit_account(db: Session, credit_data: CreditCreate) -> Transaction:
        """
        Credit an account (deposit money).
        
        This method:
        1. Locks the account for updates
        2. Records the transaction
        3. Updates the account balance
        4. Updates the transaction status
        
        Uses optimistic locking with version field to prevent lost updates.
        """
        try:
            # Start a transaction and lock the account
            account = db.query(Account).filter(Account.id == credit_data.account_id).with_for_update().first()
            
            if not account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Account not found"
                )
            
            if not account.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Account is inactive"
                )
                
            if account.currency != credit_data.currency:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Currency mismatch. Account currency is {account.currency}, transaction currency is {credit_data.currency}"
                )
            
            # Record the transaction with PENDING status
            transaction = TransactionService._record_transaction(
                db=db,
                transaction_type=TransactionType.CREDIT,
                account_id=account.id,
                amount=credit_data.amount,
                currency=account.currency,
                reference=credit_data.reference,
                description=credit_data.description,
                metadata=credit_data.metadata
            )
            
            # Update account balance
            old_version = account.version
            account.balance += credit_data.amount
            account.version += 1  # Increment version for optimistic concurrency control
            
            # Update the transaction status to COMPLETED
            transaction.status = TransactionStatus.COMPLETED
            
            # Commit the transaction
            db.commit()
            db.refresh(transaction)
            
            return transaction
            
        except HTTPException:
            # Re-raise HTTP exceptions
            db.rollback()
            raise
        except SQLAlchemyError as e:
            # Handle database errors
            db.rollback()
            logger.error(f"Database error during credit operation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process transaction due to database error"
            )
    
    @staticmethod
    def get_transaction(db: Session, transaction_id: str) -> Transaction:
        """Get transaction details by ID."""
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        return transaction 