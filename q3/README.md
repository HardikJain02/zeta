# Zeta Banking API

A scalable RESTful API for processing banking transactions with high consistency, low latency, and resilience to failures.

## Features

- Processes millions of transactions daily
- Supports debit, credit, and balance inquiry operations
- Ensures transaction atomicity
- Handles concurrent requests efficiently
- Provides clear error messages
- Optimized for high performance

## Architecture

- FastAPI for the REST endpoints
- SQLAlchemy with PostgreSQL for data storage
- Transaction isolation levels for concurrency control
- Optimistic locking for consistency
- Connection pooling for performance
- Database-level constraints for data integrity

## Installation

```bash
# Clone the repository. Go to the q3 folder

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

## API Endpoints

- `GET /api/v1/accounts/{account_id}` - Get account details
- `GET /api/v1/accounts/{account_id}/balance` - Get account balance
- `POST /api/v1/transactions/debit` - Debit an account
- `POST /api/v1/transactions/credit` - Credit an account
- `GET /api/v1/transactions/{transaction_id}` - Get transaction details

## Database Schema

The system uses two main tables:
1. `accounts` - Stores account information and balances
2. `transactions` - Logs all transaction operations with status

## Consistency Guarantees

- Transactions are atomic and isolated
- Optimistic locking prevents lost updates
- Database transactions ensure consistency in case of crashes 