import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid
from decimal import Decimal

from app.main import app
from app.db.session import get_db
from app.models.base import Base
from app.models.account import Account
from app.models.transaction import Transaction, TransactionType, TransactionStatus

# Create a test database in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in the test database
Base.metadata.create_all(bind=engine)

# Fixture for database session
@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    # Create test data
    account = Account(
        id=str(uuid.uuid4()),
        account_number="TEST123456",
        account_name="Test Account",
        balance=Decimal("1000.00"),
        currency="USD",
        is_active=True,
        version=1
    )
    session.add(account)
    session.commit()
    
    yield session
    
    # Clean up
    transaction.rollback()
    connection.close()

# Fixture for test client with override for dependency
@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Remove override
    app.dependency_overrides.clear()

def test_debit_account(client, db_session):
    # Get account ID
    account = db_session.query(Account).filter_by(account_number="TEST123456").first()
    
    # Make API call to debit account
    response = client.post(
        "/api/v1/transactions/debit",
        json={
            "account_id": account.id,
            "amount": 100.00,
            "currency": "USD",
            "reference": "TEST-DEBIT-001",
            "description": "Test debit transaction"
        }
    )
    
    # Check response status code
    assert response.status_code == 201
    
    # Check transaction was recorded
    response_data = response.json()
    assert response_data["transaction_type"] == "debit"
    assert float(response_data["amount"]) == 100.00
    assert response_data["status"] == "completed"
    
    # Check account balance was updated
    updated_account = db_session.query(Account).filter_by(id=account.id).first()
    assert updated_account.balance == Decimal("900.00")
    assert updated_account.version == 2  # Version should be incremented

def test_insufficient_funds(client, db_session):
    # Get account ID
    account = db_session.query(Account).filter_by(account_number="TEST123456").first()
    
    # Try to debit more than the account balance
    response = client.post(
        "/api/v1/transactions/debit",
        json={
            "account_id": account.id,
            "amount": 2000.00,  # More than the balance
            "currency": "USD",
            "reference": "TEST-DEBIT-002",
            "description": "Test insufficient funds"
        }
    )
    
    # Check that we get a 400 Bad Request
    assert response.status_code == 400
    assert "Insufficient funds" in response.json()["detail"]
    
    # Check account balance was not changed
    unchanged_account = db_session.query(Account).filter_by(id=account.id).first()
    assert unchanged_account.balance == account.balance 